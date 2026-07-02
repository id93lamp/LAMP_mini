-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import Mathlib.Data.List.Basic

/-!
# CoW.Factor
Prefix, suffix, and factor (subword/substring) predicates for finite words.
-/

namespace CoW

variable {α : Type*}

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

lemma IsPrefix.length_le {u w : Word α} (h : u ≤ₚ w) : u.length ≤ w.length :=
  List.IsPrefix.length_le h

/-! ### Suffix -/

def IsSuffix (u w : Word α) : Prop := List.IsSuffix u w

scoped infixl:50 " ≤ₛ " => IsSuffix

lemma IsSuffix.def (u w : Word α) :
    (u ≤ₛ w) ↔ ∃ v, w = v ++ u := by
  constructor
  · intro ⟨v, hv⟩; exact ⟨v, hv.symm⟩
  · rintro ⟨v, hv⟩; exact ⟨v, hv.symm⟩

/-! ### Factor (contiguous subword) -/

def IsFactor (u w : Word α) : Prop := ∃ x y : Word α, w = x ++ u ++ y

scoped infixl:50 " ≤f " => IsFactor

end CoW
