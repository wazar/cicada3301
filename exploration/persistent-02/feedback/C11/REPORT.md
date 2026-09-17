# C11 — literal F included in emitted-plaintext feedback history

This tests a material transition alternative to C05. Literal F emits plaintext0 and does not consume a seed entry, but enters feedback history. Normal seed phase counts only normal emissions; after k normal emissions, each next normal key sums the last k EMITTED runes including literal Fs. k2/3, no resets, same section and two frozen language objectives. Literal plaintext F is established in solved examples; its intended relationship to hypothetical feedback remains unestablished.

The exact state keeps normal seed phase, emitted-history length/content and explicit language context separately. History can fill before seed phase completes. No score-context compression or approximate pruning is used. Consumed seed values need not remain in future state because this construction has no resets. Exact snapshot/recomputation restores seeds/masks/full outputs. Retained alternatives are selected final-state representatives, not global n-best. Unused seed suffixes are recorded as unspecified aliases.500000-state/30-second refusals are unresolved; the post-allocation state guard is not a hard memory cap.

Author tests:64 complete seed×mask cases plus90 fixed-seed carried-state cases. Fresh A review:170 independent exhaustive cases including history filled before seed completion, arbitrary score contexts/boundaries, block1/4 equality and resource refusals. All32 plants independently reconstructed from C05's frozen source truths/seeds/literal masks with only the ciphertext re-encrypted. All64 opposite-construction known-seed/mask error measurements independently checked. P03 representative plant outputs and actual adapter also reviewed. Evidence section/review-feedback/emitted-review.json and emitted-plant-review.json.

Scalar distinction: seed[1,2], plaintext[3,4,0,5], literal at2 gives new ciphertext[4,6,0,9], versus old excluded-history[4,6,0,12]. On the32 full controls, supplying the correct seed and literal mask but the wrong construction gives rune errors in31/32 cases in both directions. The no-literal control is identical. Thus earlier excluded-history negatives do not cover this test.

P03 selected exact plaintext28/32. The four misses are controls9/20/22/30 with1/1/2/6 rune errors and truth score deficits .6031942799/1.2528996906/1.3401056801/.0056294134. Truth is feasible; these are ranking errors after exact optimization, not missed maxima. Max25230states in controls. Complementary control results and actual runs pending.

Complementary controls completed31/32 exact, fixing P03 misses9/22/30. Control20 has one-rune error and truth deficit1.4615590576; source truncation/terminal-word qualifications remain as previously frozen, with no fixture repair or terminal diagnostic. Both32-control runs complete with no refusal. Actual20-panel P03 full/prefix/continuation run began after these measurements and A clearance.

Seed-identification qualification: coordinator's independently reviewed fixed-mask influence diagnostic shows emitted-history feedback can lose influence of the original seed in its ACTIVE history after literal Fs. Once mature active-history coefficient rank is zero, future output is independent of the original seed for unchanged future mask/cipher, even though different seeds generally produced different EARLY plaintext. For a fixed complete plaintext and fixed mask with at least k normal emissions, the first k normal C−P values determine a unique seed. Rank loss therefore merges different early seed/plaintext histories into the same future state; it does not create additional seed aliases for that fixed complete output. The engine's `unspecified_seed_completions` counts only never-consumed seed slots. This distinction limits identification from continuation alone but does not invalidate exact complete-path scores or unchanged continuation. See coordinator/emitted-seed-influence/.

## Actual results

All240 actual fixed-scope solves completed (2models×20panels×2k values×full/prefix/tail), without resource refusal or timeout. Each full/prefix optimization integrates every k2/3 seed and legal literal mask through exact state maximization. Future masks are optimized after carrying the prefix-selected seed/path/history/context unchanged; the continuation family picks k using prefix score only.

| Model | k | Full matched rank | Per-k continuation rank |
|---|---:|---:|---:|
| P03 |2|.80|.35|
| P03 |3|1.00|.95|
| Complementary |2|.90|.70|
| Complementary |3|1.00|.95|

Both models give full-family rank1.00 and prefix-selected-k3 continuation rank.95. The actual full-family maximum lies below every one of the19 matched null maxima. All eight complete full/continuation leaders were read; none is coherent plaintext. Full alternative paths and exact seeds/masks remain available, with no solution-verification claim.

P03 actual wallwork109.529seconds, complementary109.692seconds; maximum24389states and149110784process RSS bytes. Rankings use the already-frozen/reused B packets preserving literal-F sites and adjacent equality masks, not independent new confirmation. Numerical exactness concerns the specified local float64 scoring order, not a claim of interval-certified real arithmetic.

The result bounds the emitted-history/nonconsuming-F construction at k2/3 without resets on this716-rune body under these two measured language objectives. It leaves different constructions, registers and sections untested. It supplies no reason to increase seed lengths automatically. The parallel F-free-run invariant is the next distinct check of this recurrence scope without relying on language scores; original C05 excluded-history findings remain separately preserved.

Parallel result received after completion: decoder/f-free-invariant/REPORT.md derives an English-free phase-collision invariant inside sufficiently warmed ciphertext-F-free runs, valid for both literal-history conventions without assuming physical resets. Its16 matched fresh716-rune k2/3 plants all ranked1/20, while actual family rank was19/20 (.95), with no collision excess. That independent objective adds a measured bound; it does not convert either language-score negative into a universal cipher exclusion.
