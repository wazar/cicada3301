# S17 — unknown bijective substitution in the clean Latin register

The fixed unknown-alphabet search recovered 100%, 99.705%, 99.396% and 100% of the four held Virgil control plaintexts. Applied unchanged to originals 0, 17 and 55, its best scores had full-procedure conditional-null upper tails **0.15, 0.75 and 0.75**. No coherent plaintext candidate emerged. This is useful measured recovery in one register, not a general exclusion of substitution or other languages.

## New scope and frozen method

The narrow session check distinguished P05/Q04's surjective 29→17 consonant maps, J02's finite-source count bound and F08's supplied-source compatibility checks. No direct unknown 29→29 bijection optimizer was found in the checked session cards. This is not a universal historical novelty claim.

Every rune label maps bijectively to one canonical rune; word-boundary token 29 is fixed. The clean Q05 Caesar-trained Latin trigram/boundary model is used exactly as provided, including its corrected source end, normalization and smoothing. There is no additive key, optional literal F, skip or rejection transition. Both contexts initially equal boundary29; the objective sums log probabilities over the entire decoded sequence with each explicit word boundary, including the final boundary. Optimization uses the complete page; there is no held suffix claim.

Each search has 24 restarts: one frequency-ranked initialization, then 23 random bijections. Each attempts 30,000 distinct-label swaps with temperature decreasing geometrically from 4 to 0.05. From its best encountered map, it takes at most ten best-improving sweeps across all 406 label swaps, stopping at a local optimum. All restart maps and complete outputs are retained. Incremental scores update exactly the affected trigram terms. Complete recomputations check numerical drift; 32 random-map swap probes per search are independently replayed in Python. This finite optimizer is neither exhaustive nor a posterior sampler.

`S17-CARD.md` was frozen before the cost pilot. The first control took 0.475 seconds in the engine; its 64-search forecast was 30.41 seconds. First-null generation cost was also measured before committing the full matrix. The first nulls required 147, 26,028 and 8 rejection proposals for the three pages. The remaining controls and complete original scope were then run without changing parameters.

## Held controls and limitations

Each control is one complete frozen Q05 held Virgil passage, encoded under a seeded unknown 29-label permutation. The engine receives ciphertext, word boundaries, model-derived frequency initialization and a search seed, never the planted map or plaintext.

| Control | Runes | Selected rune errors | Plaintext recovery | Observed-label map recovery | Truth rank among truth +24 restart maps |
|---|---:|---:|---:|---:|---:|
| Virgil I | 303 | 0 | 100% | 100% | 1 |
| Virgil IV | 339 | 1 | 99.705% | 95.652% | 13 |
| Virgil VII | 331 | 2 | 99.396% | 95.455% | 18 |
| Virgil X | 383 | 0 | 100% | 100% | 1 |

All four pass the predeclared ≥80% plaintext criterion; the gate required at least two. Controls IV/VII retain alternatives that slightly outscore truth by 0.0267994 and 1.0840204 total nats, respectively. Thus their rare-rune errors are real scorer ambiguity among the searched alternatives, not concealed exact recovery. Ranks count all 24 retained restarts, including equivalent maps; they are not independent hypotheses or posterior ranks.

Controls I/X retain respectively 19 and 17 exact-plaintext maps among 24 starts; IV/VII retain none. Intermediate truth visits are not tracked, so there is no claim of search-path survival. Full 29-map accuracies are 75.862%, 79.310%, 72.414% and 86.207%. These differ from plaintext accuracy because each control leaves six or seven cipher labels unused; those assignments are unidentifiable from the control. Selected maps I/X are equivalent to truth on every observed label.

Several restarts fail badly even on these controls, which is why selection and the complete restart budget are part of the instrument. The four controls are 303–383 runes; they do **not** demonstrate comparable recovery at page55's 76-rune length. Classical normalized Caesar/Virgil is also a limited Latin genre/register, not independent evidence that the puzzle is Latin.

## Actual pages and matched null procedure

For each page, 19 independent uniform permutations of its exact rune multiset were rejection-sampled until their adjacent-equality **count** matched the actual page. Word boundaries stayed fixed. The procedure preserves histogram and doublet count, but not equality positions or F positions. Uniform permutation followed by rejection is uniform conditional on this event; it is not the earlier accepted-move MCMC sampler. Each null was given the complete 24-restart optimizer and selection. Maximum attempts were fixed at 500,000 per null, with failure designated UNKNOWN. All 57 succeeded, requiring 1–38,004 attempts; no sampler or scope change occurred.

| Page | Runes / scored tokens | Best total log score | Mean per token | Null maxima ≥ actual | Add-one upper tail |
|---|---|---:|---:|---:|---:|
| 0 | 262 / 321 | -1822.301778 | -5.676953 | 2/19 | 0.15 |
| 17 | 273 / 342 | -1953.803649 | -5.712876 | 14/19 | 0.75 |
| 55 | 76 / 93 | -327.565407 | -3.522209 | 14/19 | 0.75 |

The upper tail is (1 + exceedances) / 20; resolution is 0.05. These are three exploratory discovery comparisons, not untouched confirmation. Conditional random permutations are a declared reference model, not an asserted encryption law. Full-procedure maxima incorporate this optimizer's finite budget; a missed higher-scoring map remains possible.

All 72 retained actual restart outputs were read in full, with original word boundaries and no editorial repairs. They contain isolated Latin-like fragments but no coherent complete candidate. Page55's more attractive absolute score is reproduced or exceeded by most of its length/histogram/boundary-matched nulls. No output was promoted on fragment appearance.

## Checks, preservation and reproduction

All 64 searches completed: 1,536 retained restart maps, 46,080,000 nominal annealing proposals and 649,194 additional hill-climb evaluations, totaling 46,729,194 swap evaluations. There were 857,745 accepted annealing moves. Summed engine time was 6.67 seconds and rejection-null generation 0.68 seconds; initial pilot timing was conservative. Every logged job exited zero without timeout.

Independent replay reconstructs probabilities from the frozen count dictionaries, rather than the exported score table, for all 1,536 final outputs. The maximum absolute score discrepancy was zero. All maps are bijections and all saved plaintext arrays re-encrypt exactly to their input. All 57 nulls preserve the required histogram/count/boundary invariants. Source/model/table/executable hashes and the exact compile command are in `S17/manifest.json`; each run asserts the frozen model, card and C++ source hashes.

- `s17_engine.cpp`: isolated scalar annealing kernel and score probes.
- `s17.py`: frozen inputs, control encoding, exact rejection nulls, execution and independent probe replay.
- `S17/packets.json`: complete control truth and discovery source maps.
- `S17/packet*-main.json`, `packet*-null*.json`: all restarts, mappings, outputs, scores, counts, seeds and exits; null `.input.json` files retain accepted streams and rejection counts.
- `S17/summary.json`, `actual-full-alternatives.json`, `control-retention.json`: full comparison and all unedited actual transliterations.
- `s17_summary.py`: independent count-based score/re-encryption and comparison replay.

Recorded runs: `20260917T021203.071301Z-S17-pilot`, `20260917T021250.019204Z-S17-controls`, `20260917T021312.464634Z-S17-actual0`, `20260917T021335.637461Z-S17-actual17`, `20260917T021412.566473Z-S17-actual55`, `20260917T021509.925987Z-S17-summary`, and `20260917T021647.403238Z-S17-control-retention`. Their command/input snapshots preserve exact invocations. Driver modes are `pilot`, `controls`, and `actual 4`/`5`/`6`; completed searches are reused. Invoke through the standard logger with ≤900 seconds per job and one numerical thread. STOP and the original 2026-09-17 03:30:37 UTC deadline remain binding. No reserve, image, shared-state, Git or earlier scientific artifact was changed.
