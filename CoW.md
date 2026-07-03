# Combinatorics on Words (CoW) — Lean 4 Formalization Library

## Why CoW?

**Combinatorics on Words** is a branch of discrete mathematics and theoretical computer science that studies the properties of sequences (words) over finite alphabets. Despite its significance in areas like pattern matching, DNA sequence analysis, data compression, and formal language theory, the Lean 4 **Mathlib** ecosystem currently has **no dedicated contribution** for this domain.

The `CoW/` directory in LAMP provides a **specially curated, fully compilable** Lean 4 formalization that encodes the foundational ontology of Combinatorics on Words. This library serves dual purposes:
1. **Semantic grounding** for the LAMP multi-agent prover — agents query these exact definitions via MCP tools.
2. A **standalone formalization** that could serve as a foundation for future Mathlib contributions.

---

## Library Architecture

The library models words as lists over an arbitrary type:
```lean4
abbrev Word (α : Type*) := List α
```

It is organized into **8 modules** with a strict dependency hierarchy:

```
Word.lean (foundation)
  ├── Factor.lean (prefix, suffix, factor)
  │     ├── ProperPrefix.lean
  │     ├── ProperSuffix.lean
  │     └── Border.lean (depends on ProperPrefix + ProperSuffix)
  ├── Conjugacy.lean
  ├── Period.lean
  └── Morphism.lean
```

Custom notation is used throughout:
| Notation | Meaning | Definition |
|---|---|---|
| `u ⬝ v` | Concatenation | `u ++ v` |
| `u ≤ₚ w` | Prefix | `∃ s, w = u ++ s` |
| `u ≤ₛ w` | Suffix | `∃ p, w = p ++ u` |
| `u ≤f w` | Factor | `∃ x y, w = x ++ u ++ y` |
| `u <ₚ w` | Proper Prefix | `u ≤ₚ w ∧ u ≠ w` |
| `u <ₛ w` | Proper Suffix | `u ≤ₛ w ∧ u ≠ w` |
| `u ~ v` | Conjugacy | `∃ x y, u = x ⬝ y ∧ v = y ⬝ x` |


### Declaration Summary

| S.No | Module | Definitions | Lemmas | Total |
|:---:|---|:---:|:---:|:---:|
| 1 | Word | 4 | 18 | 22 |
| 2 | Factor | 4 | 18 | 22 |
| 3 | ProperPrefix | 1 | 4 | 5 |
| 4 | ProperSuffix | 1 | 4 | 5 |
| 5 | Border | 3 | 4 | 7 |
| 6 | Conjugacy | 1 | 3 | 4 |
| 7 | Period | 3 | 6 | 9 |
| 8 | Morphism | 5 | 14 | 19 |
| | **Total** | **22** | **71** | **93** |

> **Note:** Word counts 4 definitions (`Word.empty`, `Word.length`, `Word.letter`, `Word.concat`) including `abbrev` declarations.

---

## Module-by-Module Documentation

### 1. `Word.lean` — Core Word Type & Operations

Establishes the monoid structure of words under concatenation.

#### Definitions
| S.No | Name | Type | Statement |
|:---:|---|---|---|
| 1 | `Word.empty` | `def` | `Word.empty : Word α := []` |
| 2 | `Word.length` | `abbrev` | `Word.length (w : Word α) : ℕ := List.length w` |
| 3 | `Word.letter` | `def` | `Word.letter (a : α) : Word α := [a]` |
| 4 | `Word.concat` | `abbrev` | `Word.concat (u v : Word α) : Word α := u ++ v` |

#### Lemmas — Length Properties
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `Word.length_empty` | `(Word.empty : Word α).length = 0` |
| 2 | `Word.length_letter` | `(Word.letter a).length = 1` |
| 3 | `Word.length_concat` | `(u ⬝ v).length = u.length + v.length` |
| 4 | `Word.length_pow` | `(w ^ n).length = n * w.length` |
| 5 | `Word.length_pow_eq` | `(w ^ n).length = n * w.length` *(simp lemma)* |

#### Lemmas — Concatenation Algebra
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `Word.concat_empty_right` | `w ⬝ Word.empty = w` |
| 2 | `Word.concat_empty_left` | `Word.empty ⬝ w = w` |
| 3 | `Word.concat_assoc` | `(u ⬝ v) ⬝ w = u ⬝ (v ⬝ w)` |
| 4 | `Word.concat_eq_mul` | `u ⬝ v = u * v` |
| 5 | `Word.mul_eq_concat` | `u * v = u ⬝ v` |
| 6 | `Word.one_eq_empty` | `(1 : Word α) = Word.empty` |

#### Lemmas — Power Laws
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `Word.pow_zero` | `w ^ 0 = Word.empty` |
| 2 | `Word.pow_succ` | `w ^ (n + 1) = w ^ n ⬝ w` |
| 3 | `Word.pow_one` | `w ^ 1 = w` |
| 4 | `Word.one_pow` | `([] : Word α) ^ n = []` |
| 5 | `Word.pow_add` | `w ^ (m + n) = w ^ m ⬝ w ^ n` |
| 6 | `Word.pow_mul` | `w ^ (m * n) = (w ^ m) ^ n` |
| 7 | `Word.pow_mul'` | `w ^ (m * n) = (w ^ n) ^ m` |

---

### 2. `Factor.lean` — Prefix, Suffix, and Factor Relations

Defines the compositional hierarchy of substrings with full transitivity chains.

#### Definitions
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `IsPrefix` | `def IsPrefix (u w : Word α) : Prop := List.IsPrefix u w` |
| 2 | `IsSuffix` | `def IsSuffix (u w : Word α) : Prop := List.IsSuffix u w` |
| 3 | `IsFactor` | `def IsFactor (u w : Word α) : Prop := ∃ x y : Word α, w = x ++ u ++ y` |
| 4 | `IsFactorClosed` | `def IsFactorClosed (S : Set (Word α)) : Prop := ...` |

#### Prefix Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `IsPrefix.def` | `(u ≤ₚ w) ↔ ∃ v, w = u ++ v` |
| 2 | `IsPrefix.empty` | `([] : Word α) ≤ₚ w` |
| 3 | `IsPrefix.self` | `w ≤ₚ w` |
| 4 | `IsPrefix.length_le` | `u ≤ₚ w → u.length ≤ w.length` |
| 5 | `IsPrefix.trans` | `u ≤ₚ v → v ≤ₚ w → u ≤ₚ w` |

#### Suffix Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `IsSuffix.def` | `(u ≤ₛ w) ↔ ∃ p, w = p ++ u` |
| 2 | `IsSuffix.empty` | `([] : Word α) ≤ₛ w` |
| 3 | `IsSuffix.self` | `w ≤ₛ w` |
| 4 | `IsSuffix.length_le` | `u ≤ₛ w → u.length ≤ w.length` |
| 5 | `IsSuffix.trans` | `u ≤ₛ v → v ≤ₛ w → u ≤ₛ w` |

#### Factor Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `IsFactor.empty` | `([] : Word α) ≤f w` |
| 2 | `IsFactor.self` | `w ≤f w` |
| 3 | `IsFactor.of_prefix` | `u ≤ₚ w → u ≤f w` |
| 4 | `IsFactor.of_suffix` | `u ≤ₛ w → u ≤f w` |
| 5 | `IsFactor.of_concat_left` | `w ≤f (w ⬝ y)` |
| 6 | `IsFactor.of_concat_right` | `w ≤f (x ⬝ w)` |
| 7 | `IsFactor.length_le` | `u ≤f w → u.length ≤ w.length` |
| 8 | `IsFactor.trans` | `u ≤f v → v ≤f w → u ≤f w` |

---

### 3. `ProperPrefix.lean` — Strict Prefix Relation

#### Definitions & Lemmas
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `IsProperPrefix` | `def IsProperPrefix (u w : Word α) : Prop := u ≤ₚ w ∧ u ≠ w` |
| 2 | `IsProperPrefix.def` | Equivalence form |
| 3 | `IsProperPrefix.isPrefix` | `u <ₚ w → u ≤ₚ w` |
| 4 | `IsProperPrefix.length_lt` | `u <ₚ w → u.length < w.length` |
| 5 | `IsProperPrefix.empty_of_ne_nil` | `w ≠ [] → ([] : Word α) <ₚ w` |

---

### 4. `ProperSuffix.lean` — Strict Suffix Relation

#### Definitions & Lemmas
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `IsProperSuffix` | `def IsProperSuffix (u w : Word α) : Prop := u ≤ₛ w ∧ u ≠ w` |
| 2 | `IsProperSuffix.iff` | Equivalence form |
| 3 | `IsProperSuffix.isSuffix` | `u <ₛ w → u ≤ₛ w` |
| 4 | `IsProperSuffix.length_lt` | `u <ₛ w → u.length < w.length` |
| 5 | `IsProperSuffix.empty_of_ne_nil` | `w ≠ [] → ([] : Word α) <ₛ w` |

---

### 5. `Border.lean` — Border Theory

A border is a word that is **simultaneously** a proper prefix and a proper suffix.

#### Definitions
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `IsBorder` | `def IsBorder (b w : Word α) : Prop := b <ₚ w ∧ b <ₛ w` |
| 2 | `IsUnbordered` | `def IsUnbordered (w : Word α) : Prop := ∀ b, IsBorder b w → b = []` |
| 3 | `IsLongestBorder` | `def IsLongestBorder (b w : Word α) : Prop := ...` |

#### Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `IsBorder.length_lt` | `IsBorder b w → b.length < w.length` |
| 2 | `IsBorder.isFactor` | `IsBorder b w → b ≤f w` |
| 3 | `IsBorder.empty` | `w ≠ [] → IsBorder [] w` |
| 4 | `not_isBorder_self` | `¬ IsBorder w w` |

---

### 6. `Conjugacy.lean` — Cyclic Shifts

Two words are conjugate if one is a cyclic rotation of the other.

#### Definitions & Lemmas
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `IsConjugate` | `def IsConjugate (u v : Word α) : Prop := ∃ x y, u = x ++ y ∧ v = y ++ x` |
| 2 | `IsConjugate.refl` | `w ~ w` |
| 3 | `IsConjugate.symm` | `u ~ v → v ~ u` |
| 4 | `IsConjugate.length_eq` | `u ~ v → u.length = v.length` |

---

### 7. `Period.lean` — Periodicity & Primitivity

#### Definitions
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `HasPeriod` | `0 < p ∧ ∀ i, i + p < w.length → w.get? i = w.get? (i + p)` |
| 2 | `IsMinimalPeriod` | `HasPeriod w p` and no smaller period exists |
| 3 | `IsPrimitive` | `w ≠ [] ∧ ¬ ∃ (u : Word α) (k : ℕ), k ≥ 2 ∧ w = u ^ k` |

#### Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `HasPeriod.gt_zero` | `HasPeriod w p → 0 < p` |
| 2 | `hasPeriod_length` | `w ≠ [] → HasPeriod w w.length` |
| 3 | `isPrimitive_letter` | `IsPrimitive (Word.letter a)` |
| 4 | `IsPrimitive.ne_empty` | `IsPrimitive w → w ≠ []` |
| 5 | `IsPrimitive.not_proper_power` | A primitive word cannot be `u ^ k` for `k ≥ 2` |
| 6 | `isPrimitive_iff` | Equivalence characterization of primitivity |

---

### 8. `Morphism.lean` — Word Morphisms

#### Definitions
| S.No | Name | Statement |
|:---:|---|---|
| 1 | `applyMorphism` | `def applyMorphism (f : α → Word β) (w : Word α) : Word β := w.flatMap f` |
| 2 | `compMorphism` | `def compMorphism (g : β → Word γ) (f : α → Word β) : α → Word γ` |
| 3 | `IsNonErasing` | `∀ a, f a ≠ []` |
| 4 | `IsCoding` | `∀ a, (f a).length = 1` |
| 5 | `IsUniform` | `∀ a, (f a).length = k` |

#### Core Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `applyMorphism_empty` | `applyMorphism f [] = []` |
| 2 | `applyMorphism_letter` | `applyMorphism f [a] = f a` |
| 3 | `applyMorphism_concat` | `applyMorphism f (u ++ v) = applyMorphism f u ++ applyMorphism f v` |
| 4 | `applyMorphism_mul` | Morphisms distribute over multiplication |
| 5 | `applyMorphism_pow` | `applyMorphism f (w ^ n) = (applyMorphism f w) ^ n` |

#### Composition Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `applyMorphism_comp` | `applyMorphism (compMorphism g f) w = applyMorphism g (applyMorphism f w)` |
| 2 | `compMorphism_assoc` | Morphism composition is associative |

#### Classification Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `IsCoding.isNonErasing` | Every coding is non-erasing |
| 2 | `IsCoding.isUniform` | Every coding is uniform of length 1 |
| 3 | `IsUniform.isNonErasing` | Uniform morphisms with `k > 0` are non-erasing |
| 4 | `IsUniform.length_image` | `IsUniform f k → (applyMorphism f w).length = k * w.length` |

#### Preservation Lemmas
| S.No | Lemma | Statement |
|:---:|---|---|
| 1 | `applyMorphism_preserves_factor` | `u ≤f w → applyMorphism f u ≤f applyMorphism f w` |
| 2 | `applyMorphism_preserves_prefix` | `u ≤ₚ w → applyMorphism f u ≤ₚ applyMorphism f w` |
| 3 | `applyMorphism_preserves_suffix` | `u ≤ₛ w → applyMorphism f u ≤ₛ applyMorphism f w` |

---

*This library enables the LAMP agents to reason through complex string combinatorics with full formal verification, proving advanced properties about factors, borders, periodicity, and morphisms over finite alphabets — all in a domain that currently has no Mathlib coverage.*
