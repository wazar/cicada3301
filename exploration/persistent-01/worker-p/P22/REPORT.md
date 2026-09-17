# P22 — delayed additive ciphertext-feedback family test
The fixed32-lag family produced no unusual held categorical prediction under the declared comparator. The largest gain occurs at lag1:0.01747302 natural-log units per held suffix rune, with full-family add-one tail0.255 against199 matched null panels. All four known-source controls identify their planted lag first and achieve tail0.01 against99 own matched nulls.

This is a bounded extension of existing additive-feedback work, not a new cipher-family discovery.

## Exact construction and prior overlap
For lagL, the raw encoder emits c_i=(p_i+c_(i−L))mod29 once i>=L. Its firstL symbols use an arbitrary seed vector. The suffix is therefore determined without seed search: p_i=(c_i−c_(i−L))mod29. Each page resets independently. Only L1..32 and this subtraction are tested; no additional sign, coefficient, key, null/interrupter rule or rejection filter is introduced.

Lag1 was already examined in first-difference/autokey work, and campaign10 also simulated lag8. C1 tested seven functions over complete histories2..6; H17/H18 used multiplicative/power feedback, and M28 combined one-step feedback with an external key and rejection clock. The new contribution here is the exact32-lag family comparison under a categorical train/held detector. It is not32 wholly new constructions or an exhaustive assertion that every lag was historically untouched.

Prefix plaintext is unresolved and excluded for each lag. Every input page is at least66 runes long, so all pages have a nonempty suffix at every tested lag. No feedback crosses a page boundary.

## Detector and family selection
First23 sorted F06 discovery pages train a separate29-category distribution for each lag, q=(count+1)/(training suffix count+29). The remaining22 pages supply mean log(29q[p]) scores. No English model, dictionary or plaintext readability criterion is used.

The primary statistic is the maximum of all32 held scores. Therefore the lag is selected using held data: this is a family-level test with the complete selection repeated in every null, not a lag selected before untouched validation. Pages are reused campaign discovery data. The source must have a stable nonuniform marginal distribution for this detector to be sensitive; a uniform source is invisible.

For lag1, training/held suffix counts are5,531/4,890; for lag32,4,818/4,208. Exact counts for every lag are retained. Actual lag1 decoded zero counts are30/27, matching the supplied repeat positions. That known deficit naturally contributes some predictability; it is not treated as new evidence.

## Actual null and result
The199 null panels preserve every page's first ciphertext symbol and exact adjacent-equality mask. At repeat positions they copy the previous rune; otherwise they sample among the other28 runes using smoothed empirical frequencies from actual training ciphertext. Every null refits all32 source distributions and repeats the full held maximum.

These weights are empirical marginals, **not** a conditional-exclusion maximum-likelihood estimate. They need not reproduce exact marginal frequencies after predecessor exclusion. This is an explicitly approximate plug-in competing generator, not a true-cipher or exact-exchangeability null. It preserves neither histograms nor longer-lag dependence.

Fifty of199 null maxima meet or exceed the actual maximum, giving51/200=0.255. No lag, sign, source or transition variant was added after this result. The lag1 gain is ordinary under this specific comparator. No plaintext claim follows from any categorical gain.

## Source-backed controls
Each control uses one complete held solved rune source as a circular reservoir, generating45 pages with actual page lengths. Fixed random source starts and independent uniform prefix seeds are retained. This deliberately supplies sufficient material at every page length, but creates shared-source dependence and repeated source content. These are not45 independent source texts.

| Source | Planted lag | Selected lag/rank | Held gain | Full-family tail | Cipher repeats |
|---|---:|---|---:|---:|---:|
|welcome|1|1 /1|0.43365849|0.01|222|
|jpg107-167|8|8 /1|0.54118510|0.01|408|
|p56_an_end|16|16 /1|0.58648258|0.01|379|
|p57_parable|32|32 /1|0.54135177|0.01|365|

Every planted suffix recovers exactly, and prefix seed arithmetic re-encrypts every full control page. The complete control sources, circular indices, original source-character positions, seeds, ciphertexts and decoded alternatives are retained. Each control uses99 nulls conditioned on its OWN masks and first symbols, with weights from its own training ciphertext.

The raw encoder has no repeat-rejection wrapper; its repeat counts exceed actual57. A wrapper can break the simple fixed-lag identity and is not covered. Fixed seed ranges overlap across different null ensembles, so some panels share random-number streams under different weights/masks. This correlation is disclosed; their control calibrations are not counted as independent repeated evidence.

## Checks, cost and retained outputs
The pilot reused one full control and its first three nulls; it was not extra coverage. All600 actual/control/null panels retain complete ciphertexts and all32 decoded suffix arrays in NPZ files, with255 sentinels for unresolved prefix positions. The600 files total127,598,393bytes; largest213,160bytes. Per-lag distributions/counts/scores, source prefixes and page/source-coordinate maps are in matching JSON and index-layout.json. There are19,200 family cells, not a seed-key search.

Controls took13.30s, actual/nulls6.98s, plus0.20s pilot and separately logged replay. All production exits are0, one numerical thread. The exact arithmetic identity was checked over all841 plaintext/feedback pairs before full work. Independent no-import replay passed all600panels/19,200lag fits, complete source/seed maps, null RNG, every decoded suffix and every categorical score. The first checker attempt was terminated after179.62s with retained exit−15 because lazy NPZ access redundantly decompressed arrays inside the loops. Caching loaded arrays was the only change; the same checks completed in24.37s. No production output changed. Review36 independently passed all600panels/19,200fits, full decoded arrays, every source/seed/null stream, all1,440 lag/page layout ranges and all tails. Its separate layout check initially confused local with flat offsets; the corrected audit passes and the failed audit log is preserved. No production defect was found. See exploration/persistent-01/review-36/REPORT.md.

No reserve, original50, image read, new corpus, install or Git mutation was used. The experiment stops at this raw additive-feedback family; no result is generalized to uniform-register messages, unstable source distributions, rejection wrappers or other feedback mechanisms.
