# Independent J02/J03 review — accepted within stated finite scope

Strategy outside-box-v1. Manifest hash ACK: `2f079f4539954bebba440fa78085035a2b22a6bbfe97bd2628b3bb622ead9283`; all 69 pinned files matched. No worker scientific functions imported. No reserved pages read, new hypothesis sweep, Git invocation, external controller, or subagent. No active process remains.

## Independent derivation
For n occurrences assigned to k disjoint output symbols, balancing loads minimizes pair collisions: moving one occurrence from a load a to b with a>b+1 reduces collisions by a-b-1. Therefore optimal loads differ by at most one. Equivalently the minimum is f(n,k)=sum over positive integers j of max(n-j*k,0). If m=floor((n-1)/k), this is mn-k*m*(m+1)/2, equal to the familiar quotient/remainder formula.

Each summand max(n-j*k,0) is convex in k, so successive collision reductions f(n,k)-f(n,k+1) are nonincreasing. Start each present source type at one slot and repeatedly award the remaining slots to the largest current reduction. Every type offers a nonincreasing chain; choosing the largest available reduction selects an optimal prefix-constrained set of reductions. An exchange argument gives global optimality. This is independent of the worker's dynamic programming recurrence. We verified 6,216 small count-vector/slot cases against exhaustive allocation enumeration and discrete convexity for n=1..999, k=1..30.

The result is exact for the relaxed allocation problem and a necessary collision bound for the stated cipher. It is not an exact ciphertext-count partition test. Arbitrary order/transposition cannot change collisions. Zero-count source types receive no reserved slots; every window/page receives its own optimal allocation. A shared fixed codebook may impose stricter constraints. Balancing realizes the minimum but need not realize a specified observed output-count vector.

## Executed checks
One logged 1.807-second single-thread numerical process, exit 0, checked all 14,602 stored windows from their original solved-source sequences, 149,985 sampled page count/bound records (29,997 bundles), both pooled profiles, all 115 saved attainment controls, and every selected p17 one-edit sensitivity value. It checked sample count totals, retained minima/medians, zero compatible sampled bundles, and window-reference coordinates. It did not reproduce the original RNG sequence or independently re-transcribe source images.

All nine original solved files matched their pinned hashes. Direct parsing reproduced J01's +1 mod29 rotation; reversal before transliteration was correct. All 29 transliterations matched documented KNOWLEDGE.json Gematria Primus entries. All J03 expanded values and letter-to-rune maps reconstructed exactly. Thus the observed representation sensitivity is not a rotation or mapping bug. Same four sufficiently long files enter both window ensembles, with different window counts and weights.

Python arbitrary-precision integer histogram convolution independently reproduced:

| Model | Aggregate bound <=5196 | Every page individually compatible |
|---|---:|---:|
| J02 | 53840670648 / 5152806016252125 = 0.000010448806044354222 | 0 |
| J03 | 427074721435572 / 8232458629504005 = 0.05187693502703975 | 686511374400 / 8232458629504005 = 0.00008339080769135446 |

Window totals were J02 [1325,1309,1505,1541,1281] and J03 [1461,1445,1641,1677,1417]. Individually compatible counts were [42,53,30,370,0] and [285,424,129,1468,30]. All per-source weights are retained in results.json. Integer convolutions have nonnegative terms and total mass equal to the product of window counts. Every intermediate total is bounded by the final denominator, itself below 2^63; original int64 overflow concern is resolved for these inputs.

J02 page17 minimum1261 versus observed1256 is reproduced. The selected minimum window admits exactly52 one-source-symbol substitutions reaching <=1256, with minimum1252. This verifies fragility rather than robust language exclusion. J03 page17 has30/1417 passing windows and minimum1248.

## Interpretation and next useful test
No arithmetic correction is required to the latest J02/J03 reports. Accept representation sensitivity and the finite count obstruction; reject any reading of 5.19% as language/cipher probability, positive cipher evidence, or exact partition feasibility. The aggregate is much weaker than the conjunction because one favorable page offsets another unfavorable page. The conjunction should accompany every use of the aggregate.

The probability measure is independently sampled, uniformly weighted windows per page, not independent naturally generated pages or uniformly sampled source files. Overlapping windows are not independent empirical observations; independence of page draws is an imposed model assumption. Expansion changes window boundaries, represented passage lengths, and source weights, in addition to source support, so the observed probability ratio cannot be attributed solely to alphabet size. Source files, page choice, initial observations, and adaptation are shared. This is a fresh arithmetic implementation, not fresh blind validation. The prespecified J03 5% decision threshold is a local heuristic after J02, not a calibrated significance threshold for the overall exploratory programme.

Next useful real test: freeze a necessary exact count-partition check on these same discovery pages. Given a source-window count vector and 29 observed ciphertext symbol counts, ask whether output symbols can be partitioned into disjoint groups summing to each source count. First test planted attainable and impossible controls, then all conjunction-eligible J03 windows pagewise; preserve complete certificates or bounded-search status. If any survive, require the same letter-to-output assignment across pages before claiming a shared codebook. This can reject collision-compatible samples without linguistic scoring. It still cannot establish plaintext or reject other source registers/encodings.

Raw logs: runs/20260916T210801.766073Z-independent-capacity-review/{command.json,stdout.txt,stderr.txt}; code check.py; results results.json. Logger was copied before coordinator clarified read-only git rev-parse was allowed; copy changes root resolution and replaces commit read with an explicitly unverified config-entry label. This deviation is retained honestly, not represented as the standard logger. Future runs should use the standard logger. Review is complete and slot is free.
