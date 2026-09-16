# OVERNIGHT-01 independent review

No retained output reviewed here warrants a claim of credible new Liber Primus text. Independent forward arithmetic reproduces the retained candidates; it does not validate their interpretation. No candidate qualified for fresh image-symbol transcription or a frozen-rule reserved-page reveal. None of the ten reserved originals was decoded by this reviewer, and scored-row coverage contains none of them.

Reviewer: native `/root/overnight_review`, independent of A/B/C search implementations. Scope was read-only worker code/evidence and writes only in `review/`; no search-code imports, no optimizer reruns, no production/old-evidence edits, no terminal-rune diagnostic. The common logger was inspected first. Initial pure-stdlib run used system `python3`; all subsequent runs used the existing `.venv/bin/python`. Commands, immutable reviewer code snapshots, stdout, stderr, timestamps, exit codes, and relevant hashes are in `runs/`. Dynamic input hashes are also in `checked.json`, `binary_checked.json`, `matched.json`, and `source_manifest.json`.

## What was independently reproduced

`checked.json` records 734 checked source records, including duplicate appearances across intermediate and final exports. This is **not** 734 distinct discoveries. It includes all 126 final A R01 records and all 262 final A r02 records, C's 20 R07 leaders, both B training/continuation export sets for ordinary/wide R04, 20 R03, 20 R03-F, 20 R05 relationships, 20 strongest R05 conditional crib implications, and 20 R06 leaders. `binary_checked.json` independently reproduces another 20 retained R08 outputs. Exact source filenames/local IDs and check types are recorded for registry use. R06 IDs are only unique together with original page: page is included in review records. The canonical final A clue export path is lower-case `worker-a/r02/top_candidates.json`.

Checks calculate plaintext forward from ciphertext and independently reconstructed rules, rather than accepting re-encryption alone:

- Numeric sequences: independent trial-division primes, totient factorization, integer/Fibonacci/gap indexing, offsets and signs.
- A known recipes: frozen rune-key arrays, selected offsets, affine arithmetic; explicit literal-F non-consumption paths and all retained alternative paths; rejection accepted-key indices and each skipped transition.
- A clue keys: arrays reconstructed from the cited rune-source character spans, preserving literal spellings. Running texts reconstructed directly from cited source runes. Phase, wrap/nonwrap, sign and F paths checked.
- C block keys: base60 token-to-byte reconstruction, expected byte hash, physical route coordinates, rejection threshold, modulo29, phase rotation versus finite slicing, full forward output, path consumption and alternative outputs.
- B periodic: frozen key applied at unchanged page phase and independent exact training/continuation score calculation. The search itself was not rerun.
- B layout: route permutations independently derived from frozen source-line intervals, verified as full permutations, then affine/key transforms applied forward.
- B relationships: original position pairs reconstructed for page/ordinal-line offsets, signed differences and collision statistics checked. Strongest crib outputs reconstructed from the assumed crib and differences; they have no non-crib prediction.
- C byte outputs: independently constructed clue bytes, hash derivation, XOR/RC4, or AES parameters; exact output bytes/hash/printable fractions checked. AES uses the same installed cryptography primitive, not an independently implemented AES library.

All passed in the final logged executions. Three preliminary reviewer executions failed because this reviewer's generic parser did not yet handle newly appearing rejection/widened/final-export field locations (`key`/`key_use`). Their tracebacks remain; parser support was repaired and the final comprehensive forward check passed. These were reviewer schema failures, not evidence of bad candidate arithmetic.

## Raw strongest candidates and interpretation

Representative checked IDs (all others are listed in machine evidence):

| Source | Candidate | Independent reading |
|---|---|---|
| A R01 | `R01:r01rigid:r01rigid:9852` | Original49, primes offset90 sign+; begins `URCIAYOYRJJTHHTHRTOTHEONTHSTHAM...`, −6.360734. Same output occurs in B R03, so these are not independent corroboration. |
| A r02 | `R02:r02/widen:widen:r02:literal_f:64979` | Original55 clue099 phase6 sign+, literal sites15/25/41. Begins `ENGEAUOGOEALTOWEXFNGEOGDIEOHX...`, −6.318303. No sustained coherent reading. |
| C R07 | local `12832` in `top_candidates.json` R07 | Original49 column-r0c0-reject232 periodic phase142 sign+. Begins `THIMOEJMOLNLOEAFEOTTHEOEAHJEATSIAY...`, −6.380424. |
| B R04 | `49:period32:shuffleFalse` | Training −3.512343 but continuation −6.984012. Raw `HOETHETINGITHINGTOTHEMEATTHEINTHINGTHEOFTHERTHERSTTHEOUSSOTHSTHETHTHEAUMWPEATCIACCIIACFADIA` is an adjustable-key overfit, not prose. |
| B R04 continuation | `22:period9:shuffleFalse` | Best initial continuation −6.332145; raw output incoherent. This continuation was used to select the leader, so is no longer unseen evidence. |
| B R05 relation | `8:51:line_ordinal:-15` | Difference text `HOETIRTOETHTTHEOT`, not decrypted plaintext. The 12 aligned runes yield an unstable short-sample collision peak. |
| B R05 crib | `8:53:page:15:crib:5:-1` | Assume `ULTIMATELY` on B; predicts `NWEATHATHEOURG` on A, ten runes, −3.818342. This is conditional on an imposed crib and predicts nothing outside it. |
| B R06 | page55 `boustrophedon:affine:8:11` | Begins `CHERNSTHWESLUNGIAHJAFTHOEMNXTHOELBTHJEA...`, −6.366162. No coherent reading. |

No spelling corrections, invented spaces, semantic reinterpretations, or letters were used to improve these samples. Full authoritative runes and untouched transliterations remain in worker exports/review stdout. R08's highest printable fraction was only0.4765625 and no candidate carried a validated complete structure.

## Coverage and comparison accounting

`coverage.json` independently counts scored files and page IDs. Discovery set is45 rune-bearing originals0–55 excluding50 and reserved4/9/14/19/24/29/34/39/44/54. Initial A/C omission of55 is visibly repaired by separate catchups. A known-method stages plus catchups cover45; R02 ordinary/F cover45; B R03/F/R04 cover45; R05 pairs and R06 cover45; C aggregate R07 covers45. R04-wide has43 pages:49 and55 cannot supply two training observations per phase33–64, and133 individual page/period cells were explicitly skipped. It must not be described as completed wide search on all45 pages. R01/R02 each also have ten widening cases stored in top/checkpoint files rather than compressed score rows; the coverage scanner's zero for a widening directory means no compressed score table, not zero executed widening cases.

Independent aggregation from every matched-search compressed table (`matched.json`) agrees with worker reports:

| Lane | Real cells | Matched cells | Best real | Best shuffled |
|---|---:|---:|---:|---:|
| R04 periods1–32 continuation |1,440|1,440|−6.332145|−5.810894|
| R04 periods33–64 continuation |1,307|1,307|−6.384716|−6.184524|
| R05 relationships |65,340|65,340|0.300439|0.358191|
| R05 conditional crib implications |778,504|778,504|−3.818342|−3.862899|
| R06 layout/transform |184,500|184,500|−6.366162|−6.344981|

R05 counts are990 pairs×33 offsets×2 resets, not65,340 recovered plaintexts. The real crib maximum only slightly exceeds the shuffle maximum over778,504 short outputs; this does not support significance or a solution. Each page uses one fixed shuffle reused across hypotheses, so comparisons are descriptive matched searches, not many independent null replications. No p-value is justified here.

A known/F/affine and clue representative controls report exact recovery/rank1; corrupted-first-key checks typically change just one rune and remain very English-like. They measure arithmetic sensitivity, not a false-positive rate. C's three F controls are known-key decoder controls, not full-route/key-selection recovery or a size-matched search null. A/C therefore do not establish superiority over random fragments. B initial R04 controls recover planted periods through32 on one long English source; wide33–64 recovery power remains unmeasured. R05's strong identical-shifted-stream control tests alignment/collision, not sensitivity to two different unknown plaintexts sharing a pad. R06's one-line reversal/affine control does not test every multiline layout. These limitations are accurately named in the final worker reports.

All language ranking here is English quadgram based. A's solved-word view is descriptive, shares the solved-source register, and is not independent corroboration. Beam widths and latent paths impose further model-specific limits. Fixed rules were never tested on reserved pages because no candidate was strong enough to justify consuming them.

## Required final-report/registry handling

No arithmetic bug or reserve leakage found that materially invalidates a completed lane. Preserve the exact tested bounds; do not promote to exclusions of cipher families. Label only source/page/ID records actually checked here `REPRODUCIBLE_CANDIDATE`; everything else remains `UNREVIEWED`. No candidate reaches `VALIDATION_SIGNAL` or `PARTIAL_SOLUTION_CANDIDATE`. Conditional R05 implications must remain distinguishable from predictions and non-crib continuation. Deduplicate A/B identical plaintext and route aliases while retaining origins.

Final coordinator fixes/clarifications: use canonical r02 path; include R06 original page in identity; count widening from their checkpoints, not nonexistent score rows; state wide43-page actual coverage; treat A report self-observed `RUNNING` entry as its metrics snapshot rather than claiming an unfinished search. Read final run command records for actual process completion. Source hashes are point-in-time snapshots; later report-only edits need fresh provenance if quoted.

Resume review with the commands recorded in the successful `final-with-cribs`, `binary-independent`, `final-source-manifest`, and `matched-search-aggregation` run directories. Scientific searches and new holdout reveals are outside these review commands.
