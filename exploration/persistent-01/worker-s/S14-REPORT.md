# S14: power-conjugated cyclic clue keys

All four planted solved-source controls recovered the exact plaintext, exponent, key phase and literal-F path at rank 1. The three discovery pages supplied no candidate above their matched full-search nulls: upper tails were 1.00, 1.00 and 0.45 for original pages 0, 17 and 55. This result covers the frozen conjugate-additive family and English model; it does not exclude other coordinate systems, languages or transition mechanisms.

## Frozen experiment

`S14-CARD.md` was frozen before the cost pilot. The hypothesis changes canonical GP coordinates through tau(x) = x^e modulo 29, for the 12 units e modulo 28, then applies a cyclic clue key additively in those coordinates. Normal output is tau-inverse(tau(cipher) + sign × tau(key)); the optional literal-F branch emits canonical zero without advancing the key. There is no rejection-loop transition. This remains conjugate-additive arithmetic. The identity exponent overlaps earlier canonical-coordinate searches, and aliased cells are not independent hypotheses.

The first 16 frozen P03 clue keys, every key phase and both signs give 162 cells per exponent, hence 1,944 nominal cells per search. The unchanged P03 beam has width 64 and retains 16 final paths per cell. Its frozen English rune/boundary language model scores canonical runes after inverse coordinate conversion. Reported maxima are over beam-retained paths, not exact optimization over all literal-F paths. No corpus, scorer, exponent or key changes followed the actual results.

The exact imported kernel was copied to `S14_p03_frozen.py`; subsequent runs assert its hash, the clue-cell manifest and training-source hashes against the pilot manifest. `S14-model.json.gz` records these hashes, all cells and source provenance. Discovery inputs and original source positions are preserved in each packet from `worker-f/F06-maps.json` (SHA-256 `74bdf46e10ce11080762e82350004bd95ea1952a866a9778b3e746c20012973b`).

## Controls and results

Exhaustive scalar checks covered 12 × 2 × 29³ = 585,336 encryption/decryption relations. Twenty-four tiny exhaustive literal-F cases checked the adapted beam and identity compatibility. The pilot's 32 cells measured cost only; full-family controls followed before discovery searches.

| Held solved-source control | Runes | Planted exponent | Full-family rank | Selected rune errors |
|---|---:|---:|---:|---:|
| 0_welcome | 515 | 3 | 1 | 0 |
| jpg107-167 | 319 | 5 | 1 | 0 |
| p56_an_end | 85 | 9 | 1 | 0 |
| p57_parable | 95 | 11 | 1 | 0 |

The planted path was never pruned in these controls. They establish recovery for these four constructions in the model's English register, not universal beam completeness.

Each actual page was compared with 19 independently seeded null pages preserving its exact F positions and adjacent equality mask. Other runes were sampled uniformly from the allowed nonzero labels, excluding the preceding label at unequal positions. This does not preserve frequencies and is not asserted to be the true cipher law. Every null received the entire 1,944-cell procedure. The upper tail is (1 + number of null maxima at least actual maximum) / 20.

| Discovery page | Runes | Maximum score | Best nominal cell | Null exceedances | Upper tail |
|---|---:|---:|---|---:|---:|
| 0 | 262 | -4.5377993572 | e25, clue 013, phase 1, sign +1 | 19/19 | 1.00 |
| 17 | 273 | -4.5390398468 | e9, clue 005, phase 3, sign -1 | 19/19 | 1.00 |
| 55 | 76 | -4.2425500729 | e9, clue 007, phase 1, sign -1 | 8/19 | 0.45 |

All 64 searches completed: 124,416 nominal cells and 960,042,456 beam expansions. Summed per-search time, including checkpoint archiving, was 609.48 seconds. Every logged job exited successfully without timeout. The real maxima do not justify a candidate. All 48 distinct retained global real alternatives were inspected in their full unedited transliterations; none forms coherent plaintext. Independent replay using direct modular powers and independently computed LM probabilities passed all 48 alternatives. Both power-coordinate and canonical output arrays, key consumption and literal positions are retained.

These are three descriptive discovery-page comparisons, not untouched confirmation. With 19 nulls, the attainable tail resolution is 0.05. The result is conditional on the specific key list, power permutations, optional-literal-F transition, English register and finite beam. It neither proves all keys fail nor establishes that the original numeric labeling is correct.

## Reproduction and artifacts

- `s14.py`: frozen search adapter, controls, null generator, STOP/deadline checks per cell and checkpoint resume.
- `S14-packet{0..6}-main.json.gz` and `S14-packet{4..6}-null{00..18}.json.gz`: all cell scores, top alternatives, source maps, seeds, truth and diagnostics.
- `S14-arithmetic.json.gz`: coordinate tables and arithmetic/tiny controls.
- `S14-summary.json`: control recovery, every null maximum, per-exponent maxima and global alternatives.
- `S14-actual-full-alternatives.json`, `S14-replay-main{4,5,6}.json`: full canonical/power outputs and independent replay with transliterations.

Run from the repository root through `run_logged.py`, using the virtual environment and one numerical thread. The frozen command modes are `s14.py pilot`, `s14.py controls`, and `s14.py realpacket 4` (or 5 or 6); completed packets are reused. Individual cells are checkpointed in batches; an individual search is `s14.py one 4` or `s14.py one 4 0` for null zero. Existing STOP and the original 2026-09-17 03:30:37 UTC deadline remain binding, so do not resume beyond them without a new authorized experiment.

Recorded logger runs: `20260917T013214.203659Z-S14-pilot`, `20260917T013407.818838Z-S14-controls`, `20260917T013547.450207Z-S14-actual0`, `20260917T014140.651018Z-S14-actual17`, `20260917T014630.827276Z-S14-actual55`; independent replay runs at `013744.760019`, `014259.141586`, `014742.273208`; aggregate `20260917T014742.489959Z-S14-aggregate`. Their manifests preserve executable/input snapshots, hashes, timings, exits and exact invocations. No prior S01–S13 artifact was modified.
