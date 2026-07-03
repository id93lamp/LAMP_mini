import CoW.Word
import CoW.Factor
import CoW.ProperPrefix
import CoW.ProperSuffix
import CoW.Period
import CoW.Border
import CoW.Morphism
import CoW.Conjugacy

/-!
# CoW — Combinatorics on Words

Root import file.  Import this to get the full library.

## Module structure

| File             | Contents                                                 |
|------------------|----------------------------------------------------------|
| `Word`           | `Word α`, monoid, length, power                          |
| `Factor`         | Prefix, Suffix, Factor, IsFactorClosed                   |
| `ProperPrefix`   | Proper prefix definition and properties                  |
| `ProperSuffix`   | Proper suffix definition and properties                  |
| `Period`         | HasPeriod, IsMinimalPeriod, HasModularPeriod, IsPrimitive, IsPrimitiveRoot |
| `Border`         | IsBorder, IsUnbordered, longest border, border chain     |
| `Morphism`       | applyMorphism, compMorphism, IsNonErasing, IsCoding, IsUniform |
| `Conjugacy`      | IsConjugate, conjugacy equivalence                       |
| `Squares`        | IsSquare, distinctSquares, Fraenkel-Simpson primitives   |
-/