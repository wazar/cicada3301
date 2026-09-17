# N17 — single adjacent-swap damage sensitivity

**All769single adjacent-unequal swaps destroy exact cyclic-BWT membership in these four valid control carriers.** No actual page was modified, searched for repairs, or reinterpreted. This is a detector fragility measurement, not evidence that actual transcription errors exist.

| Existing P31 control | Runes | Adjacent-unequal swaps | Format compatible | Original necklace retained |
|---|---:|---:|---:|---:|
|welcome|515|386|0|0|
|jpg107-167|319|223|0|0|
|p56|85|75|0|0|
|p57|95|85|0|0|

The complete frozen P31 all-primary parser was used, without a row0 shortcut. Every primary-row candidate, group, forward column and alias mapping is retained. All changed inputs preserve length/inventory and differ only at the named adjacent pair. No circular end-to-start swap or equal no-op was included. Stable BWT output-to-original-source rune/character maps are retained; repeated-row ties use original start index, not a claim of unique physical origin for indistinguishable symbols.

## Exact structural explanation

All four carrier inventories have gcd1 across symbol counts, and each baseline LF permutation is a single cycle. An adjacent swap of two unequal symbols changes neither cumulative counts nor either symbol's occurrence rank relative to its equal copies; it simply exchanges the two corresponding LF outgoing destinations. Exchanging two outgoing destinations within one cycle splits it into two. structural.json independently checks that exact permutation identity and the two resulting cycle lengths for every one of the769swaps.

Any valid cyclic BWT with this same gcd1 inventory would have to arise from a primitive source word: a k-fold periodic source with k>1 would make every symbol count divisible by k. Primitive cyclic rotations are distinct, and LF maps each rotation to its one-symbol predecessor, forming a single cycle. The swapped two-cycle LF is therefore incompatible. This explains the uniform result exactly; the769cases are not independent probabilistic trials and no pvalue or general error-rate estimate is claimed. Periodic carriers with nontrivial count gcd need not obey this conclusion.

Original-source necklace retention is necessarily zero even independently of that cycle argument: its forward transform remains the original column, which differs from every unequal-swap input. A different compatible necklace could in principle survive another kind of damage or another carrier; none survived these frozen cases.

## Verification and scope

Independent no-production-import replay uses Psi forward inversion and fixed-width base32 integer rotations/numeric sorting. It verifies all769inputs,284,377primary candidates,266,751necklaces, complete forward columns, all validity flags and source-coordinate swaps. The exact inventory/no-op/circular exclusions and original-source maps all pass. The full source and parser hashes are retained in inputs.json. No data or source edits were made to P31.

First20pilot swaps took1.714seconds and524,986compressed bytes, forecasting65.9seconds/20.2MB. Completed production took41.39seconds including reused pilot outputs; arrays total13,537,070bytes. Every scientific batch passed without repair or timeout. Full independent replay and structural diagnostic logs are retained. Storage is deliberate evidence retention rather than a search expansion.

Decision: P31's three actual misses remain exact-format misses and cannot by themselves exclude a damaged BWT format. This experiment supplies no reason to posit damage in those actual pages and authorizes no repair search. Freeze this control sensitivity; no new alphabets, routes or compression stages.
