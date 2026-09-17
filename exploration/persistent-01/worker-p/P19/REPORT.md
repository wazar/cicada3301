# P19 — fixed glyph-shape avoidance model
The frozen model did not produce a compelling predictive gain on the held pages. Training estimated beta=0.0125800295; held gain over the baseline was0.28681728 natural-log units across4,863 nonrepeat transitions (0.00005898 per event). Both actual fits satisfy the predeclared optimizer qualification.

The full null procedure is **unqualified**, because two of99 null fits miss the fixed projected-gradient tolerance. The reported tail remains null. Treating those two outcomes as unknown gives a conservative rank-tail interval[0.12,0.14], entirely above0.05. This is an approximate plug-in bootstrap comparison, not an exact finite-sample p-value even if all fits had qualified. No tolerance, optimizer, metric or replica count was changed after the results.

## Frozen mechanism and inputs
The hypothesis is that visual similarity influences which rune follows another, beyond exact-repeat suppression. R04's29 training-only mean glyph templates, built from original0/1, supply fixed zero-angle/zero-translation32x64 normalized grayscale features. Shape classes1..29 are **not** rune IDs: I's conflict-free bijection reorders the bank into canonical0..28. Inputs and this mapping are pinned in inputs.json.

Pairwise RMS is centered/scaled using all812 ordered off-diagonal distances, mean0.60277577465 and population SD0.12137303446. There is no learned metric, alternate orientation, pairwise registration or post-result metric selection. Template extraction/identity errors and unequal template counts remain inherited limitations.

Train pages are the first23 sorted F06 discovery pages,0 through27 with reserves omitted. Held pages are the remaining22,28 through55 with reserves/50 omitted. Original0/1 template ancestry is contained in training. These are reused discovery data from this campaign, not untouched external validation.

Conditional on a nonrepeat, successor probability is proportional to exp(a_j+beta D_ij), excluding j=i. Both baseline beta0 and alternative beta>=0 jointly fit28 nuisance symbol weights, with a_28=0. First symbols and each page's actual repeat mask are conditioned upon; repeat events copy the previous symbol and have no likelihood contribution. No page joins, source words, English model or key are used. Training and held nonrepeat event counts are5,501 and4,863. Thus the already-known scarcity of exact repeats cannot itself favor the visual term.

## Controls and cost
Forty complete planted panels use fixed nuisance weights sin(j)/4 and beta0.25 or1 (20 each). Every panel fits both models on its own training data and predicts held pages. The99 shared beta0 controls use the same fixed nuisance law, masks and first symbols. All139 control panels satisfy optimizer qualifications.

| Planted beta | Held gain range | Fitted beta range | Tail<=0.05 |
|---|---:|---:|---:|
|0.25|62.57587 to106.90496|0.19468 to0.28123|20/20|
|1|844.10946 to965.57148|0.94971 to1.06279|20/20|

Every planted tail is0.01 against the shared99 nulls. The shared reference makes these power outcomes correlated; they are not40 independent calibrations. Control null gains range−2.66572 to1.47216. These controls show sensitivity to the specified moderate/strong law, not every visual or human selection mechanism.

Six pilot panels took0.05954s of panel computation and are reused, not counted twice. Full139 control panel computation totaled1.38982s; logged control and actual batches took2.35s and1.88s including startup/write overhead. All fixed replica counts were retained. No run exceeded900s or used multiple numerical threads.

## Actual nulls and qualification
The99 actual null panels are generated from the actual TRAIN-fitted baseline weights, preserving every page's first symbol and exact repeat mask. Both models are refit on each generated training set; the same held gain is computed. These nulls preserve neither rune histograms nor an independently established true cipher generator. Estimated nuisance parameters make this a parametric bootstrap.

Actual baseline/visual projected-gradient infinities are2.5355e-8 and9.8113e-8. All optimizer statuses report success, but the frozen qualification additionally requires projected gradient<=2e-6:
- actual-null-090 visual gradient2.300535e-6;
- actual-null-095 visual gradient2.660157e-6.

Both terminate on SciPy's relative-objective condition, which is insufficient for our stricter gate. Their raw gains are retained unchanged. Eleven qualified null gains meet or exceed the actual gain. Add-one ranks range(1+11)/100 to(1+11+2)/100, or[0.12,0.14], if either unknown fit could lie on either side. Raw unqualified rank is0.12 and is explicitly not substituted for the missing qualified tail. summary.json retains qualified=false and tail=null.

## Replay, retention and scope
An independent implementation in p19_check.py reconstructs the metric by scalar loops, simulates every saved stream with scalar cumulative probabilities and recomputes every page's conditional log likelihood. It checks all239 actual/control/null panels and2,466,632 random draws. Metric max discrepancy5.77e-15; score max discrepancy2.27e-13. Synthetic finite-difference gradients agree within6.20e-10; independently summed objective agrees within5e-15. Complete sequences, parameters, gradients, optimizer status, likelihoods, source hashes and command logs are retained (about26.5MB).

Review29 independently passes reconstruction of all239 panels,238 generated streams, the rune-mapped metric, all scalar likelihoods/gradients and qualification decisions. It confirms the two failed fits and[0.12,0.14] interval without requesting repairs; see exploration/persistent-01/review-29/REPORT.md. No new image was read, and no reserved page or original50 was included. R04's orientation detector and R02's successor inventory tests were checked narrowly for overlap; neither is this shape-dependent conditional successor model. No exhaustive claim about all historical work is made.

This measurement gives no useful support for the specific fixed RMS avoidance law at the planted effect sizes. It does not establish independence, human authorship, a cipher family, or absence of other visual mechanisms. The experiment is frozen without optimizer repair or metric expansion after the result.
