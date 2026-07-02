"""
run_example.py — LAMP_mini Quick-Start
=======================================
Runs 3 theorems through the full LAMP_mini pipeline and prints each step's output.
This is the recommended first script to run after setup.

Theorems selected:
  1. word_length_eq_zero_iff   (Easy)   — smoke test
  2. prefix_antisymm           (Medium) — length reasoning + antisymmetry
  3. border_of_border_is_border (Hard)  — transitivity of borders

Usage:
    python run_example.py

Prerequisites:
    1. Copy .env.example → .env and fill in your API key.
    2. Build the Lean REPL:   cd repl && lake build
    3. Build the CoW library:  cd CoW  && lake build
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

from orchestrator import LAMPOrchestrator
from verifier import verify_lean4_file, parse_lean_result

# ── Shared Lean imports ───────────────────────────────────────────────────────
IMPORTS = """\
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
NS_END = "\nend CoW"

# ── 3 example theorems ────────────────────────────────────────────────────────
EXAMPLES = [
    {
        "name": "word_length_eq_zero_iff",
        "difficulty": "EASY",
        "description": "A word has length 0 iff it is the empty list.",
        "statement": """\
theorem word_length_eq_zero_iff (w : Word α) :
    w.length = 0 ↔ w = [] := by
  sorry
""",
    },
    {
        "name": "prefix_antisymm",
        "difficulty": "MEDIUM",
        "description": "Prefix order is antisymmetric.",
        "statement": """\
theorem prefix_antisymm {u w : Word α} (h1 : u ≤ₚ w) (h2 : w ≤ₚ u) :
    u = w := by
  sorry
""",
    },
    {
        "name": "border_of_border_is_border",
        "difficulty": "HARD",
        "description": "Border relation is transitive: a border of a border is a border.",
        "statement": """\
theorem border_of_border_is_border {b₁ b₂ w : Word α}
    (h1 : IsBorder b₁ b₂) (h2 : IsBorder b₂ w) :
    IsBorder b₁ w := by
  sorry
""",
    },
]

LEAN_WORKSPACE = "CoW/"


def _check_env():
    """Warn if no API key is configured."""
    backend = os.getenv("PROVER_BACKEND", "CLAUDE").upper().strip()
    key_map = {
        "CLAUDE": "CLAUDE_API_KEY",
        "KIMI": "KIMI_API_KEY",
        "DEEPSEEK": "DEEPSEEK_API_KEY",
    }
    key_name = key_map.get(backend, "CLAUDE_API_KEY")
    key_val = os.getenv(key_name, "")
    if not key_val or "your_" in key_val:
        print(
            f"\n⚠️  Warning: {key_name} not set in .env.\n"
            f"   LAMP will simulate LLM responses (proofs will use `sorry`).\n"
            f"   Set PROVER_BACKEND and the corresponding API key for real results.\n"
        )
    else:
        print(f"[Setup] Backend: {backend}  |  Key: ...{key_val[-6:]}")


def run_example():
    print("=" * 65)
    print("  LAMP_mini — Quick-Start Example")
    print("  (This is a reduced demo. See paper for full system results.)")
    print("=" * 65)

    _check_env()

    orchestrator = LAMPOrchestrator(
        max_replans=3,
        max_build_attempts=3,
        lean_workspace=LEAN_WORKSPACE,
    )

    all_passed = True
    for i, ex in enumerate(EXAMPLES, 1):
        name = ex["name"]
        diff = ex["difficulty"]
        desc = ex["description"]
        lean_code = f"{IMPORTS}\n{ex['statement']}\n{NS_END}"

        print(f"\n{'─' * 65}")
        print(f"[{i}/3] {name}  [{diff}]")
        print(f"       {desc}")
        print(f"{'─' * 65}")

        t0 = time.time()
        try:
            final_proof = orchestrator.run(theorem_name=name, initial_proof=lean_code)
        except Exception as e:
            print(f"\n❌  Exception: {e}")
            all_passed = False
            continue

        elapsed = time.time() - t0

        # Final verification
        raw = verify_lean4_file(final_proof, timeout=60, lean_workspace=LEAN_WORKSPACE)
        result = parse_lean_result(raw)
        solved = result.passed and "sorry" not in final_proof

        if solved:
            print(f"\n✅  Proved in {elapsed:.1f}s")
            # Show just the proof body (lines after the theorem declaration)
            lines = final_proof.split("\n")
            in_proof = False
            for line in lines:
                if ":= by" in line:
                    in_proof = True
                if in_proof:
                    print(f"   {line}")
        else:
            print(f"\n❌  Failed after {elapsed:.1f}s")
            if result.errors:
                for err in result.errors[:3]:
                    print(f"   Error: {err.message[:120]}")
            all_passed = False

    print(f"\n{'=' * 65}")
    print("  Done. See benchmark.py to run the full 5-theorem suite.")
    print("=" * 65)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_example())
