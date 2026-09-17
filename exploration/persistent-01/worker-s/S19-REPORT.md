# S19 — word lengths as a shared substitution payload

The fixed search over explicit word lengths produced no candidate separated from matched within-page permutations: the actual maximum had upper tail **0.65**. Four long held Virgil controls recovered 99.53–99.79% of payload runes, with rare-label errors. These controls validate substantial recovery for their Latin source but do not match the actual sequence's much smaller observed alphabet.

## Payload and model

All 45 admitted F06 pages contain 2,355 explicit words, with lengths 1–14 and 10,466 underlying runes. Every length fits the frozen alphabet: cipher label = length−1. One unknown 29-label bijection is shared across all pages, and the words' internal runes are treated as filler. No modulo mapping, shifted origin, parity channel or alternate length convention is searched. This changes the hypothesized payload units rather than widening an additive key search. The targeted prior check found length-copy and Elias-framing tests, but no equivalent unknown-substitution length-payload search.

The continuous Latin model uses the same clean Q05 Caesar source and original wordwise GP conversion, then removes boundary tokens. It does not re-tokenize across word edges. Training has 120,854 runes. Interpolation is fixed: unigram pseudocount 0.5 across 29 output runes, bigram concentration 8 and trigram concentration 5. Each scored page starts from context (29,29); there are no scored boundary tokens, no assumed plaintext word boundaries and no cross-page trigrams.

The checked S17 scalar optimizer is reused with only the documented context/reset adapter. Each search has one frequency-ranked start plus 23 random bijections, 30,000 swap-annealing proposals per start at temperature 4→0.05, followed by at most ten best-improving complete 406-swap sweeps. No search-budget or model change followed controls or actual scores. Exact arithmetic does not make this finite optimizer exhaustive.

The frozen preflight/card and first-control cost pilot preceded actual fitting. The pilot took 1.115 seconds and forecast 26.75 seconds for all 24 searches, so the original scope was retained.

## Controls and important mismatch

Each control uses the first 2,355 normalized runes from the same held Virgil books I, IV, VII and X, with complete source-character maps. These extend beyond Q05's earlier 60-word controls; the extension was fixed before scoring, without repeating text cyclically. Each control is split into exactly the 45 actual page-unit counts and encoded by an unknown seeded permutation into lengths 1–29.

| Control | Payload errors / 2,355 | Rune recovery | Observed-label mapping recovery | Truth rank among truth +24 starts |
|---|---:|---:|---:|---:|
| Virgil I | 10 | 99.575% | 85.185% | 10 |
| Virgil IV | 11 | 99.533% | 85.185% | 19 |
| Virgil VII | 5 | 99.788% | 92.593% | 19 |
| Virgil X | 11 | 99.533% | 88.889% | 18 |

All four satisfy the predeclared gate; at least two needed ≥80% rune recovery. None of the retained maps is exactly correct on every emitted label. Some searched mappings score above truth by changing rare symbols, so high rune accuracy must not be described as full-map recovery. Two labels are unused per control; full-map accuracies are 79.310%, 79.310%, 93.103% and 89.655%. Complete error positions, all restart errors and unused-label lists are retained. Ranks include equivalent restart outputs and are not independent hypotheses.

**Actual and control alphabets differ substantially.** Actual lengths use 14 distinct labels; every long Latin control uses 27. The controls match page unit counts, not length marginals or underlying rune totals. Their synthetic lengths sum to 33,950 / 32,281 / 37,864 / 37,119, versus actual 10,466. Internal filler rune strings were not synthesized because the tested decoder never observes them. No claim of power on an unknown 14-symbol Latin register follows, and no control letters were deleted to make the support match.

## Actual and null results

One complete shared-alphabet search fits the 2,355 actual length symbols in 45 reset chunks. Each of 19 nulls independently permutes the length sequence within every page. This preserves each page's exact length multiset, number of words and sum of underlying runes, together with every page reset. Each null receives the same full 24-start optimizer.

Actual best total log score is **−7367.886763**, or **−3.128614 per payload rune**. Twelve of 19 null maxima are at least as high, giving (1+12)/20 = **0.65**. Full null maxima and random permutations/seeds are saved. This is a within-page exchangeability comparator, not an asserted cipher generator; tail resolution is 0.05 and the discovery material is not an untouched confirmation set.

The selected complete 45-chunk output was inspected without inserting guessed word breaks. It is not coherent plaintext. All 24 actual restart outputs are preserved in full, including their source page IDs, maps and per-page scores. Other uninspected alternatives are not characterized as readable or unreadable by this report. Fixed observed action leaves 15 unused actual cipher labels unidentifiable, so the full 29-entry map itself is not a uniquely recovered key.

## Validation and execution

Independent replay verifies every original clean-Caesar word's normalized runes and character spans, reconstructs continuous unigram/bigram/trigram counts, and checks all 26,100 meaningful score-table cells. The maximum discrepancy is zero. The unused boundary-output column is NaN, and the adapter never scores it. All held Virgil control ranges are independently reconstructed from their book headings and raw bytes; all encoding maps round-trip.

All 576 retained outputs from 24 complete searches are independently rescored from counts with explicit page resets and re-encrypted to their input lengths. Maximum total-score discrepancy is 3.55×10⁻¹¹. All 19 null generators and every per-page permutation replay exactly. The engine's random-swap probes and periodic full recomputations additionally validate its incremental score arithmetic.

The first independent summary run failed because its checker mistakenly treated a final single character as a two-character token when computing its source span. The checker was corrected to require a two-character candidate. The failed log is retained; the full check then passed. No training data, model, control, search, null or optimizer was changed or rerun to obtain a different scientific result.

Total work: 24 searches, 576 restarts, 17,280,000 annealing proposals and 234,668 hill evaluations, for 17,514,668 swap evaluations. There were 3,809,041 accepted annealing moves. Summed engine time was 16.19 seconds. Every production job exited zero without timeout; the explicitly retained checker failure is the sole nonzero scientific-log exit.

## Artifacts

`S19-CARD.md` and `S19-preflight.json` freeze scope and exact source lengths. `S19/manifest.json` pins source/model/code/table/executable hashes. `s19_prepare.py` derives the continuous model and control maps; `S19/engine.diff` records the exact reset change from S17. `s19.py` drives controls, actual and nulls. `s19_summary.py` independently reconstructs sources, counts, scores, round trips and comparisons.

`S19/packets.json` preserves every actual word map and all control source positions. `S19/{control0..3,actual,null00..18}.json` preserve every restart, full map, complete output, seed, score, acceptance/evaluation count and exit. `S19/summary.json`, `actual-full-alternatives.json` and `selected-output.txt` give the full comparison and unsegmented transliterations.

Logged runs: `20260917T022839.342909Z-S19-preflight`, `20260917T023105.819659Z-S19-prepare`, `20260917T023220.824672Z-S19-pilot`, `20260917T023313.954937Z-S19-controls`, `20260917T023350.426468Z-S19-actual-and-nulls`, failed `20260917T023544.348259Z-S19-summary`, and passing `20260917T023615.616206Z-S19-summary-checker-fix`. Commands and snapshots remain in those directories. Driver modes are `pilot`, `controls` and `actual`, through the standard one-thread logger. STOP and the original 2026-09-17 03:30:37 UTC deadline remain binding. No reserve, new image, shared-state, Git or earlier scientific artifact was altered.
