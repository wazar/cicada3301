# Review56 — Q10 reverse reciprocal fitting and Q11 uniform reference

The completed independent review passes all600 reverse panels/1,200fits, profile comparisons, null accounting and all600 constant-reference calculations. Review54's exact original Q09 scientific hashes match every source reference, so its full source/RNG/decoded-array validation applies to these unchanged inputs. No new draws or optimizer reruns were performed.

## Reverse fit and profile comparisons

Independent raw sequence counts use last22 pages for training and first23 for prediction. Every reciprocal/destination conditional row, objective, analytic gradient and held likelihood agrees. Maximum objective/gradient discrepancy7.99e-15; largest normalized gradient9.90e-7 remains below2e-6. All qualification flags agree. These are saved-optimizer stationarity checks, not an alternative optimizer execution.

Normalized q profiles reproduce from the same gauge-fixed logits in both directions. Jensen–Shannon divergence was independently evaluated through entropy differences, rather than the producer's summed likelihood-ratio formula. Every profile, source-truth divergence and full-procedure null rank agrees. Training selections are absent: the same one reciprocal formula is fitted in both directions, with no exponent/key choice.

Actual forward gain+5.92203720 and reverse+12.64524891 sum to+18.56728610; the nominal upper tail is .010. Actual JS divergence .00109733877 has lower-tail .245. The controls have large positive gains in both directions, but JS lower tails .55/.28/.05/.85 show weak discrimination of profile stability under this chosen summary. The actual JS rank must not be interpreted as a demonstrated instability failure; the statistic lacks a strong control gate for that inference.

The two directions share the same panels, and this follow-up was selected after the original exploratory result. The original-direction baseline continues to generate the reused nulls. No nominal rank is a campaign-adjusted pvalue or independent untouched replication.

## Zero-parameter reference

At a nonrepeat position, uniform over the28other symbols gives log probability−log28; observed repeats and starts remain conditioned and contribute nothing. This supplies an exact zero-fit reference on each held sequence, not a new fitted model or null selection.

| Actual direction | Events | Destination minus uniform | Reciprocal minus uniform |
|---|---:|---:|---:|
|Forward|4863|−15.45811229|−9.53607509|
|Reverse|5501|−15.68842422|−3.04317531|
|Combined|10364|−31.14653650|−12.57925040|

Both fitted models predict worse than this constant reference in both directions. Reciprocal fitting loses fewer nats than destination fitting, accounting for its relative improvement; it does not beat uniform here. This is consistent with relative gains arising from differing estimation costs or distribution shift, but does not uniquely prove either explanation. Q11 is a descriptive model-adequacy comparison after exploration, not a newly selected significance test.

All600 independently calculated reference rows match Q11 all-panels.json, including1,200input hashes, event counts, both model/direction values and combined values. All full saved outputs remain available; no candidate plaintext was identified or inferred from q.

## Retained audit error and scope

The first reviewer run stopped at the first panel because reused audit code still counted the original training split while checking the reverse fields. Its NONZERO log and source snapshot remain. The correction changes only reviewer counting to last22/first23, then all600 panels pass. No production data, fit, threshold or source changed. The source error is not a Q10 failure and is not hidden as a clean first-pass review.

The corrected full replay took3.43s; separate Q11 comparison0.025s. Inputs, scripts, original failure, results and snapshots are preserved. No reserve, new key/model family, Git/shared-file mutation, image/software-format work or post-result retuning occurred.
