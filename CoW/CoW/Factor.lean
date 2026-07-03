import CoW.Word
import Mathlib.Data.List.Basic

/-!
# CoW.Factor
Prefix, suffix, and factor (subword/substring) predicates for finite words.

Design note: We lift `List.IsPrefix` and `List.IsSuffix` directly.
For CoW we need **contiguous** factors, so we define `IsFactor` explicitly
via the infix decomposition `w = x ++ u ++ y`.
-/

namespace CoW

variable {α : Type*}

-- Helper: unfold Word.length to List.length uniformly
private lemma wlen_eq {α} (w : Word α) : w.length = List.length w := rfl

/-! ### Prefix -/

/-- `u` is a prefix of `w` if there exists `v` such that `w = u ++ v`. -/
def IsPrefix (u w : Word α) : Prop := List.IsPrefix u w

scoped infixl:50 " ≤ₚ " => IsPrefix

/-- Unfolding: `u ≤ₚ w` iff `∃ v, w = u ++ v`. -/
lemma IsPrefix.def (u w : Word α) :
    (u ≤ₚ w) ↔ ∃ v, w = u ++ v := by
  constructor
  · intro ⟨v, hv⟩; exact ⟨v, hv.symm⟩
  · rintro ⟨v, hv⟩; exact ⟨v, hv.symm⟩

@[simp]
lemma IsPrefix.empty (w : Word α) : ([] : Word α) ≤ₚ w := List.nil_prefix

@[simp]
lemma IsPrefix.self (w : Word α) : w ≤ₚ w := List.prefix_refl w

lemma IsPrefix.length_le {u w : Word α} (h : u ≤ₚ w) : u.length ≤ w.length :=
  List.IsPrefix.length_le h

lemma IsPrefix.trans {u v w : Word α} (huv : u ≤ₚ v) (hvw : v ≤ₚ w) : u ≤ₚ w :=
  List.IsPrefix.trans huv hvw



/-! ### Suffix -/

def IsSuffix (u w : Word α) : Prop := List.IsSuffix u w

scoped infixl:50 " ≤ₛ " => IsSuffix

lemma IsSuffix.def (u w : Word α) :
    (u ≤ₛ w) ↔ ∃ v, w = v ++ u := by
  constructor
  · intro ⟨v, hv⟩; exact ⟨v, hv.symm⟩
  · rintro ⟨v, hv⟩; exact ⟨v, hv.symm⟩

@[simp]
lemma IsSuffix.empty (w : Word α) : ([] : Word α) ≤ₛ w := List.nil_suffix

@[simp]
lemma IsSuffix.self (w : Word α) : w ≤ₛ w := List.suffix_refl w

lemma IsSuffix.length_le {u w : Word α} (h : u ≤ₛ w) : u.length ≤ w.length :=
  List.IsSuffix.length_le h

lemma IsSuffix.trans {u v w : Word α} (huv : u ≤ₛ v) (hvw : v ≤ₛ w) : u ≤ₛ w :=
  List.IsSuffix.trans huv hvw





/-! ### Factor (contiguous subword) -/

def IsFactor (u w : Word α) : Prop := ∃ x y : Word α, w = x ++ u ++ y

scoped infixl:50 " ≤f " => IsFactor

@[simp]
lemma IsFactor.empty (w : Word α) : ([] : Word α) ≤f w :=
  ⟨[], w, by simp only [List.append_nil, List.nil_append]⟩

@[simp]
lemma IsFactor.self (w : Word α) : w ≤f w :=
  ⟨[], [], by simp only [List.append_nil, List.nil_append]⟩

lemma IsFactor.of_prefix {u w : Word α} (h : u ≤ₚ w) : u ≤f w := by
  obtain ⟨v, hv⟩ := (IsPrefix.def u w).mp h
  exact ⟨[], v, by simp only [List.nil_append, hv]⟩

lemma IsFactor.of_suffix {u w : Word α} (h : u ≤ₛ w) : u ≤f w := by
  obtain ⟨v, hv⟩ := (IsSuffix.def u w).mp h
  exact ⟨v, [], by simp only [List.append_nil, hv]⟩

lemma IsFactor.of_concat_left (w y : Word α) : w ≤f (w ⬝ y) :=
  IsFactor.of_prefix ⟨y, rfl⟩

lemma IsFactor.of_concat_right (x w : Word α) : w ≤f (x ⬝ w) :=
  IsFactor.of_suffix ⟨x, rfl⟩

lemma IsFactor.length_le {u w : Word α} (h : u ≤f w) : u.length ≤ w.length := by
  obtain ⟨x, y, hw⟩ := h
  have hlen := congr_arg List.length hw
  simp only [List.length_append] at hlen
  show List.length u ≤ List.length w
  omega

lemma IsFactor.trans {u v w : Word α} (huv : u ≤f v) (hvw : v ≤f w) : u ≤f w := by
  obtain ⟨x₁, y₁, hv⟩ := huv
  obtain ⟨x₂, y₂, hw⟩ := hvw
  exact ⟨x₂ ++ x₁, y₁ ++ y₂, by
    rw [hw, hv]
    simp only [List.append_assoc]⟩

/-! ### Factor-closed sets -/

def IsFactorClosed (S : Set (Word α)) : Prop :=
  ∀ u w : Word α, w ∈ S → u ≤f w → u ∈ S

end CoW