import CoW.Word
import CoW.Factor
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Ring

/-!
# CoW.Morphism
Morphisms (homomorphisms) of free monoids over words.

A word morphism `f : Word α → Word β` is a monoid homomorphism, i.e.,
  f(ε) = ε  and  f(uv) = f(u)f(v)
Since `Word α = List α`, morphisms are determined by their values on
single letters.  We represent them as functions `α → Word β` extended
to words by `List.flatMap` (= `List.bind`), which is the canonical free
monoid extension.
-/

namespace CoW

variable {α β γ δ : Type*}

/-! ### Core morphism definition -/

/-- A word morphism is given by a letter map `α → Word β`.
    Its extension to words is by `List.flatMap`. -/
def applyMorphism (f : α → Word β) (w : Word α) : Word β :=
  w.flatMap f

/-- Notation: apply morphism `f` to word `w`. -/
scoped infixl:70 " •w " => applyMorphism

/-! ### Morphism laws -/

@[simp]
lemma applyMorphism_empty (f : α → Word β) :
    f •w ([] : Word α) = [] := rfl

@[simp]
lemma applyMorphism_letter (f : α → Word β) (a : α) :
    f •w Word.letter a = f a := by
  simp only [applyMorphism, Word.letter, List.flatMap_cons, List.flatMap_nil,
             List.append_nil]

@[simp]
lemma applyMorphism_concat (f : α → Word β) (u v : Word α) :
    f •w (u ⬝ v) = (f •w u) ⬝ (f •w v) := by
  simp only [applyMorphism, Word.concat, List.flatMap_append]

/-- Morphisms preserve the monoid multiplication (homomorphism property). -/
@[simp]
lemma applyMorphism_mul (f : α → Word β) (u v : Word α) :
    f •w (u * v) = (f •w u) * (f •w v) :=
  applyMorphism_concat f u v

/-- Morphisms commute with powers. -/
lemma applyMorphism_pow (f : α → Word β) (w : Word α) (n : ℕ) :
    f •w (w ^ n) = (f •w w) ^ n := by
  induction n with
  | zero      =>
    change f •w Word.empty = Word.empty
    rfl
  | succ n ih =>
    rw [Word.pow_succ, applyMorphism_concat, ih, ← Word.pow_succ]

/-! ### Composition of morphisms -/

/-- Composition of two morphisms. -/
def compMorphism (g : β → Word γ) (f : α → Word β) : α → Word γ :=
  fun a => g •w (f a)

/-- Application of a composed morphism equals composition of applications. -/
lemma applyMorphism_comp (g : β → Word γ) (f : α → Word β) (w : Word α) :
    (compMorphism g f) •w w = g •w (f •w w) := by
  induction w with
  | nil       => simp only [applyMorphism_empty]
  | cons a u ih =>
    simp only [applyMorphism, List.flatMap_cons]
    have ih2 : List.flatMap (compMorphism g f) u = List.flatMap g (List.flatMap f u) := ih
    rw [ih2, List.flatMap_append]
    rfl

/-- Composition is associative. -/
lemma compMorphism_assoc (h : γ → Word δ) (g : β → Word γ) (f : α → Word β) :
    compMorphism h (compMorphism g f) = compMorphism (compMorphism h g) f := by
  funext a
  simp only [compMorphism, applyMorphism_comp]

/-! ### Special morphism classes -/

/-- A morphism is *non-erasing* if no letter maps to the empty word. -/
def IsNonErasing (f : α → Word β) : Prop :=
  ∀ a : α, f a ≠ []

/-- A morphism is a *coding* (letter-to-letter map) if every letter maps to
    exactly one letter. -/
def IsCoding (f : α → Word β) : Prop :=
  ∀ a : α, (f a).length = 1

/-- Every coding is non-erasing. -/
lemma IsCoding.isNonErasing {f : α → Word β} (hf : IsCoding f) :
    IsNonErasing f := by
  intro a
  have h := hf a
  intro heq
  rw [heq] at h
  cases h

/-- A morphism is *uniform* of length `k` if every letter maps to a word
    of length exactly `k`.  Uniform morphisms are the foundation of D0L
    systems and automatic sequences. -/
def IsUniform (f : α → Word β) (k : ℕ) : Prop :=
  ∀ a : α, (f a).length = k

/-- A uniform morphism of length `k ≥ 1` is non-erasing. -/
lemma IsUniform.isNonErasing {f : α → Word β} {k : ℕ} (hf : IsUniform f k)
    (hk : 1 ≤ k) : IsNonErasing f := by
  intro a
  have h := hf a
  intro heq
  rw [heq] at h
  change 0 = k at h
  omega

/-- For a uniform morphism, the image of a word has predictable length. -/
lemma IsUniform.length_image {f : α → Word β} {k : ℕ}
    (hf : IsUniform f k) (w : Word α) :
    (f •w w).length = w.length * k := by
  induction w with
  | nil       =>
    change 0 = 0 * k
    ring
  | cons a u ih =>
    simp only [applyMorphism, List.flatMap_cons, List.length_append, List.length_cons]
    have h1 : List.length (f a) = k := hf a
    have h2 : List.length (List.flatMap f u) = List.length u * k := ih
    rw [h1, h2]
    ring

/-- A coding is a uniform morphism of length 1. -/
lemma IsCoding.isUniform {f : α → Word β} (hf : IsCoding f) :
    IsUniform f 1 := hf

/-! ### Morphisms and factors -/

/-- Morphisms preserve factors: if `u` is a factor of `w`, then `f(u)` is
    a factor of `f(w)`. -/
lemma applyMorphism_preserves_factor {f : α → Word β} {u w : Word α}
    (h : u ≤f w) : (f •w u) ≤f (f •w w) := by
  obtain ⟨x, y, hw⟩ := h
  exact ⟨f •w x, f •w y, by simp only [hw, applyMorphism_concat, Word.concat,
                                         List.append_assoc]⟩

/-- Morphisms preserve prefixes. -/
lemma applyMorphism_preserves_prefix {f : α → Word β} {u w : Word α}
    (h : u ≤ₚ w) : (f •w u) ≤ₚ (f •w w) := by
  obtain ⟨v, hv⟩ := (IsPrefix.def u w).mp h
  apply (IsPrefix.def _ _).mpr
  exact ⟨f •w v, by simp only [hv, applyMorphism_concat, Word.concat]⟩

/-- Morphisms preserve suffixes. -/
lemma applyMorphism_preserves_suffix {f : α → Word β} {u w : Word α}
    (h : u ≤ₛ w) : (f •w u) ≤ₛ (f •w w) := by
  obtain ⟨v, hv⟩ := (IsSuffix.def u w).mp h
  apply (IsSuffix.def _ _).mpr
  exact ⟨f •w v, by simp only [hv, applyMorphism_concat, Word.concat]⟩

end CoW