import CoW.Factor

open CoW

variable {α : Type*}

lemma prefix_of_factor_is_factor {u v w : Word α}
    (h1 : u ≤ₚ v) (h2 : v ≤f w) : u ≤f w := by
exact IsFactor.trans (IsFactor.of_prefix h1) h2
