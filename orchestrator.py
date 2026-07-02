"""
LAMP Orchestrator
=================
The top-level Planner → Builder → Verifier loop for the LAMP multi-agent
automated theorem prover (as described in the paper).

Pipeline
--------
1. Load CoW library source context for the theorem's imports.
2. Locate the `sorry` region that needs to be replaced.
3. Outer loop  (up to max_replans):   PlannerAgent generates a strategy.
4. Inner loop  (up to max_build_attempts): BuilderAgent implements the plan
   and the Lean REPL verifies the result. On success, return the proof.
   On failure, feed error back to the Builder; on exhaustion, re-plan.

Environment variables  (set in .env):
  PROVER_BACKEND   — CLAUDE | KIMI | DEEPSEEK  (default: CLAUDE)
  PROVER_MODE      — cow | normal              (default: cow)
"""

import os
import re
from typing import Optional, Tuple

from planner import PlannerAgent
from builder import BuilderAgent
from verifier import verify_lean4_file, parse_lean_result

# ── CoW library context loader ──────────────────────────────────────────────
# Maps 'import CoW.X' statements in the proof file to actual .lean source,
# which is injected into Planner and Builder prompts for grounding.

_COW_BASE_PATH = os.path.join(os.path.dirname(__file__), "CoW", "CoW")


def _extract_imports(lean_code: str):
    return re.findall(r"^import\s+([\w.]+)", lean_code, re.MULTILINE)


def _load_context_for_proof(lean_code: str) -> str:
    """Read CoW .lean source files referenced by the proof's imports."""
    imports = _extract_imports(lean_code)
    parts = []
    seen = set()
    for imp in imports:
        if not imp.startswith("CoW."):
            continue
        sub = imp[len("CoW."):].replace(".", "/")
        path = os.path.join(_COW_BASE_PATH, sub + ".lean")
        if path in seen or not os.path.exists(path):
            continue
        seen.add(path)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        if src:
            parts.append(f"-- Source: {path} (from `import {imp}`)\n{src}")
    if not parts:
        return ""
    sep = "\n" + "=" * 60 + "\n"
    return "\n" + sep + sep.join(parts) + "\n" + "=" * 60


# ── Sorry locator ────────────────────────────────────────────────────────────

def _locate_sorry(lean_code: str, theorem_name: Optional[str]) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """
    Return (start_line, end_line, original_region) for the proof block
    containing `sorry` in the given theorem, or None if not found.

    The locator looks for the tactic block of the target theorem.
    On failure it falls back to the raw line(s) containing 'sorry'.
    """
    lines = lean_code.split("\n")

    # Try to find theorem declaration and its proof body
    if theorem_name:
        decl_re = re.compile(
            r"^\s*(?:theorem|lemma|def)\s+" + re.escape(theorem_name) + r"\b"
        )
        for i, line in enumerate(lines):
            if decl_re.match(line):
                # Find ':= by' — start of tactic block
                for j in range(i, min(i + 20, len(lines))):
                    if ":= by" in lines[j] or ":=" in lines[j]:
                        start = j + 1
                        # Scan forward for 'sorry'
                        for k in range(start, len(lines)):
                            if "sorry" in lines[k]:
                                region = "\n".join(lines[start : k + 1])
                                return start + 1, k + 1, region
                        break

    # Fallback: grab the first line containing 'sorry'
    sorry_start = sorry_end = None
    for i, line in enumerate(lines):
        if "sorry" in line:
            if sorry_start is None:
                sorry_start = i + 1  # 1-indexed
            sorry_end = i + 1
    if sorry_start is not None:
        region = "\n".join(lines[sorry_start - 1 : sorry_end])
        return sorry_start, sorry_end, region
    return None, None, None


# ── Definition failure heuristic ─────────────────────────────────────────────

_DEFINITION_FAILURE_KEYWORDS = [
    "not available", "don't exist", "doesn't exist", "can't find",
    "cannot find", "not defined", "not imported", "don't have access",
    "no definition", "not present", "missing definition", "not in scope",
]


def _is_definition_failure(reasoning: str) -> bool:
    if not reasoning:
        return False
    lower = reasoning.lower()
    return any(kw in lower for kw in _DEFINITION_FAILURE_KEYWORDS)


# ── Orchestrator ─────────────────────────────────────────────────────────────

class LAMPOrchestrator:
    """
    Multi-Agent Orchestrator for LAMP.

    Manages the Planner → Builder → Verifier loop with CoW library grounding.
    The Builder has access to MCP tools (get_cow_definition, search_lean_explore,
    get_lean_goal_state) for on-demand lookup.

    Parameters
    ----------
    max_replans : int
        Maximum number of times the Planner is allowed to revise its strategy.
    max_build_attempts : int
        Maximum Builder attempts per plan before triggering a re-plan.
    lean_workspace : str
        Path to the Lean project used for REPL verification (must contain
        a built REPL binary via `lake build`).
    """

    def __init__(
        self,
        max_replans: int = 3,
        max_build_attempts: int = 3,
        lean_workspace: str = "CoW/",
    ):
        self.planner = PlannerAgent()
        self.builder = BuilderAgent()
        self.max_replans = max_replans
        self.max_build_attempts = max_build_attempts
        self.lean_workspace = lean_workspace

    def run(self, theorem_name: str, initial_proof: str) -> str:
        """
        Run the full LAMP pipeline on a theorem with a `sorry` placeholder.

        Parameters
        ----------
        theorem_name : str
            The Lean 4 name of the theorem to prove (used for sorry location).
        initial_proof : str
            The complete Lean 4 file with `sorry` as the proof body.

        Returns
        -------
        str
            The updated Lean 4 file.  If successful, the `sorry` is replaced
            with a verified proof.  If all attempts fail, the best partial
            attempt is returned with the original `sorry` intact.
        """
        print(f"\n[Orchestrator] Starting LAMP pipeline for: {theorem_name}")

        current_proof = initial_proof
        mode = os.getenv("PROVER_MODE", "cow").lower().strip()

        # ── Step 1: Load CoW library source as context ────────────────────
        lean_context = ""
        if mode == "cow":
            lean_context = _load_context_for_proof(initial_proof)
            if lean_context:
                print(f"[Orchestrator] CoW context loaded ({len(lean_context)} chars).")
            else:
                print("[Orchestrator] Warning: no CoW context found.")

        # ── Step 2: Locate the sorry region ──────────────────────────────
        start_line, end_line, original_region = _locate_sorry(
            current_proof, theorem_name
        )
        if start_line is None:
            print("[Orchestrator] Error: no 'sorry' found — nothing to prove.")
            return current_proof

        print(f"[Orchestrator] Targeting sorry at lines {start_line}–{end_line}.")

        builder_feedback = None
        last_failed_attempt = None

        # ── Outer loop: re-planning ───────────────────────────────────────
        for replan_idx in range(self.max_replans):
            print(f"\n{'=' * 55}")
            print(f"--- Planning Phase (iteration {replan_idx + 1}/{self.max_replans}) ---")

            reasoning, plan = self.planner.generate_plan(
                theorem_goal=current_proof,
                builder_feedback=builder_feedback,
                lean_context=lean_context,
            )
            print(f"\n[Planner] Reasoning:\n{reasoning}\n")
            print(f"[Planner] Plan:\n{plan}\n")

            self.builder.clear_memory(keep_last_failed=last_failed_attempt)
            plan_succeeded = False
            context_retry_used = False

            # ── Inner loop: building ──────────────────────────────────────
            for build_idx in range(self.max_build_attempts):
                print(f"\n--- Builder Attempt {build_idx + 1}/{self.max_build_attempts} ---")

                # Verify current state
                raw = verify_lean4_file(
                    current_proof, timeout=30, lean_workspace=self.lean_workspace
                )
                result = parse_lean_result(raw)
                proof_done = result.passed and "sorry" not in current_proof

                if proof_done:
                    print("[Orchestrator] ✅ Proof verified!")
                    return current_proof

                # Build feedback string for the Builder
                feedback_lines = []
                for err in result.errors:
                    feedback_lines.append(
                        f"Error at line {err.source_position.line}: {err.message}"
                    )
                for goal in result.goals:
                    feedback_lines.append(f"Unsolved goal: {goal.target}")
                if not feedback_lines and "sorry" in current_proof:
                    feedback_lines += [
                        "The proof still contains 'sorry'.",
                        "Call 'get_lean_goal_state' to see the exact goal state.",
                    ]
                verifier_feedback = "\n".join(feedback_lines)

                # Tell the toolbox what the current proof is (for LSP goal query)
                self.builder.toolbox.set_current_proof(current_proof)

                # Builder generates a patch
                patch, failure_reasoning = self.builder.generate_repair(
                    plan=plan,
                    verifier_feedback=verifier_feedback,
                    original_region=original_region,
                    theorem_name=theorem_name,
                    start_line=start_line,
                    end_line=end_line,
                    lean_context=lean_context,
                    reasoning=reasoning,
                )

                if failure_reasoning:
                    print(f"[Builder] ⚠️  Plan unworkable: {failure_reasoning}")
                    # Context starvation? Retry with re-injected context (no re-plan)
                    if _is_definition_failure(failure_reasoning) and not context_retry_used:
                        print("[Orchestrator] 🔄 Context failure detected — retrying.")
                        learned = self.builder.get_learned_definitions()
                        if learned:
                            lean_context += f"\n\n-- Discovered from tools --\n{learned}"
                        self.builder.clear_memory()
                        context_retry_used = True
                        continue
                    builder_feedback = failure_reasoning
                    last_failed_attempt = {
                        "proof": original_region,
                        "error": failure_reasoning,
                    }
                    break  # exit build loop → re-plan

                # Apply the patch
                print(f"[Orchestrator] Applying patch:\n```lean4\n{patch.replacement_region}\n```")
                lines = current_proof.split("\n")
                new_proof = "\n".join(
                    lines[: start_line - 1]
                    + [patch.replacement_region]
                    + lines[end_line:]
                )
                current_proof = new_proof
                original_region = patch.replacement_region
                end_line = start_line + len(patch.replacement_region.split("\n")) - 1

                # Verify the patch immediately
                raw2 = verify_lean4_file(
                    current_proof, timeout=30, lean_workspace=self.lean_workspace
                )
                result2 = parse_lean_result(raw2)
                if result2.passed and "sorry" not in current_proof:
                    print("[Orchestrator] ✅ Proof verified after patch!")
                    return current_proof

                # Update last_failed_attempt for the next potential re-plan
                fb2 = []
                for err in result2.errors:
                    fb2.append(f"Error at line {err.source_position.line}: {err.message}")
                for goal in result2.goals:
                    fb2.append(f"Unsolved goal: {goal.target}")
                last_failed_attempt = {
                    "proof": original_region,
                    "error": "\n".join(fb2),
                }

            if not builder_feedback:
                builder_feedback = (
                    f"Builder failed after {self.max_build_attempts} attempts. "
                    "The plan may be using incorrect tactic names or missing a key lemma."
                )

        print("\n[Orchestrator] ❌ Max re-plans reached. Returning best attempt.")
        return current_proof
