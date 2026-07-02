-- Note: This is a simplified, stripped-down version of the CoW library and is not complete.

import CoW.Word
import CoW.Factor
import CoW.ProperPrefix
import CoW.ProperSuffix
import CoW.Period
import CoW.Border
import CoW.Morphism
import CoW.Conjugacy
import CoW.Squares

/-!
# CoW — Combinatorics on Words  (LAMP_mini subset)

Root import file.  Import this to get the full mini library.

> **Note**: This is a reduced subset for the LAMP_mini reviewer package.
> The full library is in the complete LAMP repository.

## Module structure

| File           | Contents                                               |
|----------------|--------------------------------------------------------|
| `Word`         | `Word α`, monoid, length, power                        |
| `Factor`       | IsPrefix, IsSuffix, IsFactor                           |
| `ProperPrefix` | IsProperPrefix and properties                          |
| `ProperSuffix` | IsProperSuffix and properties                          |
| `Period`       | HasPeriod, IsMinimalPeriod, IsPrimitive                |
| `Border`       | IsBorder, IsUnbordered, IsLongestBorder                |
| `Morphism`     | applyMorphism (stub — 2 lemmas)                        |
| `Conjugacy`    | IsConjugate (stub — 2 lemmas)                          |
| `Squares`      | IsSquare (stub — definition only)                      |
-/
