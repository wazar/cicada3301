# Review08 — M22 exact short-key kernel and optimization witness

**NO-ERROR-FOUND within the reviewed period1–3/literal-F/English-LM scope.** The saved p56 period3 case demonstrates a genuine key-optimization miss by the inherited heuristic, independently reproduced. This is a capability finding, not a puzzle decode or new search result.

## Independent arithmetic and state argument

Reconstructed the27000-entry P03 log-probability table directly from the five hashed training source files, using an independent rune/boundary parser and counter implementation. All30-token conditional probability rows normalize. Worker Python scorer/decoder modules were not imported. Table, hashes and source dependencies are saved.

Copied the inspected scalar C source into this review directory and compiled there with recorded `cc -O3 -std=c99 -dynamiclib` command, compiler version, exit code and complete stdout/stderr. `exact-local.dylib` is a **local rebuildable binary**, not a portable artifact. Source hash and independent LM table hash are retained.

All1296 tiny fixtures agreed with independent literal-F-mask enumeration (3072 masks): every length3 cipher over{0,1,28}, all8 boundary masks, periods1–3, both the real LM and an arbitrary asymmetric objective table. Separately checked scanner index/order and score for every870 period1/2 key on a tiny fixture. A second independent DP that retains **absolute consumed-key count**, rather than merging modulo phase, reproduced selected prefix and conditional suffix objectives for all12 controls and both real records; decoded paths, consumed counts, boundary contexts and re-encryption agree.

State equivalence is valid at a fixed input position/key: two histories with equal consumed-key phase and lasttwo LM tokens have identical next plaintext options, phase updates, token scores and future boundary schedule. The denominator depends only on fixed rune count and boundary count, so maximizing cumulative numerator preserves the same optimum. Keeping only the better history is therefore safe. At period<=3 there are at most3*30*30=2700 states, matching allocated capacity. This proof does not cover period>3, a richer history-dependent model, a changed key-clock rule or marginal path probability. Best endpoint paths are not a global top16 path list.

## Optimization witness and scorer errors

For p56 period3, independent enumeration of its two prefix literal-F masks gives:

| Key | Exact prefix score |
|---|---:|
|Planted[27,20,28]|−2.3011426937815616|
|Heuristic[20,28,27]|−2.495426094180916|

The gap is **.19428340039935454 nats/token**. The heuristic score equals the exact optimum at its own selected key, so this case is a key-optimization miss, not beam loss at that key. One replay of all24389 period3 scores agrees with the saved array; no additional periods or all440-search rerun was performed.

Independently verified the stated incorrect prefix-score winners despite correct period1 keys: welcome3 errors, p56 one, p57 one. Their winning scores respectively exceed true plaintext scores by.01022954,.04474457,.02741662 nats/token. All12 saved suffixes reproduce the source plaintext exactly. Thus “exact optimization” must not be summarized as universal correct-path ranking; M22 already states this distinction.

## Selection, leakage and counts

Inspected prefix search uses only the firstfloor(N/2) ciphertext runes and their declared boundary indicators. It freezes selected key and the chosen prefix path's LM context/key consumption before suffix decoding. Independent path replay reconstructs those boundaries. The saved suffix-mutated experiment retains identical exhaustive prefix arrays, training paths, selected key and boundary while replacing every suffix rune. No suffix-to-prefix key/boundary leakage was found under this fixed boundary schedule.

The suffix score maximizes over suffix literal-F paths; it is a **conditional maximum-path score**, not a normalized predictive likelihood. Source/control register and full boundary schedule remain conditioning information. The null repeats this optimization, so interpreting only the calibrated comparison is appropriate.

Verified all440 primary output names and retained score arrays. Each saved null output matches its indexed score/key and preserves the original F positions, nonzero multiset and boundaries. Recounted all tails: controls12/12 attain.05 with19 nulls; real0/17 remain.57/.49 with99 nulls. This does not establish control p<.01 or calibration against an adjacent-repeat-preserving generative null. It is the stated nonzero-order permutation comparison.

Enumerating length6 representative streams independently yields25259 nominal keys and25201 distinct infinite streams. The58 duplicates are the29 constants repeated at periods2 and3. Period2 and3 have no other common infinite sequences. Key rotations represent distinct origins, not extra searched offset factors. Primary nominal count11,113,960 follows440*25259; pilot and saved suffix-isolation check are separate.

## Disposition

Retain M22's qualified capability claim and recorded miss. No numerical correction is required. Keep the three conditionals prominent: periods1–3; optional literal ciphertextF consuming zero key symbols with additive decoding otherwise; frozen English rune/boundary LM. It does not test repeat-rejection clocks, non-English scoring or longer keys. New local binary/table, independent fixtures, compiler records and findings.json are in this review directory. No reserved input, Git mutation, nested worker or active computation; logged review batch.607s, one numerical thread. Release the review slot.
