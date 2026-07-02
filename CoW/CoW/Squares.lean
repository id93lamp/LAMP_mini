-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import CoW.Factor
import CoW.Period

/-! # CoW.Squares  -/

namespace CoW
variable {α : Type*}

def IsSquare (s : Word α) : Prop := ∃ u : Word α, u ≠ [] ∧ s = u ++ u

end CoW
