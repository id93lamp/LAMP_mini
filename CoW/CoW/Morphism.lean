-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import CoW.Factor
import Mathlib.Data.List.Basic

/-! # CoW.Morphism   -/

namespace CoW
variable {α β : Type*}

-- (25) Word morphism: extension of a letter map f : α → Word β
def applyMorphism (f : α → Word β) (w : Word α) : Word β := w.flatMap f
scoped infixl:70 " •w " => applyMorphism

end CoW
