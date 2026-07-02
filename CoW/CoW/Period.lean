-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

/-!
# CoW.Period
Primitivity for finite words.
-/

namespace CoW

variable {α : Type*}

/-- A word `w` is *primitive* if it is non-empty and is not a proper power. -/
def IsPrimitive (w : Word α) : Prop :=
  w ≠ [] ∧ ¬ ∃ (u : Word α) (k : ℕ), k ≥ 2 ∧ w = u ^ k

end CoW
