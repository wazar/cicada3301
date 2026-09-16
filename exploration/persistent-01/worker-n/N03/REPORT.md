# Adjacent-page substitution-invariant copies: N03/N04

No excess cross-page copy relationship was found on legitimate adjacent discovery pairs **0–1,1–2,2–3,5–6,6–7,7–8**. This tests relational redundancy without English scoring or additive-key assumptions; all offsets are free, so complete copied blocks may move. It does not require a common alphabet across pages.

**N03 exact equality patterns:** seed12 contiguous runes, extend under a bijective rune map up to64. Across282,728 candidate offset pairs,3960 seeds matched. Longest matches by declared page pair were17,17,15,16,18,15. Global maximum18 has **p=.34** against399 complete-procedure pagewise anti-repeat Markov simulations. Null maxima:16(67),17(197),18(103),19(27),20(5). These are unsurprising short patterns, not plaintext candidates. Independent pairwise-equality matrices verify all3960 saved matches and their maximal forward extensions; independent page relabellings leave results unchanged.

**N04 one justified robustness followup:** N03 loses power after a central corruption, so fixed windows24/40 omit exactly the middle aligned rune while requiring a single bijection across both flanks. Same pairs and all offsets, full-procedure399 new nulls. Real has **zero matches**, p=1; all399 nulls also have zero. No alternative approximate tolerance or longer-block expansion followed this miss.

| Planted copy controls | N03 exact detection | N04 one-wildcard detection |
|---|---:|---:|
|16 runes, intact|0/10|0/10|
|24 runes, intact|10/10|10/10|
|40 runes, intact|10/10|10/10|
|24 runes, central corruption|1/10|10/10|
|40 runes, central corruption|3/10|10/10|
|40 runes, random-position corruption, new controls|not retested|20/20|

Each first five controls per condition copies a fitted-Markov source, next five an actual solved-source segment; backgrounds and page lengths match the discovery panel. The new random-position controls split10/10 across these source registers. They avoid measuring robustness only at the hand-selected center. All controls use the global null maximum across both/all windows, six pairs and every offset, with detection p<=.01. N04 positive p-values have Monte Carlo floor.0025; zero null hits is not a proof of zero false-positive probability. Samples are small and do not characterize arbitrary corruption rates.

**Scope:** fixed per-page rune relabelling of a common contiguous passage, free offsets, exact windows or the specific central-wildcard construction. Block reorder is allowed only insofar as a contiguous copied window survives. Within-window reordering, insertions/deletions, position-dependent alphabets, multiple corruptions and short copies remain outside the bound. Solved-source controls can have more repeat structure than actual ciphertext; matched-Markov controls separately cover actual-like repeat behavior. Nulls model each page's smoothed rune marginal and repeat suppression, rather than exactly preserving observed counts; higher-order/nonstationary nulls are not established. Discovery selection makes reported p-values exploratory.

All source rune arrays, original-page metadata, offsets, partial bijections, complete planted pages/permutations/edits, seeds, null parameters and every null statistic are saved in compressed evidence and control files. A max64 result would only be a lower bound, but none real approached this cap. No reserved page was read; no Git writes. Logged N03/N04/verification durations8.52s,5.89s,.14s, one numerical thread each; no active jobs.

**Next decision:** this bound does not support ordinary long copied passages between these adjacent discovery pages. Retire this fixed-relabelling relation lane unless a concrete artifact identifies different alignment/adjacency. A materially different future relation would be a source-justified page-to-page numerical constraint or delimiter-layout relation, not merely more wildcard choices.
