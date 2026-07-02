import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Algebra.Group.Defs

/-!
# CoW.Word
Core definitions for finite words over an alphabet.
Words are represented as `List α` where `α` is the alphabet type.
-/

namespace CoW

variable {α : Type*}

/-- A finite word over alphabet α is a list of symbols. -/
abbrev Word (α : Type*) := List α

/-- The empty word. -/
def Word.empty : Word α := []

/-- Length of a word. Delegates to List.length. -/
abbrev Word.length (w : Word α) : ℕ := List.length w

/-- Single-letter word. -/
def Word.letter (a : α) : Word α := [a]

/-- Concatenation of two words. Delegates to List.append. -/
abbrev Word.concat (u v : Word α) : Word α := u ++ v

-- Notation for concatenation (matches standard CoW literature)
infixl:65 " ⬝ " => Word.concat

/-! ### Basic lemmas about length and concatenation -/

@[simp]
lemma Word.length_concat (u v : Word α) :
    (u ⬝ v).length = u.length + v.length :=
  List.length_append u v

@[simp]
lemma Word.concat_empty_right (w : Word α) : w ⬝ Word.empty = w :=
  List.append_nil w

@[simp]
lemma Word.concat_empty_left (w : Word α) : Word.empty ⬝ w = w :=
  List.nil_append w

lemma Word.concat_assoc (u v w : Word α) : (u ⬝ v) ⬝ w = u ⬝ (v ⬝ w) :=
  List.append_assoc u v w

/-- Words form a monoid under concatenation. -/
instance : Monoid (Word α) where
  mul       := Word.concat
  one       := Word.empty
  mul_assoc := Word.concat_assoc
  one_mul   := Word.concat_empty_left
  mul_one   := Word.concat_empty_right

@[simp]
lemma Word.mul_eq_concat (u v : Word α) : u * v = u ⬝ v := rfl

@[simp]
lemma Word.one_eq_empty : (1 : Word α) = Word.empty := rfl

@[simp]
lemma Word.pow_zero (w : Word α) : w ^ 0 = Word.empty := rfl

@[simp]
lemma Word.pow_succ (w : Word α) (n : ℕ) : w ^ (n + 1) = w ^ n ⬝ w :=
  _root_.pow_succ w n

end CoW
