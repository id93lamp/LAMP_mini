-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word

/-! # CoW.Conjugacy  -/

namespace CoW
variable {α : Type*}

-- (24) Conjugacy
def IsConjugate (u v : Word α) : Prop :=
  ∃ x y : Word α, u = x ⬝ y ∧ v = y ⬝ x
scoped infixl:50 " ~ " => IsConjugate

end CoW
