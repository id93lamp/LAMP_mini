import CoW.Word

/-! # CoW.Conjugacy  (LAMP_mini — 1 declaration, stub) -/

namespace CoW
variable {α : Type*}

-- (24) Conjugacy
def IsConjugate (u v : Word α) : Prop :=
  ∃ x y : Word α, u = x ⬝ y ∧ v = y ⬝ x
scoped infixl:50 " ~ " => IsConjugate

end CoW
