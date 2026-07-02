import CoW.Factor

namespace CoW

variable {α : Type*}

/-! ### Proper prefix -/

def IsProperPrefix (u w : Word α) : Prop := u ≤ₚ w ∧ u ≠ w

scoped infixl:50 " <ₚ " => IsProperPrefix

lemma IsProperPrefix.def (u w : Word α) :
    (u <ₚ w) ↔ ∃ v, w = u ++ v ∧ v ≠ [] := by
  constructor
  · rintro ⟨hpre, hne⟩
    obtain ⟨v, hv⟩ := (IsPrefix.def u w).mp hpre
    refine ⟨v, hv, fun hv0 => hne ?_⟩
    simp only [hv, hv0, List.append_nil]
  · rintro ⟨v, hv, hv0⟩
    refine ⟨(IsPrefix.def u w).mpr ⟨v, hv⟩, fun heq => ?_⟩
    rw [heq] at hv
    have hlen := congr_arg List.length hv
    simp only [List.length_append] at hlen
    have : List.length v = 0 := by omega
    exact hv0 (List.length_eq_zero.mp this)

end CoW
