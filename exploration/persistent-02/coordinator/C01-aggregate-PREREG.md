# C01 — family-level comparison for new Q12 page coverage

Frozen before extension results are available. The question is whether any newly covered page is exceptional under the existing Q12 comparator construction after selection across the whole extension. Individual 1/20 ranks must not become global discovery probabilities.

Input: worker C's complete new eligible-page searches, with actual plus nineteen fixed-seed full-search comparators per page, each using the same k=2–4 objective. Old originals 0/17/55 do not count as new pages. No new decoding or null generation here.

For each page, take the twenty maxima over all k=2–4 seeds. Centre by their pooled mean and divide by their pooled population standard deviation (zero variance becomes all zero). This transform treats all twenty panel labels symmetrically. For each panel label j, take the maximum standardized value over pages. Compare actual panel j=0 with the nineteen matched composite panels: (1 + number of null-panel maxima >= actual maximum)/20. Also report raw per-page ranks and all standardized values. This comparison is conditional on the exact first-rune/equality-mask comparator model; it neither preserves full rune histograms nor demonstrates English plaintext. The synthetic panel construction must use independent recorded page seeds; if that fails, the pooled comparison is skipped with the exact reason.

Controls: tiny hand-calculated matrix; column relabelling invariance; tied/constant rows. Selection rule is fixed here; no trimming pages after scores are known. Store complete selected outputs from C, inspect leaders and alternatives, and rely on separate continuation rather than this coarse rank for a candidate.

Expected useful result: a leader worth continuation, or evidence that the apparent best page is ordinary relative to the family-level comparison. Simplest competing explanation: large finite seed fitting plus English scorer preference creates fragments. Changed scope: aggregate calibration of actual new coverage, not additional seed testing. Resources: one short Python job, no independent heavy computation while three workers run. Kill condition: incomplete or inconsistent per-page input prevents aggregate calculation; it does not block lane C.

Aiming bounds: recognizer is comparative score extremeness, not a solution detector; motivation is the confirmed Q12 coverage gap; finite scope is the new page set × twenty panels; conditionals remain seeds2–4, uninterrupted forward sum-feedback/sign-minus, frozen P03 rune/boundary English score. No general cipher exclusion follows.
