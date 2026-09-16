# Detector audit C-010–019

The legacy detector finds the right key in a small independent blinded search and accepts all40 fresh ordinary-English positive instances, but it does not certify complete plaintext recovery. It rejects all20 continuous-key instances at its fixed reset interface, and two unsupported skip-by-two instances receive PASS despite substantial rune errors. The R19 pair decoder repairs that transition in our bounded positive probes. These statements concern synthetic data, not the unsolved puzzle.

## Scope and reproducibility

Agent C owns this directory only. Baseline396001a9ce55e0e85ddef19e405afc6a13954588; assigned working tree95e11e918ace77a51de4b612a48e74c298e67e58. Exact executed source/data hashes and Python version are in `manifest.json`; commands/exits in `commands.json`. No inherited code, thresholds, or input changed. No puzzle search ran. `checks.py` supplies a fresh authored prose fixture, independently written alphabet parser and encryptor, and three hand-calculated arithmetic examples (normal, one-draw rejection, two-draw rejection). The initial mapper mistakenly removed spaces before greedy digraph parsing; its assertion caught this before the pilot, and the audit mapper was corrected. Main encryption never calls the inherited plant.

`MATRIX.md` was frozen after `pilot.json`, before main results/ranking. Main batch took10.20s. Full raw per-choice scores, exact matches, rune-index recovery, decoded length, actual key-use positions, seeds and final acceptance are in `raw-results.json`. Seeds reproduce ciphertext exactly; fixture and key length2048 are pinned in code. Two different page windows are fixed;20 RNG replicates are **not20 independent language corpora**.

## Measured capability

| Construction / register | Length per page | Correct-key instances | Legacy final PASS | Selected exact pages | Mean selected rune recovery |
|---|---:|---:|---:|---:|---:|
| Reset, one-draw rejection .83, English |60|20|20|40/40|1.0000|
| Reset, one-draw rejection .83, English |120|20|20|39/40|0.99979|
| Continuous key, one-draw rejection, English |120|20|0|19/40|0.51938|
| Reset, skip-by-two rejection, English |120|20|2|1/40|0.36375|
| Reset, one-draw rejection, vowel-removed English |120|20|0|0/40|0.21354|

Every instance has two pages. Each page selects the best of rigid/beam and signs±1; beam400, max_skip3, offset0. Scores and recovery of all four choices are retained, not just winners. English prerequisite failure is necessarily final oracle rejection; candidates satisfying it also received the production200-shuffle null and .5 margin. This tests the judging functions and production decision formula on fresh synthetic segments, **not** the CLI trust-anchor and pinned-real-input hash path.

For each main length,100 varied random wrong keys and three structured controls (constant13, periodic0..28, one-position shifted true key) were rejected. Complete selection and two-page rule were replayed on every negative; no narrower null was substituted for this empirical false-accept count. Constant and periodic keys are descriptive controls, not independent trials. With0/100 varied-key acceptances, the one-sided95% binomial upper bound is2.95% **per length and this fixed ciphertext**; a billion-trial guarantee does not follow.20/20 sensitivity has two-sided95% binomial lower bound83.16%, conditional on this key distribution and fixed text.

The correct-key L120 seed51002 page0 differs by one rune yet passes. More seriously, skip-by-two seed51000 passes both pages at selected recoveries74.17%/75.83%; seed51002 passes at99.17%/65.00%. A score PASS is a candidate flag, not certification. Unsupported transition constructions must stay unsupported; occasional scores above threshold do not validate their recovery.

When supplied the independently recorded correct page-start key offsets, the legacy beam recovers99.979% of continuous-case runes; its public oracle interface never supplies those offsets. This comparison isolates reset-model loss. An offset scan is **not** calibrated here.

Vowel-removed truth itself scores−7.6002 and−7.4742, below−5.5. Correct sign/beam recovers68% on average, with2/40 pages exactly right yet rejected; the English-selection step lowers selected recovery further to21.35%. This separates a scorer blind spot from decoder path-selection errors. No broad language-coverage claim is made.

## Calibration discrepancy

For each length,100 independently shuffled two-page ciphertext pairs were evaluated through all four choices on both pages. Shuffles preserve page lengths and histograms but destroy adjacency and the anti-repeat structure; varied wrong-key trials above preserve the exact ciphertext, including its repeats.

| Length | Max narrow beam/-1/page0 | Max full selected page | Mean selection lift | Full selected greater than narrow |
|---|---:|---:|---:|---:|
|60|−6.59006|−6.49274|0.32021|77/100|
|120|−6.84619|−6.69064|0.20949|77/100|

This executes the C-015 mismatch rather than assuming its magnitude. Full selected second-page statistic is also saved. These are descriptive paired nulls, not a replacement extreme-tail fit. `threshold_for(10**9, segment_len=L)` returns exactly−5.415752407880083 for L1,31,60,120,400,12956 and None: C-016's parameter is operationally unused.

## Version and caller map

| Tool / exact hashed source | Executed here | Scope / callers |
|---|---|---|
| `liber-primus/verify_solution.py`, `analysis/campaign18_skip/skipdecode.py`, `src/lp/score.py` | selftest; independent plants; full signs/decoders/pages selection | Oracle directly imports legacy skipdecode. Actual dispatch probe shows offset0 for both pages and only beam/-1/page0 in shuffle null. |
| `liber-primus/analysis/round19/I1/driftbeam.py` pair preset |40 correct-key skip-by-two page decodes | pair=keyskip2,max_skip8,max_free0,lam0,start_slack0.39/40 exact,99.979% rune recovery. No new R19 wrong-key/FPR or permissive-drift calibration claimed. |
| `liber-primus/analysis/round19/I2/adjudicate.py` | actual Panel load attempt | Blocked: `models/panel.npz` absent. No rebuilt training data/models, power or speed rerun. |
| R20 `S-G3/sweep.py`, R21 `L3-py27-reducers-plus-64bit-map/sweep.py` | import/caller inspection only | Both explicitly import driftbeam, adjudicate, hitfn20. Later adoption is distinct from legacy oracle; no blanket retroactive validation. |
| R21 `L1-seal-realmode-proxy/{audit_catch.py,hitfn21_folds.py,catch_surface.json}` |15-cell saved-table arithmetic | Best genuine-safe tuning catch36/45=.80; held-out54/66=.81818, false-reject4/24=.16667. Not a fresh population regeneration. |

The missing I2 model blocks a present end-to-end multi-register/R21 executable validation; the saved arithmetic supports consistency of its stated failed seal, not independent reproduction of the underlying population. Permissive drift settings, arbitrary offsets, low-entropy keys, other languages and large-trial thresholds remain outside this measured capability.

## Claims

* C-010 reproduced narrowly: inherited selftest returns0, accepts its planted key and rejects its constructed wrong key. `oracle-selftest.stdout.txt` preserves the output. Fresh independent plants support a wider but still finite scope above.
* C-011 executed: legacy4096-symbol wrong key has one unique symbol27; persistent-RNG control has29 unique symbols. Varied negatives were measured separately.
* C-012 supported by actual call tracing and continuous/reset controls; per-page or continuous interfaces are not silently credited to the oracle.
* C-013 supported by independent one-draw/two-draw tests; legacy rejection relation is insufficient for general skips.
* C-014 supported for this vowel-removed fixture, including two exactly recovered correct-sign pages whose English score fails. Other inherited language power values were not rerun.
* C-015 measured selection discrepancy, with full-procedure negatives and narrower production null explicitly distinguished.
* C-016 executed length invariance. Historical constants' universal tail validity remains unsupported.
* C-017 partial independent support for pair-mode repair only. The historical20/20 gates and2000/4000 wrong-key rates were not reproduced.
* C-018 blocked new execution by missing model. Retain source-checked/historical status; do not promote claimed27-cell power or speed measurements.
* C-019 arithmetic of retained records reproduced; seal's causal/population experiment remains historical and not independently regenerated.

## Blinded search

Coordinator supplied eight candidates and two120-rune pages from an independent encryptor after handchecks. C froze descending second-best page score, then best score, then ID before ranking. Every sign/decoder choice was tested at offset0; no search tuning. Ranking SHA256 `7917dc1f6db49ec85f086334291dbec4cb0ad13597f80665096432ee00e30e71` was sent before answer reveal. Candidate6 ranked first (second page statistic−4.34124; runner-up−7.15855). Reveal identified candidate6; post-reveal measurement found240/240 exact runes. See `blind-ranking.json`, `lightweight.json`, and coordinator commitment/reveal records. Shared filesystem gives procedural separation, not strong access isolation. This is one successful8-candidate search, not an estimated search-success rate.

## Smallest defensible next setup

The tested legacy reset/sign/beam400/max_skip3/two-page L120 setup can flag ordinary-English candidates. It cannot certify exact plaintext or support general negative conclusions. For a proposed small clue-derived key dictionary, freeze the exact candidate set and reduction first, pass fresh plants using those actual candidate keys, then calibrate the **whole candidate-set maximum** with matched ciphertext/wrong-key trials before touching LP2. Our100-single-candidate negatives do not calibrate an8-candidate maximum. Preserve all candidate rune outputs and require independent follow-up of any flag; stop at the frozen bound, without adaptive dictionary expansion. No new puzzle experiment has run, and current evidence alone does not justify a broad reopened search.
