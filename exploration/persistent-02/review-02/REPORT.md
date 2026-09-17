# Review02 — posterior, invariant, continuation forest and publication recipe

Reviewed 2026-09-17 around 08:47–08:56 UTC, within fixed deadline16:15:06 UTC. Reviewer is independent of these implementations' authors, but not blinded to their outputs or previous work. Only this review directory was authored. No reserved-page experiment, source/input edits, Git mutation or nested workers. Scientific executions used the shared logger, selected venv, numerical threads1 and caps≤900s.

**Algorithm decision: no arithmetic blocker found in B07's partition/marginals, C04's phase-collision invariant/statistic, or the bounded continuation forest. C04 actual scoring is cleared under its preregistered conditional interpretation.** One reproducibility defect was found in the original forest summary script, corrected by the coordinator and independently verified. It affected rerun counts/control labeling, not the validated forest arrays or the previously saved original summary. See below.

## B07: sum-product and uncertainty claims

`decoder/posterior.py` uses the same sufficient state as the fixed-key optimizer: key phase/finite position plus two scoring tokens at each ciphertext index. Each legal ordinary/literal choice remains a separate DAG edge even if emitted rune and destination state coincide. Forward log-sum-exp aggregates path weights and counts; backward values contain precisely the remaining score. Multiplying forward/edge/backward factors and dividing by the partition produces whole-text branch and join marginals. Terminal states receive zero suffix score; finite dead-end prefixes receive zero full-context mass. Prefix-only calls instead truncate the DAG, correctly omitting future evidence.

`beam_pool` retains the entire terminal width-limited path pool. `mass` sums precisely those decision-path weights relative to the full partition and rejects duplicate literal masks. Its output is not the mass of only the old function's returned top16 unless that subset is explicitly supplied. Distinct paths yielding the same plaintext are intentionally distinct. Model-induced weights conditional on one fixed key are not calibrated plaintext confidence or a posterior over keys. Underflow and tiny normalization roundoff remain disclosed qualifications.

`check_posterior.py` independently enumerated650 fresh packets:487legal,163exhausted,6,275complete legal paths. Cases covered both signs, periodic/finite modes, arbitrary starts and score contexts, fixed delimiters, consecutive F, zero keys/aliasing, score ties, empty input, negative weights down to thousands, and finite dead ends. Independent stable full-path sums checked the partition, every F branch marginal, every cut's state/position distribution, separate prefix-only distributions, and beam widths1/3/64 as weighted legal subsets. Maximum partition/branch absolute discrepancy was1.819e−12. Evidence: `posterior-checks.json`; all checks passed.

Representative replay independently reran both fixed models on the already-selected Mill1 and Shelley2 continuation examples. Complete B07 outputs matched saved records except runtimes, including full terminal beam pools and hashes. Mill1 rune514 literal weight changes .9556069975→9.79596e−125 under P03, .9152446677→3.64942e−190 under the complementary model. Shelley2 rune498 remains .8154031901 / .8678101174 after continuation. Thus Mill's full-context revision and Shelley's persistent scoring error reproduce. This is a selected consequential-example review, not a fresh population-level power estimate. Evidence: `posterior-source-checks.json`.

## C04: seed-independent phase collisions

For period m=k+1, any two valid decodes differ by a constant shift within each index phase. Equality of two runes in the same phase is invariant under that shift; therefore the ordered-pair collision numerator and phase-size denominator are invariant. This detects phasewise distributional nonuniformity, not semantics or a unique cipher. The optimized running-window baseline matches the direct recurrence; the reviewer additionally used the independent difference recurrence q[i]=q[i−m]+C[i]−C[i−1] after initialization.

The family statistic pools all200 panel labels symmetrically for each period's mean/population SD, then takes the maximum over the same33 periods for every label. The plus-one tail rank is computed from those200 maxima. This correctly calibrates the stated within-experiment conditional family comparison; it is not a programme-wide discovery probability. k2..34 gives at least20 observations per phase at length716. Null streams preserve the first rune and complete adjacent equality mask by construction.

`check_invariant.py` passed36 fresh algebra cases spanning k2/3/5/8/17/34 and lengths from1 to716. Checked the direct recurrence, independent difference baseline, constant phase offsets, invariant numerator/denominator, and explicit ordered-pair enumeration on small packets. It independently reconstructed all20 frozen control plaintext/seed/RNG sequences and encryption, plus the frozen source-packet hash.

Three complete saved control panels were rebuilt independently: Guest k3 (`control00`), Blake k34 (`control15`) and uniform k3 (`control16`). For each, every one of200 ciphers×33 periods was checked: comparator RNG values, every phase histogram including padding, numerator, denominator, fraction, pooled standardization, selected period and maximum-family rank. Whole-panel label reversal preserved equivariance. Ranks .005/.005/.51 reproduced. This totals19,800 histogram/period reconstructions. No actual collision result was scored or read for clearance. Evidence: `invariant-checks.json`; run completed in214.81s. The slower independent histogram implementation remained within its900s cap.

## B04/A05: frozen complementary source preparation

All four complete training spans were checked against source file hashes, recorded byte-character spans, first1000 lexical matches, every word coordinate, greedy rune mapping and end position. Source starts/end excerpts were inspected: Emerson Self-Reliance, Poe Tell-Tale Heart, Plato/Jowett Republic and Melville Moby Dick body prose. Recorded excerpts contain neither Project Gutenberg boilerplate nor picture markers. Training paths are disjoint from Guest/Mill/Shelley/Blake control paths; LP texts are absent. Full records are in `posterior-source-checks.json`.

This verifies the frozen recipe and targeted cleanup claim, not an independently sampled language corpus. Both corpus and lexical/rune boundary preprocessing differ from P03. The preexisting Blake authorial headings and control endpoint qualifications are not removed by this review.

## A04/A05 bounded continuation forest

`section/forest.py` keeps at most16 prefix×16 middle×16 final conditional paths. The final cache key retains absolute used-key count and scoring context, so it is sufficient for finite keys and conservative for periodic keys. Continuous mode carries the absolute count; page-reset resets only the key count while preserving the score context. `a02.Finite` converts the new decoder's relative `used` count back to the absolute convention expected by the old adapter. No global completeness follows from the bounded earlier-stage alternatives.

Independent `check_forest.py` checked six representative panels and14,432 complete paths:

- A01 circumference reference, page-reset:2,048paths.
- A02 WELCOME, continuous:4,096paths; truth survives prefixrank2.
- A02 AN END, continuous:32paths; truth survives middlerank2.
- A05 finite PARABLE, page-reset:64paths.
- A02 actual body, continuous:4,096paths.
- A05 periodic actual whole, page-reset:4,096paths.

Checked source hashes, prefix-selected key metadata, contiguous spans, complete path provenance, distinct-plaintext counts, literal bits, finite/periodic re-encryption under each clock, independent exact final conditional scores, full-string direct scores, suffix-only direct scores, and selected rank metadata. Every tested control truth remained in its forest. Maximum full-score discrepancy was1.155e−14. Evidence: `forest-checks.json`.

Full-score and suffix-only selection are correctly separate. In the A05 actual whole/reset panel, suffix selects prefixrank8 while the full objective selects prefixrank1; the audit reproduces both. A suffix-selected prefix is retrospective selection using continuation and must not be called an untouched prefix prediction. No broad replay of the629,000-path negative panels was needed.

### Reporting defect, corrected and verified

`section/summarize_forest.py` at source SHA256 `6b07d538b8498f6d0ed169d05de700aaaf193677fda4bf496cd004422aace4cf` scans all `A04/*.json` without filtering batch. After A05 files were added, rerunning it mixes P03 and complementary records into `counts` and `controls`, while its actual result loop still selects only A01/A02. The saved original summary was produced earlier and correctly reports176panels/629,000paths; an unfiltered rerun sees352panels/1,258,000paths. `summarize_a05_forest.py` already filters its own group.

Fix requested: filter original summary records to batches A01/A02 before aggregation and regenerate it. Reviewer did not edit author code. This is a reproducibility/reporting defect, not a failure of the tested forest arithmetic or the original saved counts. `summary-scope-check.json` and its logged source snapshot preserve the finding. Owner was informed immediately.

Coordinator then applied the explicit A01/A02 filter and reran the summary. `check_summary_fix.py` independently checked the actual AST guard,176/629,000 counts in the mixed352-panel directory, and SHA256 equality of both regenerated summary and leading-output text against their original recorded hashes. All passed. Corrected source hash is `8c4f2ab6b5382f34a60b8547ce8c38cb76024254aa0548d97c63a39f2c5ca37b`; evidence `summary-fix-check.json`. No scientific search/input/result changed.

## Lossless publication recipe

Reviewed `coordinator/reconstruct_q12_null.py`: source/model hashes and metadata hashes are pinned before pure arithmetic reconstruction; it never calls the original writer/search/guard, refuses output overwrite, and verifies shape/dtype/raw-C-byte hashes for all nine arrays. A representative `actual1-null00` reconstruction passed all checks. Independent comparison with the unchanged original local archive verified every six retained arrays byte-for-byte plus all three reconstructed score-array hashes. Original archive hash stayed unchanged. Evidence: `reconstruction-checks.json` and `reconstructed-actual1-null00.npz`.

This supports raw-array losslessness on the recorded runtime. Zip-container byte identity is neither required nor claimed. Hash checks fail closed if a different numerical environment changes reconstructed raw bytes. The large redundant original null archives need not be published when exact inputs, version-pinned recipe and verified array hashes are published.

## Reproduction and review scope

All eight logged runs passed; no algorithm/harness failure was suppressed. `runs/*/command.json` contains complete commands, source snapshots/hashes, numerical-thread environment, stdout/stderr and runtime. Main reviewer scripts are `check_posterior.py`, `check_invariant.py`, `check_posterior_sources.py`, `check_forest.py`, `check_summary_scope.py`, `check_summary_fix.py`, `check_reconstruction.py`. They write only review02 outputs. Example:

```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-02 --label posterior-independent --seconds 900 --input exploration/persistent-02/decoder/posterior.py -- .venv/bin/python exploration/persistent-02/review-02/check_posterior.py
```

The fixed deadline is not extended. This review certifies the specified targeted checks and qualifications, not every ordinary negative, model interpretation or an intended Liber Primus plaintext.
