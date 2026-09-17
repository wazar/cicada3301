# Review63 — Q12 scoped PASS

Independent review of the frozen Q12 arbitrary-seed sum-autokey experiment passes. No scientific defect was found. This review independently recomputed all **46,880,704 seed scores** by forward recurrence, rather than reusing Q12's periodic factor-table search. All 64 packets passed. The largest score discrepancy was 1.865174681370263e−14; all **18,730,752 factor cells** matched exactly. Exact finite enumeration remains subject to ordinary floating-score precision.

## Scope and independence

`check.py` imports neither Q12 nor P03. It reconstructs the English rune/boundary LM from the five pinned P03 training sources, with a separate character-by-character run parser, count accumulation and interpolation. All 27,000 log-probability cells match. The training names, held source names, rune alphabet, smoothing constants, boundary handling and normalization were also checked against `worker-c/p03_frozen.py`. This validates those source-derived tables; it does not make their English register language-neutral.

For each k=2,3,4, the independent vector scan enumerates every seed in batches and directly advances p_i=c_i−seed_i for i<k and p_i=c_i−sum(previous k plaintext) thereafter. It checks every saved score, zero-seed trajectory, global maximum, all 3,072 retained per-family paths, and all 1,024 selected global alternatives, including seeds, index conversion, offset periods, complete plaintext and re-encryption. Top16 ordering uses the saved float arrays after independently bounding every score; maxima independently agree within the stated numerical error. Whole-family distinct-plaintext selection and cross-family aliases were checked. Factor tables were separately reconstructed from an expanded rune/boundary token reference stream.

The independent scalar fixtures cover 10,933 seed-score comparisons, 180 fresh arbitrary-seed periodic fixtures and the 60 saved random production fixtures. Boundary-free, every-rune and irregular-boundary tiny inputs are included. All checks passed. Exact source words/maps and every null RNG stream were verified for originals 0/17/55; no reserved source was introduced.

## Mathematics and observed results

The recurrence proof in `MATH.md` is confirmed under Q12's explicit initial-seed convention. Subtracting two consecutive zero-sum blocks of k+1 errors yields e_i=e_(i−k−1). The free first k errors equal the negative seed, and the last error equals its seed sum. Thus all 29^k seeds are represented. Seed errors generally persist periodically; the claimed automatic seed lock-on does not hold for this construction. This does not assert anything about other feedback rules.

All four complete held-source controls were recovered exactly at global seed rank 1. The minimum rune errors achievable by the 29 equal-component seed vectors were respectively 343/515, 239/319, 51/85 and 57/95. These diagnostics substantiate why restricting to equal seeds is inadequate for these planted cases.

| Original | Actual maximum | Null maxima at least actual | Smoothed tail |
|---|---:|---:|---:|
| 0 | −4.513828494966559 | 3/19 | .20 |
| 17 | −4.549503590003141 | 17/19 | .90 |
| 55 | −3.9806028305721983 | 4/19 | .25 |

The null holds the first rune and the complete adjacent-equality mask fixed, selecting uniformly among the other 28 symbols at each required inequality. It does not preserve histograms or wider correlations. The full 732,511-cell search is repeated for each null. These are bounded English-score comparisons for k2/3/4, this orientation/sign/sum recurrence, and no F/skip mechanism. They neither solve a page nor exclude other registers or constructions. This review validates arithmetic and selection, not semantic readability of every output.

## Preserved amendments and reviewer failure

Q12's original control generator drew [1,1,1] for control1 and stopped before actual work because the frozen card required nonconstant seeds. `CONTROL-AMENDMENT.md` records continuation of the same RNG stream to [11,23,24]. The reviewer independently reproduced both draws and every other control seed; control0's older cache legitimately lacks the new draw-list field. No scientific search setting changed.

The first review aggregation failed on a missing `independent_seed_draws` field in the reviewer's pilot-era control0 report. The final checker was already amendment-aware. Control0 was replayed under that checker, and aggregation then passed. Both logged runs are retained; no Q12 data or algorithm was edited. The earlier temporary pending/platform-error status is historical and is superseded by this completed review.

## Reproduction and provenance

`result.json` contains complete aggregate counts, errors, seeds/draws, control metrics and tails. Each `<packet>-review.json` records source artifact hashes and per-family independent score-array hashes, maxima and errors. `manifest.json` pins the reviewed card, amendment, code, LM, F06, all 128 packet JSON/NPZ artifacts, training and held sources. The three actual summary files were compared exactly to independently reconstructed counts. Q12's final prose report was not yet available at review freeze, so this PASS covers its card, code, fixtures and scientific outputs rather than an unseen later report.

To repeat a full numeric review before the fixed deadline, remove only copies of prior `<packet>-review.json` outputs in a separate review directory or run the `panel NAME` mode for every packet; `all` intentionally resumes by skipping already reviewed packet names. The logged pilot, controls, actual, control0 refresh and final aggregation commands preserve the exact original invocations. Each job obeyed one numerical thread, the existing STOP/deadline checks and the ≤900-second logger cap. No source changes, new searches, images, external queries or Git actions were performed.
