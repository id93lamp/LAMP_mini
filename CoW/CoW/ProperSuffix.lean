-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Factor

namespace CoW

variable {α : Type*}

/-! ### Proper suffix -/

def IsProperSuffix (u w : Word α) : Prop := u ≤ₛ w ∧ u ≠ w

scoped infixl:50 " <ₛ " => IsProperSuffix

lemma IsProperSuffix.iff (u w : Word α) :
    (u <ₛ w) ↔ ∃ v, w = v ++ u ∧ v ≠ [] := by
  constructor
  · rintro ⟨hsuf, hne⟩
    obtain ⟨v, hv⟩ := (IsSuffix.def u w).mp hsuf
    refine ⟨v, hv, fun hv0 => hne ?_⟩
    simp only [hv, hv0, List.nil_append]
  · rintro ⟨v, hv, hv0⟩
    refine ⟨(IsSuffix.def u w).mpr ⟨v, hv⟩, fun heq => ?_⟩
    rw [heq] at hv
    have hlen := congr_arg List.length hv
    simp only [List.length_append] at hlen
    have : List.length v = 0 := by omega
    exact hv0 (List.length_eq_zero.mp this)

end CoW
