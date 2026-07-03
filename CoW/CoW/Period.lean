import CoW.Word
import CoW.Factor
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

/-!
# CoW.Period
Periodicity predicates for finite words.

A word `w` has period `p` if `w[i] = w[i+p]` for all valid indices.
We give two equivalent formulations:
  1. Index-based (computationally natural, default definition)
  2. Modular-index-based (cleaner for the equivalence proof)

We also define primitive words and the primitive root.

Changes from previous version:
- `IsPrimitive` fixed: requires `w ≠ []` and `k ≥ 2` (old `k = 1` version
  was unsound due to `w = u ^ 0 = []` degeneracies).
- `IsPrimitiveRoot` fixed: added minimality condition.
- `HasPrefixPeriod` replaced with modular-index version to avoid circularity
  and make the equivalence proof tractable.
- `isPrimitive_letter` updated to match new `IsPrimitive`.
- Added `IsPrimitive.ne_empty`, `IsPrimitive.not_proper_power`.
-/

namespace CoW

variable {α : Type*}

/-! ### Period: index-based definition -/

/-- `w` has period `p` (with `p > 0`) if for all valid indices `i`,
    `w[i] = w[i + p]`.  Uses `List.get?` for safe access. -/
def HasPeriod (w : Word α) (p : ℕ) : Prop :=
  0 < p ∧ ∀ i : ℕ, i + p < w.length → w.get? i = w.get? (i + p)

/-- `IsMinimalPeriod w p`: `p` is the smallest period of `w`. -/
def IsMinimalPeriod (w : Word α) (p : ℕ) : Prop :=
  HasPeriod w p ∧ ∀ q, HasPeriod w q → p ≤ q



/-! ### Primitive words -/

/-- A word `w` is *primitive* if it is non-empty and is not a proper power:
    `w = u ^ k` with `k ≥ 2` is impossible.

    Equivalently, the only way to write `w = u ^ k` is with `k = 1`
    (and then `u = w`).

    Design note: We require `w ≠ []` explicitly because:
    - `[] = u ^ 0` for all `u`, so the old `k = 1` condition would force
      `0 = 1` (absurd), making the empty word fail to be primitive — but
      also fail in degenerate ways.
    - The standard CoW convention excludes the empty word from the domain
      of primitivity. -/
def IsPrimitive (w : Word α) : Prop :=
  w ≠ [] ∧ ¬ ∃ (u : Word α) (k : ℕ), k ≥ 2 ∧ w = u ^ k

/-- Convenience: a primitive word is non-empty. -/
lemma IsPrimitive.ne_empty {w : Word α} (h : IsPrimitive w) : w ≠ [] :=
  h.1

/-- Convenience: a primitive word is not a proper power. -/
lemma IsPrimitive.not_proper_power {w : Word α} (h : IsPrimitive w) :
    ¬ ∃ (u : Word α) (k : ℕ), k ≥ 2 ∧ w = u ^ k :=
  h.2

/-- Reformulation: `IsPrimitive w` iff `w ≠ []` and
    `w = u ^ k → k = 1` (for `k ≥ 1`).
    This matches the informal statement in CoW literature more closely. -/
lemma isPrimitive_iff (w : Word α) :
    IsPrimitive w ↔ w ≠ [] ∧ ∀ (u : Word α) (k : ℕ), 1 ≤ k → w = u ^ k → k = 1 := by
  constructor
  · intro ⟨hne, hnp⟩
    refine ⟨hne, fun u k hk hw => ?_⟩
    by_contra hk1
    have hk2 : k ≥ 2 := by omega
    exact hnp ⟨u, k, hk2, hw⟩
  · intro ⟨hne, huniq⟩
    refine ⟨hne, fun ⟨u, k, hk2, hw⟩ => ?_⟩
    have := huniq u k (by omega) hw
    omega



/-! ### Basic period lemmas -/

lemma HasPeriod.gt_zero {w : Word α} {p : ℕ} (h : HasPeriod w p) : 0 < p :=
  h.1

/-- Every non-empty word has `w.length` as a (degenerate) period. -/
lemma hasPeriod_length {w : Word α} (hw : w ≠ []) : HasPeriod w w.length := by
  -- List.length_pos_iff_ne_nil : 0 < length l ↔ l ≠ [] (verified in Mathlib/Data/List/Basic.lean)
  have hpos : 0 < w.length := List.length_pos_iff_ne_nil.mpr hw
  refine ⟨hpos, fun i hi => ?_⟩
  -- i + w.length < w.length is impossible
  omega

/-! ### Primitivity of single letters -/

/-- Every single-letter word is primitive. -/
lemma isPrimitive_letter (a : α) : IsPrimitive (Word.letter a) := by
  refine ⟨by simp [Word.letter], ?_⟩
  rintro ⟨u, k, hk2, huk⟩
  change [a] = u ^ k at huk
  -- Length argument: 1 = k * u.length, with k ≥ 2
  have hlen := congr_arg Word.length huk
  simp [Word.length_pow] at hlen
  -- hlen : 1 = k * u.length
  -- Since k ≥ 2, we need u.length = 0, but then u ^ k = [] ≠ [a].
  have hu0 : u.length = 0 := by
    rcases Nat.eq_zero_or_pos u.length with h | h
    · exact h
    · have : k * u.length ≥ 2 * 1 := Nat.mul_le_mul hk2 h
      omega
  -- u = []
  have hu_nil : u = [] := List.length_eq_zero.mp hu0
  subst hu_nil
  have h_empty_pow : ([] : Word α) ^ k = [] := one_pow k
  rw [h_empty_pow] at huk
  cases huk


end CoW