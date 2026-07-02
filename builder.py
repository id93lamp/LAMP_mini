"""
Builder Agent
=============
The Builder is the code-generation component of the LAMP pipeline.

Given a strategic plan from the Planner, the Builder:
  1. Reads the CoW library source context (injected in the first prompt).
  2. Optionally calls MCP tools (get_cow_definition, search_lean_explore,
     get_lean_goal_state) for on-demand lookup.
  3. Outputs the Lean 4 tactic proof body that replaces the `sorry`.
  4. If the plan is mathematically impossible, outputs a <reasoning> block
     explaining why, which triggers a Planner re-plan.

The Builder maintains conversation history across multiple fix attempts
within a single planning cycle (persistent repair loop).

Environment variables (set in .env):
  PROVER_BACKEND — CLAUDE | KIMI | DEEPSEEK  (default: CLAUDE)
  PROVER_MODE    — cow | normal              (default: cow)
"""

import re
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from mcp_tools import SemanticToolBox


# ── ProofPatch dataclass ──────────────────────────────────────────────────────

@dataclass
class ProofPatch:
    """Represents a proof region replacement."""
    original_region: str
    replacement_region: str
    theorem_name: Optional[str]
    start_line: int   # 1-indexed
    end_line: int     # 1-indexed
    patch_reason: str


# ── Builder Agent ─────────────────────────────────────────────────────────────

class BuilderAgent:
    """
    Code-generation agent.

    Implements the mathematical plan from the Planner as Lean 4 tactic code.
    Maintains conversation history so it can iteratively fix verifier errors
    without losing context.
    """

    def __init__(self):
        self.toolbox = SemanticToolBox()
        self.history = []
        self.last_failed_attempt = None

        mode = os.getenv("PROVER_MODE", "cow").lower().strip()

        if mode == "normal":
            self.system_prompt = (
                "You are an expert Lean 4 developer implementing a mathematical plan to prove a theorem.\n"
                "Follow this strict hierarchy:\n"
                "  1. Use the `get_lean_goal_state` tool to retrieve the exact tactic goal state at the current 'sorry' position.\n"
                "  2. If you need to search for a specific Mathlib lemma name you have forgotten, use `search_lean_explore`.\n"
                "  3. Output the exact Lean 4 proof body enclosed in ```lean4 ... ```. Do NOT output imports or theorem signatures.\n"
                "  4. If, and ONLY IF, the plan itself is mathematically impossible, "
                "output a <reasoning> block explaining precisely why.\n"
                "CRITICAL: Do NOT use the `sorry` tactic or placeholder under any circumstances in your final proof code.\n"
                "Note: If a previous proof attempt and its verifier errors are provided, try to reuse, repair, or adapt that code "
                "wherever possible to maintain progress, unless the new mathematical plan requires a completely different approach.\n\n"
                "OUTPUT FORMAT:\n"
                "- Output ONLY the tactic proof body that replaces the `sorry`\n"
                "- No imports, no namespace declarations, no variable declarations\n"
                "- The proof will be inserted directly into an existing file\n\n"
                "LEAN 4 SYNTAX RULES:\n"
                "- This is Lean 4, not Lean 3. Key differences:\n"
                "  · No begin...end blocks. Use `by` followed by indented tactics\n"
                "  · Subgoals use · bullets or { } blocks, not comma-separated lists\n"
                "  · Tactic names may differ from Lean 3 (e.g. contrapose not contraposition)\n"
                "  · When unsure of a tactic name, prefer exact with a Mathlib lemma\n\n"
                "TOOL USE RULES:\n"
                "- Tool calls are separate from proof output\n"
                "- Never write tool call syntax inside a lean code block\n"
                "- Lean code blocks contain ONLY valid Lean 4 tactic syntax"
            )
        else:
            # CoW mode (paper's main contribution)
            self.system_prompt = (
                "You are an expert Lean 4 developer implementing a mathematical plan to prove a theorem. "
                "You will be given the full source code of the CoW Lean library in a <lean_context> block. "
                "Follow this strict decision hierarchy:\n"
                "  1. FIRST, read the <lean_context> source carefully to find existing definitions and lemmas.\n"
                "  2. If you need the exact statement of a specific CoW definition, use the `get_cow_definition` tool.\n"
                "  3. Only as a LAST RESORT (for Mathlib lemmas you've forgotten), use `search_lean_explore`.\n"
                "  4. Output the exact Lean 4 proof body enclosed in ```lean4 ... ```. Do NOT output imports or theorem signatures.\n"
                "  5. If, and ONLY IF, the plan itself is mathematically impossible given what you see in the source, "
                "output a <reasoning> block explaining precisely why (e.g., 'the lemma X requires Y but the hypothesis only provides Z').\n"
                "  6. Do NOT output a <reasoning> block simply because a definition is unfamiliar — look it up first.\n"
                "CRITICAL: Do NOT use the `sorry` tactic or placeholder under any circumstances in your final proof code.\n"
                "Note: If a previous proof attempt and its verifier errors are provided, try to reuse, repair, or adapt that code "
                "wherever possible to maintain progress, unless the new mathematical plan requires a completely different approach.\n\n"
                "OUTPUT FORMAT:\n"
                "- Output ONLY the tactic proof body that replaces the `sorry`\n"
                "- No imports, no namespace declarations, no variable declarations\n"
                "- The proof will be inserted directly into an existing file\n\n"
                "LEAN 4 SYNTAX RULES:\n"
                "- This is Lean 4, not Lean 3. Key differences:\n"
                "  · No begin...end blocks. Use `by` followed by indented tactics\n"
                "  · Subgoals use · bullets or { } blocks, not comma-separated lists\n"
                "  · Tactic names may differ from Lean 3 (e.g. contrapose not contraposition)\n"
                "  · When unsure of a tactic name, prefer exact with a Mathlib lemma\n\n"
                "TOOL USE RULES:\n"
                "- Tool calls are separate from proof output\n"
                "- Never write tool call syntax inside a lean code block\n"
                "- Lean code blocks contain ONLY valid Lean 4 tactic syntax"
            )

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_repair(
        self,
        plan: str,
        verifier_feedback: str,
        original_region: str,
        theorem_name: Optional[str],
        start_line: int,
        end_line: int,
        lean_context: str = "",
        reasoning: Optional[str] = None,
    ) -> Tuple[ProofPatch, Optional[str]]:
        """
        Attempt to implement the plan and fix the proof.

        Returns
        -------
        (patch, failure_reasoning)
            patch              : ProofPatch with the suggested replacement.
            failure_reasoning  : non-None only when the Builder decides the
                                 plan is unworkable (triggers Planner re-plan).
        """
        mode = os.getenv("PROVER_MODE", "cow").lower().strip()

        # ── First message of this planning cycle ──────────────────────────
        if not self.history:
            context_block = ""
            if lean_context and mode == "cow":
                context_block = (
                    f"\n\nHere is the full source of the Lean library being used:\n"
                    f"<lean_context>\n{lean_context}\n</lean_context>\n\n"
                )

            failed_block = ""
            if getattr(self, "last_failed_attempt", None):
                prev_code = self.last_failed_attempt.get("proof", "")
                prev_err = self.last_failed_attempt.get("error", "")
                failed_block = (
                    f"\n\n--- Previous Proof Attempt ---\n"
                    f"Code from the last planning iteration:\n```lean4\n{prev_code}\n```\n"
                    f"Associated verifier feedback/errors:\n{prev_err}\n"
                    f"-------------------------------\n\n"
                )

            reasoning_block = ""
            if reasoning:
                reasoning_block = (
                    f"Here is the planner's conceptual reasoning:\n"
                    f"<reasoning>\n{reasoning}\n</reasoning>\n\n"
                )

            self.history.append({
                "role": "user",
                "content": (
                    f"{context_block}"
                    f"{failed_block}"
                    f"{reasoning_block}"
                    f"Here is the mathematical plan to implement:\n<plan>\n{plan}\n</plan>\n\n"
                    f"Here is the current verifier feedback:\n{verifier_feedback}\n\n"
                    f"Current proof body to fix:\n```lean4\n{original_region}\n```\n\n"
                    "Please generate the corrected Lean 4 proof body."
                ),
            })
        else:
            # Subsequent attempts within the same plan
            if mode == "cow":
                reminder = "Remember to consult the <lean_context> from earlier, or use `get_cow_definition` if needed. "
            else:
                reminder = "Remember to use `get_lean_goal_state` or `search_lean_explore` if needed. "
            self.history.append({
                "role": "user",
                "content": (
                    f"The previous patch failed. New verifier feedback:\n{verifier_feedback}\n\n"
                    f"Please revise your Lean 4 code. {reminder}Provide the corrected proof body or a <reasoning> block."
                ),
            })

        # ── Tool-use loop (max 2 tool call cycles) ────────────────────────
        tools = self.toolbox.get_tool_schemas()
        if mode == "normal":
            allowed = {"get_lean_goal_state", "search_lean_explore"}
            tools = [t for t in tools if t["name"] in allowed]

        final_text = ""
        for _ in range(2):
            response = self._call_llm(tools)
            content_blocks = response.get("content", [])

            text_blocks = [b["text"] for b in content_blocks if b["type"] == "text"]
            if text_blocks:
                final_text = "\n".join(text_blocks)

            tool_use_blocks = [b for b in content_blocks if b["type"] == "tool_use"]
            if not tool_use_blocks:
                break

            self.history.append({"role": "assistant", "content": content_blocks})
            tool_results = []
            for blk in tool_use_blocks:
                print(f"[Builder] 🛠️  Tool call: {blk['name']}({blk['input']})")
                result_str = self.toolbox.execute_tool(blk["name"], blk["input"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": blk["id"],
                    "content": result_str,
                })

            self.history.append({"role": "user", "content": tool_results})
            self.history.append({
                "role": "user",
                "content": (
                    "You have received the tool results. Do NOT use any more tools. "
                    "Provide ONLY the corrected proof body in ```lean4 ... ```, "
                    "or a <reasoning> block if the plan is fundamentally broken."
                ),
            })
            final_response = self._call_llm(tools=None)
            final_content = final_response.get("content", [])
            text_blocks = [b["text"] for b in final_content if b["type"] == "text"]
            if text_blocks:
                final_text = "\n".join(text_blocks)

        self.history.append({"role": "assistant", "content": final_text})

        # ── Parse result ──────────────────────────────────────────────────
        reasoning_match = re.search(
            r"<reasoning>(.*?)</reasoning>", final_text, re.DOTALL
        )
        failure_reasoning = reasoning_match.group(1).strip() if reasoning_match else None
        replacement = self._extract_lean_code(final_text)

        patch = ProofPatch(
            original_region=original_region,
            replacement_region=replacement,
            theorem_name=theorem_name,
            start_line=start_line,
            end_line=end_line,
            patch_reason="Builder Agent implementation.",
        )
        return patch, failure_reasoning

    def clear_memory(self, keep_last_failed=None):
        """Reset conversation history for a new planning cycle."""
        self.history = []
        self.last_failed_attempt = keep_last_failed

    def get_learned_definitions(self) -> str:
        """Return any text returned by tools during this attempt."""
        learned = []
        for msg in self.history:
            if isinstance(msg["content"], list):
                for blk in msg["content"]:
                    if blk.get("type") == "tool_result":
                        learned.append(str(blk.get("content", "")))
        return "\n\n".join(learned)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _call_llm(self, tools):
        backend = os.getenv("PROVER_BACKEND", "CLAUDE").upper().strip()
        if backend == "DEEPSEEK":
            from llm.deepseek import generate_with_tools
        elif backend == "KIMI":
            from llm.kimi import generate_with_tools
        else:
            from llm.claude import generate_with_tools
        return generate_with_tools(self.history, self.system_prompt, tools)

    def _extract_lean_code(self, response: str) -> str:
        match = re.search(r"```lean(?:4)?\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            return self._strip_declaration_wrapper(code)
        if "<reasoning>" in response and not match:
            return "sorry"
        return response.strip()

    def _strip_declaration_wrapper(self, code: str) -> str:
        """
        If the LLM outputs a full theorem/lemma declaration, extract only
        the proof body (tactics after ':= by').  If the code is already a
        pure proof body, return as-is.
        """
        lines = code.split("\n")
        first = next((l.strip() for l in lines if l.strip()), "")
        is_decl = any(
            first.startswith(kw)
            for kw in ("theorem ", "lemma ", "def ", "private lemma ")
        )
        if not is_decl:
            return code

        body_lines = []
        in_body = False
        for line in lines:
            if not in_body:
                if ":= by" in line:
                    in_body = True
                    after = line.split(":= by", 1)[1].strip()
                    if after:
                        body_lines.append("  " + after)
                elif ":=" in line and "by" not in line:
                    in_body = True
                    after = line.split(":=", 1)[1].strip()
                    if after:
                        body_lines.append(after)
            else:
                body_lines.append(line)

        return "\n".join(body_lines).strip() if body_lines else code
