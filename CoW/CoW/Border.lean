-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import CoW.Factor
import CoW.ProperPrefix
import CoW.ProperSuffix

/-!
# CoW.Border
Border theory for finite words.
-/

namespace CoW

variable {α : Type*}

/-- A *border* of `w` is a word that is both a proper prefix and a proper suffix. -/
def IsBorder (b w : Word α) : Prop := b <ₚ w ∧ b <ₛ w

end CoW
