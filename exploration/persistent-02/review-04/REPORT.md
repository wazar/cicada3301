# Review04 — C07 variable-feature composite and H3 marked resets

Reviewed around2026-09-17 09:05–09:16 UTC. Fixed deadline remains16:15:06 UTC. Reviewer is independent of the implementation authors, not blinded to repository context. Only review04 files were authored. No actual C07/A07 search, reserved input experiment, producer edit, Git mutation or nested worker was performed. Five logged targeted runs passed, using venv/numerical threads1 and≤900s limits.

**Both implementations are cleared in their stated scope.** C07 passed variable-feature calibration and representative synthetic-book reconstruction. H3 passed independent exhaustive arithmetic, fixed-mark coordinate checks and a complete representative prefix/continuation panel. Short-control sensitivity and observed language-ranking failures still bound negative interpretations.

## C07: scope and calibration

The same seed-independent equality statistic is evaluated on45eligible F06 pages with k2..floor(N/20)−1, giving at least20runes/phase and411actual features. This reuses0/17/55 and section0–2 as a new statistic/unit, not new seed coverage or untouched validation. A contiguous segment of an uninterrupted recurrence has effective first-k seed values C−P, so independent per-page initial conditions do not assert a physical key reset; they relax cross-page compatibility.

For each page/k feature, all200panel values enter the pooled mean and population SD. All feature columns are then concatenated, and the maximum over the complete page/k set is taken for each common panel label. This treats the observed and comparator labels symmetrically even when different pages contribute different feature counts. A selected local page/k rank must not replace the global composite rank. It remains a conditional exploratory comparison against first-rune/equality-mask uniform strings, not a programme-wide probability or unique cipher identification.

The synthetic-book controls correctly replace the original49slot with the control's own length and feature count, and draw the other44units from their fixed templates. The planted book and its199comparator panels share those resulting lengths and constraints. These simulations measure the stated composite task rather than assuming that perfect716-rune control power transfers to short pages.

`check_c07.py` independently verified:

- All25frozen controls: source prefixes,20language/5uniform plaintexts, RNG stream, seeds and encryption.
-45eligible page identities, exact source ciphertexts,411features and minimum phase sample counts.
- Four complete200-panel matrices at lengths66/80/121/249, including an exact feature-count threshold. Independent direct recurrence, null draws, collision counts, denominators and standardization matched; maximum z discrepancy1.31e−14.
- A heterogeneous concatenated-feature fixture, whole-panel label reversal and a tied-max fixture; rankings matched independent calculations.
- All238,905registered local/book/actual RNG assignments are distinct, including background-baseline+900slots.
- Three fresh contiguous-slice effective-seed identities.

`check_c07_controls.py` then checked completed control00/01books:411and414features respectively. Reconstructed every45-unit baseline/source cipher and seed assignment, recomputed whole-book standardization/max/rank, and independently rebuilt all200-panel matrices for background slot0 and planted slot49 in both books, plus both separate local panels. All saved numerators/denominators/z values matched. Both local and composite ranks were.005. These are deliberately representative control replays, not a new25-book power study or an independent rerun of actual negatives. No actual C07 statistic was read or computed by this review.

Evidence: `c07-checks.json`, `c07-control-checks.json`, and synthetic fixture NPZ/JSONs. Early clearance was sent to C and the coordinator before actual scoring. The full author control panel must still supply length-appropriate sensitivity qualifications.

## A07/H3: exact marked-reset state

The reset rule is fixed before decoding: reset key position to0 immediately before the eight supplied whole-section major-mark sites (seven in body-only coordinates), retaining both scoring-context tokens. It does not reset at ordinary single dots or physical page/row joins. The same previously rotated periodic vectors/finite streams and two frozen scorers remain in use.

At a fixed input position, future behavior depends on current key position and the two scoring tokens. At a mark, collapsing old positions to0 while retaining context is therefore sound; keeping the best retained paths per new state preserves conditional n-best scores. Total normal-emission count is bookkeeping, not the post-reset key position. `marked_exact.py` maintains these separately. Finite exhaustion remains an error only if no legal path survives; an upcoming reset cannot repair an already impossible earlier rune. No state cap or global tie-census claim is introduced.

`check_marked.py` independently enumerated850cases/13,464complete paths.132correct finite-exhaustion rejections,717legal nondefault-context cases and259no-reset comparisons with the reviewed original exact decoder passed. Tests covered both signs, finite/periodic keys, starts, reset0/everywhere/subsets/none, boundary timing, consecutive F, zero-key aliases, all ties, fractional weights, empty input and retain1/2/7/16/33. Every returned score list and every retained plaintext/literal-mask/used/final-position tuple matched independent mask enumeration. Tied cutoff representatives retain the existing arbitrary-representative qualification.

`check_mark_coordinates.py` verified all eight crop hashes, page-to-section coordinate arithmetic, whole-to-body conversion and existing explicit boundary membership. Whole sites are[13,154,275,297,350,394,434,531]; body sites[141,262,284,337,381,421,518]. The reviewer separately viewed the native page1/line0 crop and observed the four-dot major mark among single-dot delimiters. This is not a new full-glyph transcription or independent reread of all30joins.

## H3 adapter and capability interpretation

Source review of `a07.py` confirms the selected key is frozen on the first physical-page prefix. Each retained prefix carries its **final position** and scoring context into a joint two-page suffix decode. Reset indices are shifted relative to the cut, including a reset exactly at the cut. This avoids the earlier greedy middle-page commitment. The resulting≤16prefix×16suffix collection is a bounded candidate set; it is not the whole-section global n-best set. Selecting a path using its suffix is retrospective path selection, not strict top1-prefix prediction.

`check_h3_plant.py` rebuilt all16frozen source cases, key-selection RNG draws, nearest-word-end scaled synthetic marks, literal masks, splits and source encryptions. Then every256retained paths of the716-rune P03 periodic Guest panel was independently checked: prefix/suffix/full re-encryption, final position versus total emission count, literal bits, context, direct full/suffix scores, winner metadata and truth membership. Maximum score discrepancy3.553e−15. All256paths have a carried position different from total-used modulo key length, so this test meaningfully exercises reset-state handoff.

The selected Guest key is correct, but its best complete path has3errors while truth is retained at rank2; the known-key joint diagnostic also prefers the same3-error alternative. This reproduces a scoring limitation rather than an arithmetic failure. Author subsequently reported all32plant/model cases complete with truth retained in32/32 and some additional rank2/3misses; this review independently replays the specified representative only. No model or threshold was changed to improve it. A was cleared to proceed to actual comparisons after its remaining capability checks.

Evidence: `marked-checks.json`, `mark-coordinate-checks.json`, `h3-plant-checks.json`. No scientific test failure was suppressed.

## Concrete next construction test, if selecting the next bounded lane

The next justified construction question is whether **A07's same fixed major-mark reset rule changes C05's normal-only literal-F sum-feedback behavior**, using one shared unknown seed across every segment. C04/C07's uninterrupted offset invariant does not cover such reset streams; A07's fixed-key clocks do not cover feedback. This is a specific gap exposed by the existing families, not a new key/model/format sweep.

The new state must retain the immutable initial seed (or its partial assignments) separately from the active normal-event history and seed phase. At each fixed mark, clear the active history/phase and reuse that same seed. Keep the score context; literal F remains nonconsuming and excluded from feedback history. Distinct original seeds cannot be merged merely because their current history/context agree: a later reset distinguishes them. Do not silently introduce independently free per-segment seeds.

Gate it with independently enumerated tiny seed×literal-mask cases, especially resets before allkseed components have been assigned, multiple resets, literal F around marks, finite initial phases, and inherited score context. Re-encrypt the existing frozen source plants with their same seeds/masks under the new reset rule; marks use the already-fixed A07 synthetic layout mapping. Begin a measured resource pilot at existing k2, then attempt existing k3 only if exact state/memory cost is practical. A guard must stop rather than prune, and any relaxation needs an explicit bound. No automatic k4+expansion.

If that instrument is sound and useful, use the same body reset positions, same two scorers and existing F-site/equality comparators. Preserve the uninterrupted C05/C06 outputs as paired baselines and distinguish unknown-seed full fitting from prefix-selected continuation. This tests a new transition relation with a source-backed clock; it does not establish that the reset interpretation is intended. The current source-motivated H3 remains the third/final procedural rule, not a pretext for further punctuation variants.

## Reproduction

Every execution is in `runs/*/command.json` with exact command, source snapshots/hashes, raw output, numerical-thread overrides and outcome. Scripts are `check_c07.py`, `check_c07_controls.py`, `check_marked.py`, `check_mark_coordinates.py`, `check_h3_plant.py`. Example:

```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-04 --label H3-independent --seconds 900 --input exploration/persistent-02/section/marked_exact.py --input exploration/persistent-02/section/A07-PREREG.md -- .venv/bin/python exploration/persistent-02/review-04/check_marked.py
```

The logger refuses work after the fixed deadline. Review completion does not end the eight-hour research assignment.
