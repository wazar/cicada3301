# Review70 — S20 scoped PASS

Independent reconstruction verifies41,062 source words,236,243 normalized rune identities and every half-open raw-character span. Caesar's pinned clean body/exclusions and Virgil I/IV/VII/X heading boundaries agree; normalization remains greedy canonical GP within each ASCII word, including declared aliases, never across word edges. S19's four prefix source/maps also match. UTF-8-sig decoding preserves the existing raw-character coordinate convention.

All45 F06 pages and their2,355 explicit word-length-minus-one payload symbols were rebuilt. Distinct support is exactly14. Independent per-symbol cumulative-presence arrays reproduce every one of224,473 full-window support counts without importing s20 or using its sliding histogram/last-occurrence algorithms.

| Source | Windows | Minimum support | Maximum support | Minimum offsets |
|---|---:|---:|---:|---:|
|Caesar clean|118500|23|26|3540|
|Virgil I|24829|25|27|355|
|Virgil IV|23223|24|27|416|
|Virgil VII|27201|24|27|930|
|Virgil X|30720|25|27|4205|

All histograms, minima/maxima, minimizing offsets, endpoint character spans and empty support14 candidate lists agree. Direct set checks additionally cover9,456 minimizing/endpoint offsets. Seed632020 reproduces all five bijection controls; the full14/15-symbol synthetic sequences classify correctly. Independently counted22,862 tiny panels agree using bit-set support versus direct sets.

The mathematical obstruction is exact: a bijection preserves the number of distinct symbols, so none of these windows can equal the full14-label payload. It is conditional on one shared bijection, fixed2355length, these five normalized contiguous streams and their frozen ranges. It does not exclude Latin, paraphrases, different sources, assembled excerpts, alternate registers, nonbijective maps or other payload roles. Windows may cut normalized words; Caesar concatenation retains its already excluded-heading gaps. No additional source/window was introduced.

P04/CARD.md was inspected: it studies a common many-to-one rune-to-consonant count map across five page-specific window sets after vowel deletion, including shared-support joins and integer count equations. S20 shares the support-invariant idea but changes source units, normalization, window family and bijection premise. It is a narrow adaptive follow-up to S19's support mismatch, not a claim of universal methodological novelty or independent language evidence.

Logged run `20260917T031649.378041Z-review70-source-support` exited0 in0.775seconds. All snapshotted input hashes remained unchanged. No failed audit attempt, production import, optimizer/search rerun, reserve/image/Git operation or source expansion occurred. No defect or candidate found; S19's prior scorer result remains separate.
