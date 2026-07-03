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

lemma IsProperPrefix.isPrefix {u w : Word α} (h : u <ₚ w) : u ≤ₚ w := h.1

lemma IsProperPrefix.length_lt {u w : Word α} (h : u <ₚ w) : u.length < w.length := by
  obtain ⟨hpre, hne⟩ := h
  have hle := IsPrefix.length_le hpre
  rcases Nat.lt_or_eq_of_le hle with hlt | heq
  · exact hlt
  · exfalso; apply hne
    obtain ⟨v, hv⟩ := (IsPrefix.def u w).mp hpre
    have hlen : List.length v = 0 := by
      have := congr_arg List.length hv
      simp only [List.length_append] at this
      have heq' : List.length u = List.length w := heq
      omega
    rw [List.length_eq_zero.mp hlen] at hv
    simpa using hv.symm

lemma IsProperPrefix.empty_of_ne_nil {w : Word α} (hw : w ≠ []) : ([] : Word α) <ₚ w :=
  ⟨IsPrefix.empty w, fun h => hw h.symm⟩

end CoW
