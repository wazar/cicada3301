# Worker L — finite bag inventory renewal

L1 found no finite-inventory renewal signal on the45 authorised discovery pages. This is an explicit bounded direct-output model test, not a key search, plaintext decode, or evidence of a uniquely determined generator.

## Mechanism and prior overlap

Compared memory-one stutter/uniform-other28 generator to equal-copy shuffled bags m=1,2,4. The base permutation is conditioned to contain no equal neighbours, including across bag boundaries; independent stutters create the observed doublets without consuming bag contents. Run compression is therefore exact for this particular construction. Each page may begin at an arbitrary unknown phase, and all phases are fitted.

Prior check found OB-C1 rank-deletion, OB-C2/C3 move-to-front recurrence ranks, campaign14 lag2..12, and round17/P4 lag2..8 plus window58 underdispersion already measured. We did not call those statistics new. L1 instead tests exact block inventory renewal: a complete29m block at the true phase must contain m copies of every symbol. R18/L2 already covers fixed collision-nudge delta spectra, so that proposed followup was not executed again.

## Results and limits

The page list was split into23 training and22 held discovery pages by sorted index parity. The three inventory sizes were ranked by training z; m=4 selected. Per-page phase minimization is repeated for controls and nulls, including held pages as a latent nuisance fit. No reserved pages were accessed or scored.

| Copies m | Eligible train / held pages | Inspected train / held runes at best phases | Held excess fraction |
|---|---:|---:|---:|
|1|23 /22|4437 /4785|0.323511|
|2|21 /21|3654 /3886|0.227483|
|4|14 /15|2088 /2088|0.146073|

Initial parametric wholeprocedure M1 null at training-fitted q gave p=0.149254. A specified followup conditions on the *exact observed per-page stutter masks*, removing fitted q as a nuisance:80 calibration and200 full-procedure nulls give p=0.154229. Conditional held statistic1.1234, null99th percentile1.9853. These are overlapping analyses, not independent replications.

All20 exact controls per inventory size had zero true-model excess and selected the correct m. All20 per size with1% independent pre-stutter substitutions also selected the true m. Across60 exact and60 corrupted controls,120/120 exceeded the conditional99th-percentile null bar. This measures a narrow strong-signal power envelope; it does not establish sensitivity to heavily corrupted, variable-size or imbalanced bags.

Independent Counter-based verification recomputed all7105 eligible phase scores and independently reconstructed each collapsed stream from the allowed original-page indices. Every one of7105 phase choices has an explicit excess-symbol complete-block witness. Therefore none of these exact balanced-bag constructions is compatible with the tested eligible pages, under the stated no-adjacent base/stutter model. Fractions above are inventory excess per inspected compressed rune; they are not arbitrary edit-distance or transcription-error bounds.

## Instrument failure caught and repaired

The first exact-control run exited nonzero BEFORE any actual discovery statistic. For a short page, the true phase sometimes left no complete block while a wrong phase left one; minimizing only eligible phases then falsely rejected the exact control. Corrected page/model eligibility requires compressed length >=2B-1, guaranteeing a complete block at every possible phase. This omitted3 pages for m2 and16 for m4, recorded explicitly in `l1-conditional/independent-verification.json`. The failed run and generated full arrays remain in `l1-failed-control/` and the original logged snapshot. Repaired controls then passed. No real score was seen before the repair.

## Evidence and scope

`PREREG.md`, `L1-CONDITIONAL-CARD.md`, and `strategy-ack.json` record design and repair. `l1-conditional/` contains exact input/map hashes, full phase maps back to source indices, full generated datasets, calibration arrays, null arrays, control arrays, summary, independent verification and7105 phase witnesses. Seeds33012701/33012702 and all code snapshots/exitcodes are retained in `runs/`. Completed main batches18.08s and18.20s approximately; exact recorded durations in command.json are authoritative. No Git mutations, English scorer, additive keystream or reserved-page reads.

The negative is conditional on the3 stated finite inventories, the conditioned shuffled-bag plus stutter transition rule, and a language-independent inventory adjudicator. It does not address unequal inventories, probabilistic/partial/variable refills, arbitrary hidden resets within pages, genuine equal consecutive base draws removed by compression, or an arbitrary output channel. Matching adjacent doublets alone does not identify M1; tested bags fail their additional renewal prediction. No broad sampler/OTP conclusion follows.

# L2 — fresh unit alphabets

After the bag miss, changed the encoding unit: each delimiter unit gets a fresh independent29-symbol permutation. This breaks F09's identical-codeword prediction but preserves each unit's internal equalitypattern. A conditional transport removes source adjacent repeats and expands with the actual unit's repeat mask. It is a deliberately flexible source-register hypothesis, not a parsimonious key or an explanation of repeatmask generation.

One frozen likelihood ratio compares0.9 solved-source empirical equalitypattern distribution +0.1 Markov background against the exact no-adjacent-repeat Markov pattern law, conditional on collapsed unit length. Source templates are nine solved rune texts; no English scorer or fitted real plaintext. Analytic canonical-pattern probability is falling_factorial(29,distinct)/(29*28^(length-1)); independent enumeration checks total probability1 for every length1..7.

1881 actual units eligible (922train/959held). Length1/2 excluded by definition;13 length12 units lack source support and are omitted. Actual train/held logLR=-358.78/-427.37; source-like held upper tail p=.992519 among400 conditional nulls. Twenty full source-model controls score708.25..859.14 on held units,20/20 above null99th percentile(-317.46); all token permutation inverses/equalitypatterns are exact. Nine leave-one-source-out transfer fixtures each also beat400 correctly rescored nulls using that fixture's exact eligible-length subset (tail1/401). They are9 fixtures, not an estimated population power or independent corpus.

The real score is in the opposite tail; that was not the preregistered positive prediction and is not promoted into a new discovery. This weighs against fresh word-alphabet transport of these source token distributions. Other source registers, different unitization, stateful/homophonic substitutions, or nonlinguistic source objects remain outside this bound. Full source hashes, input unit maps, generated permutations/source tokens/outputs,400 null outputs,9x400 transfer-null arrays and summaries are in `l2/`. `L2-CARD.md` and `L2-TRANSFER-CARD.md` specify the experiment/followup. No new bag models were added.

# L3 — one-step lookahead swap collision repair

The final operation test retained the iid draw multiset and swapped a colliding queued symbol with the next queued symbol when that next symbol differed. This is one explicit alternative to discarding/resampling draws. Its predicted second observable is excess ABA: the duplicate suppressed at the current position moves one position forward. **ABA/lag2 is an old statistic already used in campaign14/R17; L3 adds an exact new generator calibration, not a claim of new statistical novelty.**

Training doublet rate29/5109=.005676258 gives fitted swap probability s=.865223835 under q=(1-s*28/29)/29. Across200 exact controls, measured doublet means train/held=.005649834/.005688065, SD=.001099675/.001009086. The swap generator therefore matches the first-order feature within simulation error.

Its second prediction fails: held nonrepeat-ABA rate actual176/5235=.033619866; swap-control mean=.063837575, range[.057460257,.073946360]. The conditional M1 null mean=.035904489 and99th percentile=.042217765. All200 swap fixtures exceed that null bar; actual upper tail under M1=.810945, lower tail under the fitted swap model=1/201. The latter is a finite-replicate plug-in model comparison at training-fitted s, not a composite-model confidence interval. Every control preserves its raw iid queue multiset including the terminal unused buffer, and reversing saved swaps exactly recovers that input.

This weighs against the specified local one-step swap repair at fitted suppression strength. Other swap rules, latent boundaries, source distributions or output mechanisms remain outside scope. Full raw queues, swaps, emitted arrays, conditional-null arrays, per-page counts, fitting constants and hashes are in `l3/`; model definition in `L3-CARD.md`. No swap-radius expansion was performed.

## Rotation closeout

Coordinator requested freeze after L3 for a fresh review slot. L1/L2/L3 are now frozen with `evidence-manifest.json`; no experiment is running. This is worker rotation, not completion of the overall research mission. All findings are model-conditional claims, and no plaintext/solve is claimed.

Two different future questions, NOT executed: (1) whether an explicit separator-unit can encode a nonlinguistic lookup identifier using fixed checksum relationships across adjacent units, with an independently bounded checksum rule and power control; (2) whether a documented source-field procedure creates a testable directed relationship between two discovery sections, selected before fitting rather than a global generator. Check completed F/H/I/K/M/N coverage and any review findings before assigning either. They are starting questions, not ready-made positive predictions or a recommendation to expand the rejected families.
