# P14 — continuous numeric clock across originals 0–3

No candidate emerged from the frozen four-cell continuous-clock test. The actual 946-rune packet scored −4.700894751855845, selecting integer-phi with sign−1. Four of19 exact-repeat-mask null packets scored at least as highly: corrected empirical tail5/20=.25. This is one joint four-page selection, not four independent confirmations. Page0 was already tested under the reset convention and is not new input coverage.

## What changed

The key and repeat-filter state continue through physical cuts after runes262,528,729. Keys remain prime-minus-one and integer-phi modulo29, each sign±1, start0, rejection probability.83, rejected trial consumes2 draws, accepted trial1. The existing English rune/boundary LM resets context at each cut in BOTH clock conventions. Word-end positions are unchanged and no delimiter is injected at a cut. Thus this is a key/filter clock test with fixed pagewise language scoring, not a new language model or an assertion that prose necessarily resets there.

The primary statistic is the continuous four-cell maximum. Reset scores are diagnostic and do not enter selection or a posthoc difference test. Complete top1 outputs for all cells and top16 for the selected cell are retained for every packet. The real continuous scores were:

| Cell | Score |
|---|---:|
| integer_phi:−1 | −4.700894751855845 |
| integer_phi:+1 | −4.723702467991741 |
| prime_minus_one:+1 | −4.729362353561463 |
| prime_minus_one:−1 | −4.801185007152353 |

The best reset diagnostic score was −4.743435531822405. No significance is assigned to this observed difference.

## Instrument and finite bound

All four complete held English groups from M25 were concatenated in their fixed order into1014 runes, preserving source character-to-rune maps and word ends, then split at the same three cuts. These are four encoded instances of ONE shared source packet, not four independent corpora. Frozen seeds331400..331403 plant the four cells. The independently written scalar encoder matched all ciphertext and accepted indices; explicit rejected/burned/accepted traces and boundary rows are saved.

| Planted cell | Selected key correct | Rune errors /1014 | Exact truth path rank in top16 | Correct-key reset errors |
|---|---|---:|---:|---:|
| prime_minus_one:−1 | yes |0|1|724|
| prime_minus_one:+1 | yes |0|1|723|
| integer_phi:−1 | yes |1|2|722|
| integer_phi:+1 | yes |0|1|720|

The imperfect control differs at position290; its exact truth plaintext and path survive at rank2. The method is not a perfect complete-text selector. No parameter changed to remove this error. A separate two-symbol scalar fixture forces rejection exactly at a cut: tested draw1 and burned draw2 precede acceptance at draw3; retaining previous ciphertext is necessary to explain it.

Sixty-four tiny exhaustive cases compared direct acceptance-index enumeration against dynamic programming in both reset and continuous modes, including LM context reset. A further scalar arithmetic/score replay checked116 saved cell rows, every full top1 path, and all source maps. The independent reviewer checks top16 paths separately.

The2048-draw finite cap was fixed before scoring. Every first1024 array entry equals the saved M25 key. No wrapping, padding, cap increase, seed search, offset search, beam choice or additional key was used. Across116 saved cell rows the highest queried index was1099 (zero-based), with zero cap-excluded continuations. Actual four-cell search queried through1025, so the old finite1024 convention cannot silently be credited with this test. The winning actual path uses1000 draws, with page intervals0→274→556→767→1000. This is a finite formula-stream approximation, not a proof over infinite streams or arbitrary long rejection sequences.

## Null and coverage

Seed331419 draws19 strings uniformly over the fixed actual adjacent-equality mask: first symbol uniform29, each repeat forced, each nonrepeat uniform among the other28 symbols. This includes the three page joins. Every null runs all four continuous cells and selected-cell top16. It preserves exact repeat locations, not histogram or linguistic structure; it is a conditional generative reference, not the actual ciphertext-generating distribution. There are96 continuous top1 cell evaluations across4 controls+1 actual+19 nulls,24 selected-cell top16 evaluations, and20 reset diagnostic cell evaluations (controls and actual only). No extra packet/group was tested after the miss.

The overlap check found OB-C3 tests move-to-front continuity/rank entropy, while the detector audit tests random one-draw continuous keys at a reset-only interface. M25/M26 explicitly reset these numeric skip-by-two streams per page. Those priors do not cover this exact construction; neither does this result invalidate their measured bounds.

Runs: pilot0.860s, remaining controls2.168s, actual/null12.052s, replay0.568s, all standard-logger exit0 and one numeric thread. Sources, exact key arrays, frozen card, maps, all outputs and command snapshots are retained. The scope is two numeric formulas/two signs, finite2048 draws, this skip-by-two rejection rule, one English rune/boundary model with LM resets, and one contiguous discovery packet. No family-wide cipher conclusion, solve claim, or evidence against other clocks follows. A different boundary mechanism would require its own predeclared controls; this packet is not expanded after the miss.
