# M24 — frozen recency-context predictor did not transfer

On22 held discovery pages, the predefined conditional recency model scored **−0.00421828 nats per retained rank** relative to its unconditional baseline, empirical upper-tail **0.777** (776/999 nulls at least as large). Training gain was+0.00401520, so the fitted dependency did not generalize. This tests one finite recency grammar; it does not establish absence of all memory.

The two constructed rank-memory control strengthsρ=.3/.6 each exceeded the null99percentile in100/100 actual-size replicates. Minimum gains were0.02320/0.10137, against null99threshold0.0002763. Their unconditional latent rank distribution is uniform in stationarity by construction, so their separation does not depend on nonuniform marginal rank entropy. All controls/nulls exactly preserve the observed57 stutters and their positions by expanding the same runlengths.

## Question and prior overlap

OB-C2 already measured seen-symbol recency entropy and in-sample rank-pair MI; C3 recovered cross-page ranks. Campaign14 and R17/P4 measured unconditional lag/ABAB statistics, and R17's conditional_next is an offdiagonal symbolbigram chi2. H06/H07 concern delimiter grammar. L3 calibrates conditionalnonrepeat ABA mean for a local-swap encoder. M24 reuses C2's rank representation explicitly; it adds a fixed train-to-held likelihood comparison, not a claim that rank dependence itself is new.

Collapse each page's adjacent equal symbols. A previously seen symbol's recency rank is the number of distinct intervening symbols since its previous occurrence,1–28. The two context states are previousrank1–3 versus4–28. Both consecutive ranks must be known; firstoccurrences and their adjacent pairs are excluded, and pages are never bridged. Baseline28-category probabilities use pooled trainingcounts plus1 percategory. Conditionalrows use28 pseudoobservations proportional to baseline. No state threshold, smoothing, family or key search was performed.

Sorted discovery page ordinal parity gives23train/22held, reused from L and already-examined discovery data. Raw scope10,466runes becomes10,409collapsed symbols; eligiblepairs4,113train/4,364held. No reservedpage is included. The statistic is an average categorical logprobability ratio on **retained recurrent-rank pairs**, conditional on their selection. It is not a complete normalized next-rune forecasting score and does not predict firstoccurrences or stutter placement. Full predictive tables and each real eligible position's probabilities are retained; eligibility omissions are explicit.

## Constructed mechanism and null

Control state is previousrank group, not literal previous two rune identities. A full29-symbol alphabet moves each emitted symbol to front. Letπ=3/28. Transition nearprobabilities areπ+ρ(1−π) afternear andπ(1−ρ) afterfar, with uniform choice inside each group. Groupstate is initialized atstationarity; πP(near|near)+(1−π)P(near|far)=π, preserving uniform marginal latent ranks. This is finite adaptive MTF memory, not a literal order2 rune Markov chain, not a plaintext/key hypothesis and not an English-register detector.

Nullρ=0 selects uniformly among the28 nonprevious symbols, starting from a uniformly random initialpermutation. Every page is generated independently at its actual collapsedlength, then expanded through its observed runlengths. Thus the exact repeatmask is conditioned out; symbolhistograms and higherorder structure are not fixed. Every one of999 nulls and200 controls repeats extraction, eligibility, trainingfit and heldscoring. The pooled cross-page model can miss different/opposing page-specific grammars, other rank partitions, higher-order dependency and memory affecting only discarded firstoccurrences.

## Evidence and checks

Primary run completed17.19s logged wall,11.57s to finish simulation/scoring before serialization. `generated-evidence.npz` preserves all1,199 generated collapsed outputs, latent ranks and initialalphabets with pagelengths; `replicates.json.gz` preserves every probabilitytable, fit/held/perpage count and score. `input-manifest.json` carries source SHA256, all sourcecoordinate maps and collapse/runlength maps; `real.json` gives actual perposition probabilities and eligibility. Seed330824/PCG64 and finalstate recorded. There is one frozen primary model.

`check.py` independently reconstructs real ranks from sets of intervening symbols, replays allgenerated outputs from alphabets/ranks, checks every expanded repeatmask against the actual page, and recomputes1,200 predictive-table scores and the null tail using a scalar formula. It also records latent marginal calibration separately from the predictive statistic. See check-result.json/latent-calibration.json and logged commands/exitcodes.

Decision: checkpoint this one grammar with measured control power and no real predictive signal. No rho/state/threshold expansion. Continue with a materially different source-backed question; no broad no-memory verdict.

Replay completion: cached evidence replay PASS in4.55s, covering all1,199 generated outputs/1,200 fitted tables. The first checker repeatedly reopened compressed arrays inside loops; it was terminated before completion and preserved as a NONZERO logged run. Caching those same arrays fixed checker I/O only, without changing scientific code/results.
