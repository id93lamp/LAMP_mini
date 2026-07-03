import CoW.Word
import CoW.Factor
import CoW.ProperPrefix
import CoW.ProperSuffix
import CoW.Period
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

/-!
# CoW.Border
Border theory for finite words.

A *border* of a word `w` is a word that is simultaneously a proper prefix
and a proper suffix of `w`.  Borders are central to:
- The Fine–Wilf periodicity theorem
- The KMP (Knuth–Morris–Pratt) failure function
- Overlap-free and border-free combinatorics
- Critical factorization theorem

This file develops:
1. Basic properties of borders (`IsBorder`)
2. The longest border function
3. Unbordered words
-/

namespace CoW

variable {α : Type*}

/-! ### Definitions -/

/-- A *border* of `w` is a word that is both a proper prefix and a proper suffix. -/
def IsBorder (b w : Word α) : Prop := b <ₚ w ∧ b <ₛ w

/-- A word is *unbordered* if its only border is the empty word. -/
def IsUnbordered (w : Word α) : Prop := ∀ b, IsBorder b w → b = []

/-! ### Basic border lemmas -/

/-- A border has strictly smaller length than the word it borders. -/
lemma IsBorder.length_lt {b w : Word α} (h : IsBorder b w) :
    b.length < w.length :=
  h.1.length_lt

/-- If `b` is a border of `w`, then `b` is also a factor of `w`. -/
lemma IsBorder.isFactor {b w : Word α} (h : IsBorder b w) : b ≤f w :=
  IsFactor.of_prefix h.1.1

/-- A non-empty word `w` always has the empty word as a border. -/
lemma IsBorder.empty {w : Word α} (hw : w ≠ []) : IsBorder [] w :=
  ⟨IsProperPrefix.empty_of_ne_nil hw, IsProperSuffix.empty_of_ne_nil hw⟩

/-- `w` itself is not a border of `w` (a border must be *proper*). -/
lemma not_isBorder_self (w : Word α) : ¬ IsBorder w w := by
  intro ⟨⟨_, hne⟩, _⟩
  exact hne rfl


/-! ### Longest border -/

/-- `b` is the longest border of `w`:  it is a border, and no longer border exists. -/
def IsLongestBorder (b w : Word α) : Prop :=
  IsBorder b w ∧ ∀ b' : Word α, IsBorder b' w → b'.length ≤ b.length

end CoW