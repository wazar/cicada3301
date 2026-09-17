# P25-clean — corrected Caesar boundary, identical search

Removing the accidentally included English footer changes rankings materially but yields no candidate on originals 0, 17 or 55. All four held Virgil controls still recover the exact planted plaintext, literal-F path and key/phase/sign at rank 1. This is a source-boundary repair of P25, not additional independent search coverage or selection between two models.

## Frozen repair

The original P25 run and contaminated model remain intact. Q05-latin-clean removes exactly 16 footer word fragments, 59 runes and 16 boundaries from the Caesar training body; its 20,484 preceding words and every held control object are unchanged. Corrected training contains 120,854 runes and 141,338 tokens. The corrected model SHA256 is `f4667652da86ab021af47cfcba098226454415a809ff3b1ecce84a1b4023e92e`; original model SHA256 is `16f491d53007cc4492d1bb94b42fed16aca136bca0f62ba7ebe1b8ba769c3b93`.

Every model probability changes through normalization. The maximum absolute log-probability change is 18.608995 nats, despite the small removed token fraction; its median is 0.00053045. Small contamination does not establish negligible influence. The source boundary is repaired from provenance, without tuning against puzzle results.

The original CARD and P25 report specify the unchanged optional-literal-F additive relation, beam width 64, Latin rune/boundary LM, first 16 clue keys, all 81 natural phases and both signs. Exactly the same seven main packets and 133 null packets, boundaries, ciphertexts, random seeds and 162-cell grids are searched. No key, corpus, beam, null or transition variant was added. This remains an existing additive-method/register extension, conditional on its language and visible word-boundary assumptions.

## Results and measured effect

| Main packet | Original maximum | Corrected maximum | Original tail | Corrected tail |
|---|---:|---:|---:|---:|
| Virgil I | -2.23581116 | -2.23538720 | .05 | .05 |
| Virgil IV | -2.47495174 | -2.47481599 | .05 | .05 |
| Virgil VII | -2.34041594 | -2.34043009 | .05 | .05 |
| Virgil X | -2.19913438 | -2.19874998 | .05 | .05 |
| Original 0 | -6.59722100 | -6.66288938 | .30 | .20 |
| Original 17 | -6.71571979 | -6.90736206 | .85 | 1.00 |
| Original 55 | -6.43410896 | -6.60805127 | .95 | .95 |

All four controls have zero rune errors, true key rank 1 and true path rank 1; none loses its truth path during beam pruning. All seven main winning key IDs remain unchanged. Original 17's winning literal/ plaintext path changes; the other six main winning paths remain unchanged. The actual winning IDs are respectively `clue:008:3:1`, `clue:006:0:1`, and `clue:012:3:-1`.

Across all 140 main/null searches, every one of 22,680 cell top scores changes. The maximum absolute top-score change is 0.57634030; 18,914 cell path sets change, as do 46 search winning key IDs and 65 winning paths. Complete per-cell scores, old/new ranks, path comparisons and global alternatives are retained in `all-cell-comparison.json.gz` and `all-packet-comparison.json.gz`. These changes must not be hidden behind the unchanged main key IDs.

All 48 corrected actual leading alternatives were inspected in full and are preserved in `packet-4-full-top16.txt`, `packet-5-full-top16.txt`, and `packet-6-full-top16.txt`. None supplies coherent complete Latin plaintext. This assessment does not promote isolated word-like fragments or establish a general exclusion of Latin plaintext.

## Calibration and validation limits

Each main packet retains its 19 original full-procedure nulls, conditioning exactly on the ciphertext-F and adjacent-equality masks. Every null searches the same 162 cells. The conditional sampler is uniform over its mask-defined class; it does not preserve non-F histograms or longer dependencies and is not claimed to be the true cipher distribution. Per-packet tail resolution is .05. No combined cross-page significance is inferred, and the source repair is not a second independent experiment.

Production re-encrypts every retained path. The separately implemented checker verifies all 140 searches, 22,680 cells and 336,960 alternatives, source controls, keys, null RNG, plaintext/consumption maps, global alternatives and tails; maximum independent score discrepancy is 1.69e-14. Tiny exhaustive controls pass unchanged. Beam64 is still a bounded heuristic on full pages, and encountered aliases do not exhaust paths pruned earlier. Four windows from one held author do not establish universal language power.

The seven corrected logged batches took about 85 seconds including I/O; the full independent replay took 6.70 seconds and comparison 7.84 seconds. One numeric thread was used, all exits were zero and no batch approached 900 seconds. Independent review43 now passes all45,360 cells across both models and673,920 retained paths, complete selections/null RNG/source controls and score arithmetic (maximum discrepancy1.87e−14); see ../../review-43/REPORT.md. It independently confirms18,914 unordered path-set changes, distinct from21,852 order-sensitive path-list changes.

No reserved page, image50, new image read, Git mutation or installation was used. The corrected model is the intended instrument after a documented source repair; the original model, outputs and failures remain available in P25. The bounded result does not support expansion of this key list or a claim that other Latin registers or cipher constructions are excluded.
