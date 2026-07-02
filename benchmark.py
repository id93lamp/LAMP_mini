"""
CoW Mini Benchmark — 5 Theorems
================================
A representative subset of the full 90-theorem CoW evaluation suite,
selected for the LAMP_mini reviewer package.

Each theorem is a self-contained Lean 4 code string with `sorry` as the
proof placeholder.  The LAMP orchestrator replaces each `sorry` with a
verified proof.

NOTE: This mini suite is NOT representative of the full system's capability.
See the paper and the complete LAMP repository for the full 90-theorem
evaluation results.
"""

import time
import json
import os
from pathlib import Path

from orchestrator import LAMPOrchestrator
from verifier import verify_lean4_file, parse_lean_result

# ── Common imports ────────────────────────────────────────────────────────────

COMMON_IMPORTS = """\
import CoW.Word
import CoW.Factor
import CoW.ProperPrefix
import CoW.ProperSuffix
import CoW.Border
import CoW.Period
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

namespace CoW
variable {α : Type*}
"""

NAMESPACE_END = "\nend CoW"


def make_theorem(statement: str, imports: str = COMMON_IMPORTS) -> str:
    """Wrap a theorem statement in a complete Lean 4 file."""
    return f"{imports}\n{statement}\n{NAMESPACE_END}"


# ── 5 Benchmark Theorems ──────────────────────────────────────────────────────
# Distribution: 2 Easy · 2 Medium · 1 Hard
# Modules: Word (1), Factor (2), ProperPrefix (1), Border (1)

BENCHMARK_THEOREMS = [

    # ── Word (Easy) ──────────────────────────────────────────────────────────
    {
        "name": "word_length_eq_zero_iff",
        "difficulty": "EASY",
        "module": "Word",
        "statement": """\
theorem word_length_eq_zero_iff (w : Word α) :
    w.length = 0 ↔ w = [] := by
  sorry
""",
    },

    # ── Factor (Easy) ─────────────────────────────────────────────────────────
    {
        "name": "prefix_of_concat",
        "difficulty": "EASY",
        "module": "Factor",
        "statement": """\
theorem prefix_of_concat (u v : Word α) :
    u ≤ₚ (u ⬝ v) := by
  sorry
""",
    },

    # ── Factor (Medium) ───────────────────────────────────────────────────────
    {
        "name": "prefix_antisymm",
        "difficulty": "MEDIUM",
        "module": "Factor",
        "statement": """\
theorem prefix_antisymm {u w : Word α} (h1 : u ≤ₚ w) (h2 : w ≤ₚ u) :
    u = w := by
  sorry
""",
    },

    # ── ProperPrefix (Medium) ─────────────────────────────────────────────────
    {
        "name": "proper_prefix_trans",
        "difficulty": "MEDIUM",
        "module": "ProperPrefix",
        "statement": """\
theorem proper_prefix_trans {u v w : Word α}
    (huv : u <ₚ v) (hvw : v <ₚ w) : u <ₚ w := by
  sorry
""",
    },

    # ── Border (Hard) ─────────────────────────────────────────────────────────
    {
        "name": "border_of_border_is_border",
        "difficulty": "HARD",
        "module": "Border",
        "statement": """\
theorem border_of_border_is_border {b₁ b₂ w : Word α}
    (h1 : IsBorder b₁ b₂) (h2 : IsBorder b₂ w) :
    IsBorder b₁ w := by
  sorry
""",
    },
]


# ── Evaluation runner ─────────────────────────────────────────────────────────

def run_benchmark(lean_workspace: str = "CoW/", output_dir: str = "verified_proofs_mini"):
    """
    Run the full 5-theorem mini benchmark.

    Results are saved as JSON in the current directory and passing proofs
    are written as .lean files to output_dir/.
    """
    orchestrator = LAMPOrchestrator(
        max_replans=3,
        max_build_attempts=3,
        lean_workspace=lean_workspace,
    )
    os.makedirs(output_dir, exist_ok=True)
    results = []
    total = len(BENCHMARK_THEOREMS)

    print(f"\n{'=' * 65}")
    print(f"  LAMP_mini CoW Benchmark — {total} Theorems")
    print(f"  (NOT representative of full system — see paper for full results)")
    print(f"{'=' * 65}\n")

    for i, thm in enumerate(BENCHMARK_THEOREMS, 1):
        name = thm["name"]
        diff = thm["difficulty"]
        module = thm["module"]
        lean_code = make_theorem(thm["statement"])

        print(f"[{i:2d}/{total}] {module:>14s} | {diff:>6s} | {name}")

        t0 = time.time()
        try:
            final_proof = orchestrator.run(theorem_name=name, initial_proof=lean_code)
            no_sorry = "sorry" not in final_proof
            lean_verified = False
            if no_sorry:
                raw = verify_lean4_file(final_proof, timeout=60, lean_workspace=lean_workspace)
                v = parse_lean_result(raw)
                lean_verified = v.passed and not v.errors
            solved = no_sorry and lean_verified
            error = None
            if solved:
                out_path = os.path.join(output_dir, f"{name}.lean")
                with open(out_path, "w") as f:
                    f.write(final_proof)
        except Exception as e:
            solved = False
            error = str(e)

        elapsed = time.time() - t0
        results.append({
            "name": name, "difficulty": diff, "module": module,
            "solved": solved, "time_s": round(elapsed, 2), "error": error,
        })
        print(f"         {'✅' if solved else '❌'}  {elapsed:.1f}s\n")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print("  RESULTS SUMMARY")
    print(f"{'=' * 65}\n")
    for diff_level in ["EASY", "MEDIUM", "HARD"]:
        subset = [r for r in results if r["difficulty"] == diff_level]
        if subset:
            s = sum(1 for r in subset if r["solved"])
            print(f"  {diff_level:>6s}: {s}/{len(subset)}")
    total_solved = sum(1 for r in results if r["solved"])
    print(f"\n  TOTAL: {total_solved}/{total}  ({100 * total_solved / total:.1f}%)")

    # ── Per-module breakdown ──────────────────────────────────────────────────
    print(f"\n  {'Module':>14s}  Solved  Total")
    print(f"  {'-' * 14}  ------  -----")
    for mod in ["Word", "Factor", "ProperPrefix", "Border"]:
        subset = [r for r in results if r["module"] == mod]
        s = sum(1 for r in subset if r["solved"])
        print(f"  {mod:>14s}  {s:>4d}    {len(subset):>3d}")

    # ── Save ──────────────────────────────────────────────────────────────────
    outdir = Path("eval_results")
    outdir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    outpath = outdir / f"lamp_mini_benchmark_{ts}.json"
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved → {outpath}\n")
    return results


if __name__ == "__main__":
    run_benchmark()
