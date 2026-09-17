# Independent P16 parity lemma check

The corrected256-byte artifact has XOR148, independently recomputed using eight separate bit-count parities and the pinned SHA256. No GF256 multiplication sweep was rerun.

Let F have256 elements. For k=0, sum over F of x^k is256 copies of1, hence0 in characteristic2 (constant monomial is identically1). For1<=k<=254, some nonzero a has a^k!=1: otherwise the nonzero polynomial X^k−1 of degree at most254 would have255 distinct roots. Multiplication by a permutes F, so S=sum(x^k)=sum((ax)^k)=a^k S. Thus(1−a^k)S=0 and S=0. By linearity, every polynomial degree<=254 has sum of its256 evaluations equal0.

Consequently nonzero XOR148 rules out this artifact as an unweighted complete evaluation vector of any such polynomial. Ordering the field points differently does not change the sum. An invertible F2-linear change of byte basis maps the sum to its invertible image and cannot make it zero. This argument applies to any GF256 field representation compatible with the declared linear byte coordinates; it does not require checking all irreducible polynomials.

For k=255 every nonzero x satisfies x^255=1 and zero contributes0, giving sum255 copies of1 =1. Thus for the unique degree<=255 interpolation polynomial, the leading coefficient equals the field sum of its values, consistent with stored coefficient148 in the chosen basis. The main exclusion needs only the nonzero sum, not interpolation computation.

No claim covers generalized column multipliers, a punctured/subsampled evaluation set, nonlinearly relabeled output bytes, damaged values, degree255 or a different artifact. Necessary-condition rejection is exact for the declared complete/unweighted model, not a generic Reed–Solomon/coding exclusion.
