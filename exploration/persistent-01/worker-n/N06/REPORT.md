# N06: fixed-candidate model-matched discrimination succeeds

The true codebook strictly beats all eight frozen alternatives on every one of 1,600 new model-generated samples, separately on prefix, conditional suffix and full likelihood. There are no numeric ties. This is a likelihood discrimination result with the truth supplied among nine maps; it is not unknown-map recovery or a real-page result.

Before simulation, CARD.md was frozen at SHA256 `61278bf0e12c128d4dd14371f4f97ace894aba7f3041e39f49decc1b2ea7269b`. There are 100 fresh independent draws for each of P05's 16 truth codebooks at the original length and cut. Each keeps its same eight saved competitors. All source/emission RNG seeds, every uniform draw, complete plaintext/ciphertext, nine maps, decomposed scores, rank margins and equivalence diagnostics are retained in records.json.gz/results.json. Exact source/control snapshots and hashes are local. No optimization, parameter fitting, source replacement or real-page rerun occurred.

| Original source group | Length; prefix/suffix | Prefix strict wins | Mean/min prefix margin | Suffix strict wins | Mean/min suffix margin |
|---|---|---|---|---|---|
| 0_welcome | 324;216/108 | 400/400 | 284.17 / 216.05 | 400/400 | 139.29 / 100.89 |
| jpg107-167 | 195;130/65 | 400/400 | 172.77 / 125.19 | 400/400 | 83.86 / 56.67 |
| p56_an_end | 54;36/18 | 400/400 | 49.98 / 18.21 | 400/400 | 22.92 / 4.32 |
| p57_parable | 62;41/21 | 400/400 | 50.83 / 20.98 | 400/400 | 24.73 / 5.70 |

Margins are truth minus the best of eight alternatives, in nats; prefix and suffix competitors can differ. Every original codebook independently has 100/100 strict prefix, suffix and full wins. All nine maps in each set are distinct; none equals truth, and there are no observed-label equivalences on either partition. Prefix selection therefore always selects truth, giving suffix plaintext accuracy 100% and selected-minus-truth suffix score zero. Full-likelihood wins are also 400/400 in each group. Per-codebook ranks, pairwise mean margins, minima/maxima and all raw sample outcomes are saved.

The 1,600 draws are independent conditional on their fixed codebooks and one shared fitted source model. They do not provide 1,600 independent validations of that model on natural language. Per-codebook 100/100 successes give a one-sided exact 95% lower success bound of approximately .9705 if that codebook's specified generator is taken as the sampling population; combining groups into a universal natural-language power claim is unwarranted.

These outcomes contrast sharply with P05D's actual held-source truth ranks: only 2/16 top, and all eight shortest controls last. The same likelihood readily discriminates those same frozen competing maps at those lengths when the plaintext actually follows its source model. Thus finite sample length alone, against these fixed competitors, does not explain the original failures. Source-distribution mismatch is supported as an explanation. It is not uniquely identified: original competitors were adaptively optimized on their particular original samples, whereas these new samples are fresh. Searching new alternatives per simulation could expose substantial selection bias and additional near-equivalent maps. The test does not quantify that unknown-map optimization problem, recover real plaintext, or exclude another homophonic register/transition mechanism.

Verification uses a separate script: it replays every random draw from its recorded seed, checks inverse-CDF source choices and emission choices, and independently aggregates unigram/trigram and emission-event counts to reproduce all 28,800 map-by-partition scores. Both logged batches exit zero. The simulation took 2.243s. Original P05/P05D failures and the 16 control inputs are preserved; no failed run was replaced.

Next actual direction: leave this frozen LM-only homophonic search rather than raise its optimizer budget. Root has selected a distinct finite-state control-symbol alternative, which changes the emitted representation/transition mechanism and can receive its own exact controls. The immediately assigned bounded task is independent review13 of M28's historical clock correction; N06 does not automatically launch another search or generalized framework.
