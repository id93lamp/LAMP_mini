import CoW.Word

/-!
# CoW.Conjugacy
Conjugacy of words.

Two words are *conjugate* if one is a cyclic shift of the other.
Equivalently, `u` and `v` are conjugate if there exist words `x` and `y`
such that `u = x ⬝ y` and `v = y ⬝ x`.
-/

namespace CoW

variable {α : Type*}

/-- `u` and `v` are conjugate if there exist `x` and `y` such that `u = x ⬝ y` and `v = y ⬝ x`. -/
def IsConjugate (u v : Word α) : Prop :=
  ∃ x y : Word α, u = x ⬝ y ∧ v = y ⬝ x

scoped infixl:50 " ~ " => IsConjugate

lemma IsConjugate.refl (w : Word α) : w ~ w :=
  ⟨Word.empty, w, by simp, by simp⟩

lemma IsConjugate.symm {u v : Word α} (h : u ~ v) : v ~ u := by
  obtain ⟨x, y, h1, h2⟩ := h
  exact ⟨y, x, h2, h1⟩

lemma IsConjugate.length_eq {u v : Word α} (h : u ~ v) : u.length = v.length := by
  obtain ⟨x, y, h1, h2⟩ := h
  have l1 := congr_arg Word.length h1
  have l2 := congr_arg Word.length h2
  simp only [Word.length_concat] at l1 l2
  omega


end CoW
