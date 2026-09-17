# An order-independent necessary bound for the proposed field object

Independent byte replay gives XOR148 for the pinned256-byte interpretation. This alone contradicts an **unweighted evaluation of a polynomial of degree at most254 over every element of GF(256)**. It is a sharper necessary condition than searching alternative point orders inside P16's degree223 format.

For the constant monomial, the sum over all256 field points is256·1=0 in characteristic2. For each exponent1..254, the nonzero points form a cyclic multiplicative group of order255; summing their kth powers gives zero because k is not divisible by255. The zero point contributes zero. By linearity, every polynomial of degree<=254 sums to zero over the full field. In an ordinary linear8-bit field representation, that sum is the bitwise XOR of the output bytes.

Reordering evaluation points does not change a sum. Changing the binary polynomial basis applies an invertible linear map, which cannot turn a nonzero sum into zero. Thus no such reordering or field-basis choice rescues this unweighted complete-field interpretation of these exact bytes. This is a proof of a specified format incompatibility, not an assertion that the artifact is random or that all error-correcting formats are excluded.

Column multipliers/weights, punctured codes, arbitrary nonlinear byte relabelings, another input interpretation, or corruption of even one byte fall outside this necessary bound. No correction or alternate data file was produced. P16's full32syndrome result remains the separate exact-format measurement.

The independent checker uses carryless multiplication directly, reproduces all32 actualsyndromes and256polynomial reevaluations, and checks all256monomial sums for the chosen implementation. Those finite checks validate code; the algebra above establishes the representation/order scope. The actual interpolant's degree255 leading coefficient is148, consistent with its nonzero sum.
