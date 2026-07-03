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

lemma IsProperSuffix.isSuffix {u w : Word α} (h : u <ₛ w) : u ≤ₛ w := h.1

lemma IsProperSuffix.length_lt {u w : Word α} (h : u <ₛ w) : u.length < w.length := by
  obtain ⟨hsuf, hne⟩ := h
  have hle := IsSuffix.length_le hsuf
  rcases Nat.lt_or_eq_of_le hle with hlt | heq
  · exact hlt
  · exfalso; apply hne
    obtain ⟨v, hv⟩ := (IsSuffix.def u w).mp hsuf
    have hlen : List.length v = 0 := by
      have := congr_arg List.length hv
      simp only [List.length_append] at this
      have heq' : List.length u = List.length w := heq
      omega
    rw [List.length_eq_zero.mp hlen] at hv
    simpa using hv.symm

lemma IsProperSuffix.empty_of_ne_nil {w : Word α} (hw : w ≠ []) : ([] : Word α) <ₛ w :=
  ⟨IsSuffix.empty w, fun h => hw h.symm⟩

end CoW
