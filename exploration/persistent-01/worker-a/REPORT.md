# PERSISTENT-01 worker A: P01, P04 and P10

No credible plaintext was recovered. Both real searches ranked below their equally searched shuffled controls. This closes two specific admission gaps in the inherited searches; it does not identify or exclude the cipher used by the remaining pages.

## P01: independently admitted periodic clues

All 256 frozen source-rune phrase keys were admitted directly to the literal-F decoder, with every phase, both signs, and all 45 discovery pages. There was no rigid-score shortlist. The new search ran **181,659 nominal cells**, excluding the 501 periodic cells in the historical 512-cell F plan; the other 11 historical cells were finite running keys. Together these cover the declared 182,160-cell periodic grid.

Nominal cells are not independent keystreams. Canonical signed periodic aliases reduce the combined grid to 178,650 distinct page-keystreams. The new execution contains 178,161 distinct page-keystreams, of which eight repeat historical streams through different aliases: **178,153 genuinely new page-keystreams**. See `periodic-aliases.json`.

A size-matched search of 181,659 page-wise shuffled cells completed. Real maximum: **−6.3171108400**; shuffled maximum: **−6.2456920485**. Real page maxima exceeded their paired shuffled maxima on 13 of 45 pages. Complete global top-20 outputs in each condition were inspected and remain incoherent. Ninety page leaders replayed with identical scores; independent scalar arithmetic and full-score recomputation checked all 356 retained alternatives of the 40 global leaders.

The 256-cell planted pilot included 45 page-specific planted keys. Each ranked first among its tested same-page distractors; true plaintext survived the retained 16 alternatives on all 45. The best output was exact on 44; the page-55-length fixture had two rune errors. This was a small sampled key-search control, not a planted search of the complete grid.

All cell rows retain quadgram score, IoC×N, minimum distinct runes in a 32-rune window, zlib ratio, and unavailable non-English LM as null. The structural views did not supply a candidate: real extrema exceeded the single shuffled extreme on 28/45 pages for IoC×N, 8/45 for low distinctness (30 ties), and 10/45 for compression (29 ties). Those statistics use each key's English-beam-winning path and are not independent language-free path searches.

## P04: exact paths versus beam ranking

Complete enumeration tested 68,740 paths over 196 key hypotheses, including matched shuffled searches, on 66-, 92- and 76-rune synthetic controls. The two-error page-55-length winner is a **scoring preference**: the true key ranks first, but the exact true plaintext ranks second among compatible paths. Widths 4, 16, 64 and 256 all select the two-error alternative.

Widths 64 and 256 retain an exact winning plaintext for all 196 hypotheses. Width 16 loses it in four cases; width 4 in 47. These short controls do not prove completeness on long pages. Full exact and beam alternatives remain in `p04-results.json`.

## P10: finite running-text feasibility

The eight frozen solved-source running texts have 3,972 feasible key/offset/sign/page cells under literal-F nonconsumption, including **76 cells rejected by the old ordinary-length admission rule**. Excluding the 11 historical F cells left **3,961 new real cells**, each also searched under a matched page shuffle.

The frozen worker-B decoder checks necessary suffix consumption before pruning. Every retained path was re-encrypted during the search. A 16-hypothesis finite-pressure control recovered the exact 80-rune plaintext at key rank 1; the shuffled control's leading output had 76 errors. Real maximum: **−6.6258742257**; shuffled maximum: **−6.5588620860**. Complete top-20 outputs in both conditions were inspected; no coherent text appeared. P10 completed with exit 0 in 76.395 seconds.

## Scope, evidence and next decision

Both searches assume additive modulo-29 keys, the specified literal-F transition, and English transliteration quadgrams, with beam width 256 and at most 16 retained paths. They neither test other transition models nor establish non-English recovery. Shuffles preserve page length, rune counts and F counts, but not sequential structure or the repeated-rune deficit. One shuffle per page supports descriptive comparisons, not a significance claim.

All reserved originals remained unused. No source glyphs were changed. Search commands, code snapshots, input hashes, raw output, exits and cursors remain under `runs/`; the immutable publication manifest maps preserved originals to publication copies. No historical result was rewritten.

Strategy `outside-box-v1` assigns this worker to the existing-method lane. P01 and P10 are two bounded extensions of that family, not alternative problem models. P04 resolved a decoder-versus-scorer ambiguity. The independently reported line-width explanation removed the proposed rationale for a line-reset search. No further key-space expansion starts automatically.

Two executable followups remain available but **deferred pending evidence-based allocation**: `p12.py --mode control` tests the frozen delimiter-rune adjudicator on four complete held-out source groups; `p07.py --mode control` tests layout/F composition before any layout search. P12 and P07 have not executed. The fixed mission deadline remains 2026-09-17 03:30:37 UTC.
