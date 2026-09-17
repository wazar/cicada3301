# Review71 — S21 exact error-mass bound

Scoped arithmetic PASS, with one input-metadata hash discrepancy retained below. Independently authored occurrence-position/searchsorted counts reproduce every one of 6,509,717 symbol counts across all 224,473 windows. Summing the fifteen smallest counts independently reproduces every lower bound. All support counts, minima, maxima, minimizing offsets, complete minimum count vectors and raw source spans agree. The complete source object is hash-identical to independently reconstructed review70 inputs; this review did not repeat raw source normalization.

The five minima are 119, 163, 149, 152 and 149 errors per 2355 positions. The overall minimum is 119/2355 = 5.05307856%. Any output using at most fourteen types can match only positions belonging to its chosen types; the maximum possible such mass is the fourteen largest source counts. Thus this is a lower bound even after granting arbitrary ordering. It is not an attainable substitution alignment, an approximate plaintext, or a language-wide exclusion. Only the same five finite source streams/windows are covered. Review70 already establishes actual fourteen-type support and its source-normalization scope.

All 768 tiny controls were independently checked by enumerating every subset of size AT MOST the cap, including empty subsets; explicit projections attain the relaxed bound. No S21 module was imported. No scientific search was rerun or enlarged.

The first logged audit failed on the S21-pinned metadata file S20/inputs.json: recorded ccc04fcb1a4633109e3d6de3ec50367e7c460e5d4c28fb3e32a8ee116120a9b7 versus current 1f2859c72bad5a362e398769b1dbb80a80768b126bb50de4afa91e5daf37956c. All other S21-pinned files match, including actual sources and support arrays. The audit was changed only to record and explicitly permit this sole metadata discrepancy, then passed in 0.422 seconds. Cause is pending coordinator confirmation; it does not change numerical replay, and provenance consistency is not asserted. Both logs and snapshots remain. No author scientific outputs were edited.

Inputs/result/script and the complete run logs are retained here. Report finalized before the research deadline; no new hypothesis or source expansion.

## Metadata resolution

Coordinator publication redaction explains the discrepancy. The retained private original hashes exactly to the S21 pin. Replacing ONLY the checkout prefix with `<REPO_ROOT>` reproduces the published bytes exactly; all embedded source hashes are unchanged. `metadata-resolution.json` records both digests. This resolves the provenance caveat without rewriting S21 pins or concealing the initial failed check.
