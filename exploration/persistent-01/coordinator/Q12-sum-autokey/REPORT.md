# Q12 — arbitrary-seed sum-autokey: exact finite search, no candidate

The inspected C1 sum/plaintext/sign−1 recurrence does not forget an incorrect initial seed. Its error sequence has period k+1 and sums to zero over a period. Direct execution of the extracted inherited functions reproduces four correct encodes/decodes and 116 persistent wrong-seed error sequences. This corrects the scope of an inherited coverage argument without changing inherited code or conclusions in place. It does not concern every feedback function.

That reduction makes every seed for k=2,3,4 cheaply enumerable. The fixed search evaluated 732,511 seeds for each of 64 packets (46,880,704 total), using the existing P03 English rune/boundary trigram model. Four complete held-source controls recover the exact nonconstant seed and every plaintext rune at global rank1. Even the all-equal seed with minimum errors against known truth leaves343/239/51/57 rune errors; these are not the highest-LM equal-seed selections. Arithmetic, seed search, ranking and interpretation are separate checks.

| Original page | Maximum score | Full-search null upper-tail rank |
|---|---:|---:|
| 0 | −4.513828495 | .20 |
| 17 | −4.549503590 | .90 |
| 55 | −3.980602831 | .25 |

Each page has nineteen fixed-seed comparators preserving its first rune and exact adjacent-equality mask, otherwise selecting uniformly among the other28 symbols. They do not preserve its histogram or longer correlations. These are exploratory comparison ranks, not untouched validation probabilities across the wider adaptive programme. All48 global top16 outputs were read completely in `actual-top16-transliterations.txt`; none supplies coherent plaintext. Full arrays preserve every score and the exact indexing needed to reconstruct every seed/output, including non-leading alternatives.

The first control generator happened to draw an all-equal three-symbol seed and correctly stopped at its nonconstant assertion. The amendment continues that same seeded RNG until nonconstant; both draws, original failure/source snapshot and successful controls are retained. No actual input was searched before the controls passed. See CONTROL-AMENDMENT.md. Floating scores use deterministic enumeration and ordinary float64 tolerances; exact finite coverage is not exact real arithmetic.

Independent review63 replays the forward recurrence for every seed, rebuilding the language model directly from frozen sources rather than importing the factor construction. Its report is `../../review-63/REPORT.md`. Review aggregation needed a metadata-only checker correction for the cached first control; failed logs remain.

Limits: only forward, uninterrupted sum feedback, sign−1, seed lengths2–4, canonical indices and this English model. This is neither the P30 FIFO construction nor a general autokey exclusion. No k/sign/function expansion, holdout reveal, input repair or solution claim follows the miss. The useful result is a demonstrated coverage gap and exact bounded search, not evidence favouring this cipher.

Reproduction: inspect `test.py` and its explicit pilot/controls/actual modes, then use the commands recorded under `runs/` through the shared `run_logged.py`; `check_inherited.py` independently reproduces the targeted inherited arithmetic. Inputs, model hashes, seeds, full score arrays, factors and selected outputs are local to this directory or pinned by each command record. Future work should first justify a different source or construction; rerunning completed cells adds no evidence.
