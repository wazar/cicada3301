# P11 independent evidence review

PASS within the stated finite scope. No candidate plaintext or significant real/null separation is established. This review confirms accounting, saved evidence integrity and selected-path arithmetic; it does not prove search completeness beyond the recorded finite beam configuration or identify the puzzle's cipher.

Scope ACK: outside-box-v1 and continuous contract read, together with strategy.json, config.json and standard logger. Root remains sole coordinator/Git writer; review owns review-05 only. Direct deadline 2026-09-17T03:30:37Z and STOP apply. Review runs alongside other research, without a global barrier. Only the pinned 45 discovery pages were interpreted; no reserved-page data was inspected. No new keys were searched. P11 code was inspected before running review code, and was never imported/executed by this review.

## Measured checks

- All 11,520 compact rows checked against all 11,520 local raw shard SHA-256s, byte counts and values: native/cross scores, structural statistics, selected rune hash, length, consumption, literal count, alternative count and diagnostics. Total raw size exactly 187,082,357 bytes. Every page has exactly all 128 offsets × two signs. Both real/null modes and both model selectors are present: 46,080 recorded beams, 686,080 retained paths (171,520 per combination).
- All 223 copied full candidate cells are byte-identical to their raw shards. Their selection is exactly the union of per-page/model/mode leaders and four global top-20 lists. All 12,128 retained paths in those cells independently scalar-reencrypted: literal sites emit rune 0 and consume no key; other sites emit `(plaintext - sign * phi_mod29[offset + consumed]) % 29` and consume one key. All complete rune outputs, key-before/after traces and delimiter consumption records agree.
- Independently replayed all 12,288 paths in all 1,024 control key/model cells. Rebuilt both fixtures from solved sources; recomputed complete saved key rankings. Each of four true keys ranks first, the leading plaintext has zero rune errors and truth survives in retained alternatives. WELCOME has 4,096 retained paths per model; AN_END has 2,048 per model. The archived complete controls exactly match local files.
- All 15,000 integer phi entries independently reproduced using smallest-prime-factor recurrence, distinct from the worker's subtractive sieve; first 128 also checked by literal gcd counts. Mod29 array and pinned hash agree. Null arrays on all 45 pages independently reproduced with documented NumPy seed 190020+page; zero positions and nonzero multisets are preserved.
- Within every page, all 256 signed mod29 key prefixes of full ciphertext length are distinct. This confirms the stated alias definition only, not absence of shared shorter prefixes or duplicate decoded paths.
- Frozen C source/training hashes, English table, control source hashes and P11 source hashes agree. Actual search/control logger snapshots match current p11.py and included search/scorer source snapshots. Four logged runs exited zero. Review scalar rescoring of 96 leader/control alternatives reproduced both model scores to maximum absolute difference 2.665e-15. Scoring uses independent scalar code but deliberately shares the frozen English table and five solved source texts; it is not independent language evidence.

| Model | Real maximum | Null maximum | Page wins | Median paired difference |
|---|---:|---:|---:|---:|
| English | -6.590867818603594 | -6.612181821410794 | 21/45 | -0.008301040743361021 |
| Rune/boundary | -4.231952657639068 | -4.27913838402899 | 27/45 | +0.0082973577538894 |

The English real leader is page55, offset62, +sign, 74 consumed keys and literal sites15/25. Rune real leader is page49, offset0, -sign, 65 consumed keys and literal site3. Full leading outputs and two competing paths for all four real/null model leaders are preserved in leading-outputs.json. Inspection finds no sustained coherent plaintext; English-looking short fragments provide no candidate claim. No oracle solve assertion is warranted.

Prior R03 REPORT.md and extras.py confirm its literal-F family list excluded integer_phi, despite rigid integer_phi coverage. Thus this is a finite coverage extension rather than a repeat of that literal-F matrix.

## Limits and documentation

The compact publication accurately says that all raw alternatives remain local; it does not publish all 187 MB. The complete compact statistics describe language-selected paths, not an independent structural-score path search. One matched-null field cannot calibrate significance. Negatives remain conditional on the finite phi offsets/signs/page reset, literal-F-only transition, and the two English/solved-register adjudicators. Exact reencryption is consistency, not evidence that a key is genuine. This review did not rerun the beam searches or reencrypt every path in unselected raw shards.

Minor wording issue: raw-retention-manifest.json's controls string says `allretained16alternatives`, while AN_END cells have eight retained alternatives. The counts and coverage report correctly report 2,048 per AN_END model. Prefer “all retained alternatives (up to 16)” if editing the publication metadata; this is not an arithmetic defect.

## Execution record and continuation

check.py completed through standard logger in 33.474 seconds, exit0. rescore.py corrected run completed in 0.088 seconds, exit0. Both use <=900-second bound and numerical thread settings1. The first supplemental rescore run exited1 because this review's suffix matcher inadvertently matched summarize_p11.py as p11.py; the only source difference was the already documented missing-brace repair in the summary script. Corrected exact-basename matching passed. Original error, code snapshot and stderr are retained; no search files were altered.

Reproduce:

```
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/review-05 --label p11-complete-evidence-check --seconds 900 --input exploration/persistent-01/worker-i/p11.py --input exploration/persistent-01/worker-i/p11/publication/raw-retention-manifest.json --input exploration/persistent-01/config.json -- .venv/bin/python exploration/persistent-01/review-05/check.py
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/review-05 --label scalar-frozen-rescore --seconds 900 --input exploration/persistent-01/worker-i/p11/manifest.json -- .venv/bin/python exploration/persistent-01/review-05/rescore.py
```

No process remains. Release this review slot. Do not expand phi offsets based on these maxima. Next useful discriminating experiment is the proposed delimiter-bounded numeric-output interpretation with a planted complete structure and held-back group prediction; freeze representation choices before evaluation. A separate construction-control test could measure a genuine plaintext model outside these two scorers, but requires its own hypothesis and sensitivity fixture, not reinterpreting these misses as language-general evidence.
