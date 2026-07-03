# CoW Evaluation suite — 90 Theorems

This reference document lists all 90 theorems in the Combinatorics on Words (CoW) evaluation suite, split into two batches of 45 theorems each.

## Combined Distribution Summary

| Module       | Easy | Medium | Hard | Combined Total |
|:-------------|:----:|:------:|:----:|:--------------:|
| Word         |  2   |   10   |  0   |       12       |
| Factor       |  2   |   11   |  2   |       15       |
| ProperPrefix |  2   |    8   |  0   |       10       |
| ProperSuffix |  2   |    8   |  0   |       10       |
| Border       |  2   |    8   |  2   |       12       |
| Conjugacy    |  2   |    5   |  2   |        9       |
| Period       |  2   |    3   |  5   |       10       |
| Morphism     |  1   |    5   |  6   |       12       |
| **Total**    |**15**| **58** |**17**|     **90**     |

---

## Full Theorem List

### Word (12)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| W1 | `word_length_eq_zero_iff` | Easy | 1 | `w.length = 0 ↔ w = []` |
| W2 | `word_length_pos_of_ne_nil` | Easy | 1 | `w ≠ [] → 0 < w.length` |
| W3 | `word_concat_right_cancel` | Medium | 1 | `u ⬝ w = v ⬝ w → u = v` |
| W4 | `word_concat_left_cancel` | Medium | 1 | `w ⬝ u = w ⬝ v → u = v` |
| W5 | `word_pow_two_length` | Medium | 1 | `(w²).length = 2 · w.length` |
| W6 | `word_pow_succ_left` | Medium | 1 | `w^(n+1) = w ⬝ w^n` |
| W7 | `pow_ne_empty_of_ne_empty` | Medium | 2 | `w^n ≠ []` (given `w ≠ []`, `0 < n`) |
| W8 | `concat_eq_nil_iff` | Medium | 2 | `u ⬝ v = [] ↔ u = [] ∧ v = []` |
| W9 | `pow_eq_nil_iff` | Medium | 2 | `w^n = [] ↔ (n = 0 ∨ w = [])` |
| W10 | `pow_comm_concat` | Medium | 2 | `w^m ⬝ w^n = w^n ⬝ w^m` |
| W11 | `pow_injective_of_ne_empty` | Medium | 2 | `w^m = w^n → m = n` (given `w ≠ []`) |
| W12 | `pow_add_length_eq` | Medium | 2 | `(w^(m+n)).length = (w^m).length + (w^n).length` |

### Factor (15)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| F1 | `prefix_of_concat` | Easy | 1 | `u ≤ₚ (u ⬝ v)` |
| F2 | `suffix_of_concat` | Easy | 1 | `v ≤ₛ (u ⬝ v)` |
| F3 | `prefix_antisymm` | Medium | 1 | `u ≤ₚ w → w ≤ₚ u → u = w` |
| F4 | `suffix_antisymm` | Medium | 1 | `u ≤ₛ w → w ≤ₛ u → u = w` |
| F5 | `prefix_of_factor_is_factor` | Medium | 1 | `u ≤ₚ v → v ≤f w → u ≤f w` |
| F6 | `suffix_of_factor_is_factor` | Medium | 1 | `u ≤ₛ v → v ≤f w → u ≤f w` |
| F7 | `prefix_concat_right` | Medium | 1 | `u ≤ₚ w → u ≤ₚ (w ⬝ v)` |
| F8 | `suffix_concat_left` | Medium | 1 | `u ≤ₛ w → u ≤ₛ (v ⬝ w)` |
| F9 | `factor_of_concat_left` | Medium | 2 | `u ≤f w → u ≤f (w ⬝ v)` |
| F10 | `factor_of_concat_right` | Medium | 2 | `u ≤f w → u ≤f (v ⬝ w)` |
| F11 | `prefix_of_pow_succ` | Medium | 2 | `w ≤ₚ w ^ (n + 1)` |
| F12 | `prefix_eq_of_length_eq` | Hard | 2 | `u ≤ₚ w → v ≤ₚ w → u.length = v.length → u = v` |
| F13 | `prefix_of_pow_le` | Medium | 2 | `m ≤ n → w^m ≤ₚ w^n` |
| F14 | `suffix_of_pow_le` | Medium | 2 | `m ≤ n → w^m ≤ₛ w^n` |
| F15 | `prefix_suffix_concat_partition` | Hard | 2 | `u ≤ₚ w → v ≤ₛ w → u.length + v.length = w.length → w = u ⬝ v` |

### ProperPrefix (10)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| PP1 | `proper_prefix_irrefl` | Easy | 1 | `¬ (w <ₚ w)` |
| PP2 | `proper_prefix_ne` | Easy | 1 | `u <ₚ w → u ≠ w` |
| PP3 | `prefix_lt_of_length_lt` | Medium | 1 | `u ≤ₚ w → u.length < w.length → u <ₚ w` |
| PP4 | `proper_prefix_trans` | Medium | 1 | `u <ₚ v → v <ₚ w → u <ₚ w` |
| PP5 | `proper_prefix_concat_ne_nil` | Medium | 1 | `v ≠ [] → u <ₚ (u ⬝ v)` |
| PP6 | `proper_prefix_of_prefix_of_proper_prefix` | Medium | 2 | `u ≤ₚ v → v <ₚ w → u <ₚ w` |
| PP7 | `proper_prefix_of_proper_prefix_of_prefix` | Medium | 2 | `u <ₚ v → v ≤ₚ w → u <ₚ w` |
| PP8 | `proper_prefix_witness` | Medium | 2 | `u <ₚ w → ∃ v, v ≠ [] ∧ w = u ⬝ v` |
| PP9 | `proper_prefix_witness_is_suffix` | Medium | 2 | `u <ₚ w → ∃ v, v ≠ [] ∧ w = u ⬝ v ∧ v ≤ₛ w` |
| PP10 | `proper_prefix_double_lt` | Medium | 2 | `u <ₚ v → v <ₚ w → u.length + 2 ≤ w.length` |

### ProperSuffix (10)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| PS1 | `proper_suffix_irrefl` | Easy | 1 | `¬ (w <ₛ w)` |
| PS2 | `proper_suffix_ne` | Easy | 1 | `u <ₛ w → u ≠ w` |
| PS3 | `suffix_lt_of_length_lt` | Medium | 1 | `u ≤ₛ w → u.length < w.length → u <ₛ w` |
| PS4 | `proper_suffix_trans` | Medium | 1 | `u <ₛ v → v <ₛ w → u <ₛ w` |
| PS5 | `proper_suffix_concat_ne_nil` | Medium | 1 | `v ≠ [] → u <ₛ (v ⬝ u)` |
| PS6 | `proper_suffix_of_suffix_of_proper_suffix` | Medium | 2 | `u ≤ₛ v → v <ₛ w → u <ₛ w` |
| PS7 | `proper_suffix_of_proper_suffix_of_suffix` | Medium | 2 | `u <ₛ v → v ≤ₛ w → u <ₛ w` |
| PS8 | `proper_suffix_witness` | Medium | 2 | `u <ₛ w → ∃ v, v ≠ [] ∧ w = v ⬝ u` |
| PS9 | `proper_suffix_witness_is_prefix` | Medium | 2 | `u <ₛ w → ∃ v, v ≠ [] ∧ w = v ⬝ u ∧ v ≤ₚ w` |
| PS10 | `proper_suffix_double_lt` | Medium | 2 | `u <ₛ v → v <ₛ w → u.length + 2 ≤ w.length` |

### Border (12)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| B1 | `border_is_proper_prefix` | Easy | 1 | `IsBorder b w → b <ₚ w` |
| B2 | `border_is_proper_suffix` | Easy | 1 | `IsBorder b w → b <ₛ w` |
| B3 | `border_ne_word` | Medium | 1 | `IsBorder b w → b ≠ w` |
| B4 | `border_empty_iff` | Medium | 1 | `IsBorder [] w ↔ w ≠ []` |
| B5 | `longest_border_length_unique` | Medium | 1 | `IsLongestBorder b₁ w → IsLongestBorder b₂ w → b₁.length = b₂.length` |
| B6 | `border_of_border_is_border` | Hard | 1 | `IsBorder b₁ b₂ → IsBorder b₂ w → IsBorder b₁ w` |
| B7 | `not_unbordered_iff_exists_nonempty_border` | Medium | 2 | `¬ IsUnbordered w ↔ ∃ b, IsBorder b w ∧ b ≠ []` |
| B8 | `not_border_of_length_ge` | Medium | 2 | `b.length ≥ w.length → ¬ IsBorder b w` |
| B9 | `border_of_prefix_suffix` | Medium | 2 | `u ≤ₚ w → u ≤ₛ w → u.length < w.length → IsBorder u w` |
| B10 | `border_nonempty_implies_length_ge_two` | Medium | 2 | `IsBorder b w → b ≠ [] → 2 ≤ w.length` |
| B11 | `border_period_duality` | Hard | 2 | `IsBorder b w → HasPeriod w (w.length - b.length)` |
| B12 | `border_imp_not_unbordered` | Medium | 2 | `IsBorder b w → b ≠ [] → ¬ IsUnbordered w` |

### Conjugacy (9)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| C1 | `conjugate_concat` | Easy | 1 | `(u ⬝ v) ~ (v ⬝ u)` |
| C2 | `conjugate_of_eq` | Easy | 1 | `u = v → u ~ v` |
| C3 | `conjugate_symm_iff` | Medium | 1 | `u ~ v ↔ v ~ u` |
| C4 | `conjugate_trans` | Hard | 1 | `u ~ v → v ~ w → u ~ w` |
| C5 | `conjugate_empty_iff` | Medium | 2 | `u ~ [] → u = []` |
| C6 | `conjugate_concat_rotate` | Medium | 2 | `u ⬝ v ⬝ w ~ v ⬝ w ⬝ u` |
| C7 | `conjugate_preserves_ne_empty` | Medium | 2 | `u ~ v → u ≠ [] → v ≠ []` |
| C8 | `conjugate_pow_rotate` | Medium | 2 | `w ^ (n + 1) ~ w ⬝ w ^ n` |
| C9 | `conjugate_pow_of_conjugate` | Hard | 2 | `u ~ v → u ^ n ~ v ^ n` |

### Period & Primitivity (10)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| P1 | `primitive_length_pos` | Easy | 1 | `IsPrimitive w → 0 < w.length` |
| P2 | `hasPeriod_of_short` | Easy | 1 | `w.length ≤ 1 → 0 < p → HasPeriod w p` |
| P3 | `isPrimitive_of_length_one` | Medium | 1 | `w.length = 1 → IsPrimitive w` |
| P4 | `minimalPeriod_unique` | Medium | 1 | `IsMinimalPeriod w p → IsMinimalPeriod w q → p = q` |
| P5 | `primitive_minimal_period_is_length` | Hard | 1 | `IsPrimitive w → w.length ≥ 2 → IsMinimalPeriod w w.length` |
| P6 | `pow_two_not_primitive` | Medium | 2 | `w ≠ [] → ¬ IsPrimitive (w ⬝ w)` |
| P7 | `hasPeriod_concat_self` | Hard | 2 | `w ≠ [] → HasPeriod (w ⬝ w) w.length` |
| P8 | `hasPeriod_mul_of_hasPeriod` | Hard | 2 | `HasPeriod w p → 1 ≤ k → HasPeriod w (k * p)` |
| P9 | `period_of_prefix` | Hard | 2 | `HasPeriod w p → u ≤ₚ w → p ≤ u.length → HasPeriod u p` |
| P10 | `hasPeriod_pow_length` | Hard | 2 | `w ≠ [] → HasPeriod (w ^ (n + 1)) w.length` |

### Morphism (12)

| ID | Name | Difficulty | Batch | Description |
|----|------|------------|:-----:|-------------|
| M1 | `morphism_cons` | Easy | 1 | `f •w (a :: u) = (f a) ⬝ (f •w u)` |
| M2 | `coding_preserves_length` | Medium | 1 | `IsCoding f → (f •w w).length = w.length` |
| M3 | `identity_morphism` | Medium | 1 | `(fun a => [a]) •w w = w` |
| M4 | `nonErasing_preserves_ne_empty` | Medium | 1 | `IsNonErasing f → w ≠ [] → f •w w ≠ []` |
| M5 | `uniform_pow_length` | Medium | 1 | `IsUniform f k → (f •w (w^n)).length = n · w.length · k` |
| M6 | `comp_nonErasing` | Hard | 1 | `IsNonErasing f → IsNonErasing g → IsNonErasing (compMorphism g f)` |
| M7 | `morphism_length_cons` | Medium | 2 | `(f •w (a :: u)).length = (f a).length + (f •w u).length` |
| M8 | `coding_comp_coding` | Hard | 2 | `IsCoding f → IsCoding g → IsCoding (compMorphism g f)` |
| M9 | `uniform_comp` | Hard | 2 | `IsUniform f j → IsUniform g k → IsUniform (compMorphism g f) (j * k)` |
| M10 | `morphism_preserves_proper_prefix_ne` | Hard | 2 | `IsNonErasing f → u <ₚ w → (f •w u) <ₚ (f •w w)` |
| M11 | `morphism_preserves_proper_suffix_ne` | Hard | 2 | `IsNonErasing f → u <ₛ w → (f •w u) <ₛ (f •w w)` |
| M12 | `border_preserved_by_coding` | Hard | 2 | `IsBorder b w → IsCoding f → IsBorder (f •w b) (f •w w)` |

---

## Difficulty Criteria

- **Easy**: Direct unfolding, single tactic (`simp`, `exact`, `rfl`), or one-step application of an existing library lemma.
- **Medium**: 3–6 tactic steps, may require `obtain`/`rcases` to destructure existentials, cross-module lemma chaining, or length arithmetic via `omega`.
- **Hard**: Multi-step reasoning across multiple modules, requires discovering and applying non-obvious lemmas (e.g., `List.append_eq_append_iff` for Levi), induction with non-trivial case analysis, or contrapositive arguments with algebraic reasoning.
