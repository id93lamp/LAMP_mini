import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Algebra.Group.Defs
import Mathlib.Tactic.Ring

/-!
# CoW.Word
Core definitions for finite words over an alphabet.
Words are represented as `List α` where `α` is the alphabet type.

Design notes:
- `Word α := List α` gives us all of Mathlib's List infrastructure for free.
- We define a `Monoid` instance (concat / empty), so `w ^ n` and `w * v`
  come from the standard algebraic hierarchy — no custom `HPow` needed.
- `⬝` is notation for `*` (= `Word.concat`) so CoW-literature style is
  preserved while staying compatible with `simp` and `norm_num`.
- Power convention follows Mathlib: `w ^ (n+1) = w ^ n ⬝ w` (right concat),
  since that is what `Monoid.npow` implements internally.
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
lemma Word.length_empty : (Word.empty : Word α).length = 0 := rfl

@[simp]
lemma Word.length_letter (a : α) : (Word.letter a).length = 1 := rfl

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

/-- Words form a monoid under concatenation.
    This gives `w ^ n`, `w * v`, and all standard monoid lemmas for free. -/
instance : Monoid (Word α) where
  mul       := Word.concat
  one       := Word.empty
  mul_assoc := Word.concat_assoc
  one_mul   := Word.concat_empty_left
  mul_one   := Word.concat_empty_right

/-! ### Bridge: `⬝` and the monoid `*` are the same operation.
    These simp lemmas let automation work uniformly regardless of which
    notation appears in a goal. -/

lemma Word.concat_eq_mul (u v : Word α) : u ⬝ v = u * v := rfl

@[simp]
lemma Word.mul_eq_concat (u v : Word α) : u * v = u ⬝ v := rfl

@[simp]
lemma Word.one_eq_empty : (1 : Word α) = Word.empty := rfl

/-! ### Power lemmas
    The Monoid instance provides `w ^ n` via `Monoid.npow` which follows
    Mathlib's standard right-multiplication convention:
      `w ^ 0     = ε`
      `w ^ (n+1) = w ^ n * w = w ^ n ⬝ w`
    We expose this as `Word.pow_succ` and derive length / add / mul lemmas. -/

@[simp]
lemma Word.pow_zero (w : Word α) : w ^ 0 = Word.empty := rfl

/-- `w ^ (n + 1) = w ^ n ⬝ w`  (right-concatenation, matching Mathlib's npow). -/
@[simp]
lemma Word.pow_succ (w : Word α) (n : ℕ) : w ^ (n + 1) = w ^ n ⬝ w :=
  _root_.pow_succ w n

lemma Word.length_pow (w : Word α) (n : ℕ) :
    (w ^ n).length = n * w.length := by
  induction n with
  | zero      => simp
  | succ n ih =>
    rw [Word.pow_succ, Word.length_concat, ih]
    ring

@[simp]
lemma Word.one_pow (n : ℕ) : ([] : Word α) ^ n = [] :=
  _root_.one_pow n

@[simp]
lemma Word.pow_one (w : Word α) : w ^ 1 = w :=
  _root_.pow_one w

/-! ### Utility lemmas -/

@[simp]
lemma Word.length_pow_eq (w : Word α) (n : ℕ) :
    (w ^ n).length = n * w.length := Word.length_pow w n

lemma Word.pow_add (w : Word α) (m n : ℕ) : w ^ (m + n) = w ^ m ⬝ w ^ n :=
  _root_.pow_add w m n

lemma Word.pow_mul (w : Word α) (m n : ℕ) : w ^ (m * n) = (w ^ m) ^ n :=
  _root_.pow_mul w m n

lemma Word.pow_mul' (w : Word α) (m n : ℕ) : w ^ (m * n) = (w ^ n) ^ m := by
  rw [Nat.mul_comm, Word.pow_mul]

end CoW