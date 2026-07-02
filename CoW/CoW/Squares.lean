-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import CoW.Factor
import CoW.Period

/-! # CoW.Squares  (LAMP_mini — 0 counted declarations, stub)
Definition only — no additional lemmas in this mini package. -/

namespace CoW
variable {α : Type*}

def IsSquare (s : Word α) : Prop := ∃ u : Word α, u ≠ [] ∧ s = u ++ u

end CoW
