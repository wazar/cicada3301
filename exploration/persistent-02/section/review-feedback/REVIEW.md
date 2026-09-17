# Fresh feedback review checkpoint — 2026-09-17

Reviewer is section worker A, who did not author these feedback implementations. Writes are confined to section/review-feedback and section logger runs. Earlier A07 arithmetic was reviewed by the separate worker now authoring reset-feedback; that worker did not self-review the new implementation.

## Shared-seed literal-F reset decoder (C08)

Core arithmetic cleared. `check_reset_literal.py` independently enumerated 120 complete seed/mask cases over alphabets 2/3/5/29, seed lengths 1–3 and ciphertext lengths 0–8, with random boundaries/resets, integer/float weights, empty inputs and seed aliases. Every returned path matches direct recurrence and score, global partition maximum matches exhaustive enumeration, block sizes 1 and 5 return identical alternatives, and the state cap raises an explicit MemoryError rather than pruning silently. Immutable seed identity remains in the packed state while reset clears only normal history. This addresses the coordinator's seed-forgetting witness. Maximum exactness is over supplied complete seed partitions; retained outputs are final-state representatives, not an exhaustive n-best/tie census.

Initial reviewer run completed arithmetic but failed while serializing a numpy integer. Corrected reviewer serialization and reran; both logged versions are retained. This was not a research-code repair. Control-driver/representative-plant review remains pending at this checkpoint.

## No-literal-F shared-seed reset factors and bounded optimizer

Cleared for actual work after author capability checks. Independent direct recurrence, cyclic-offset identity and factor scoring passed 1,440 checks across k2–8, including short segments, consecutive resets and reset at zero. Six arbitrary dense W/B problems at k2/k3 were independently exhaustively optimized; 12 capped/uncapped comparisons verified feasible lower and upper containment and uncapped certificates. Non-boundary resets reject explicitly. Source review confirms cross-reset B factors are conditioned on x0 and added once: j>=2 in suffix unaries, j0/1 in closure. No score-context reset is introduced.

`check_reset_inputs.py` reconstructs all 44 frozen plants from the RNG and A07 source fixtures, checks all 20 actual/comparator arrays and major-marker sites, verifies source hashes, and matches every one of 54,000 scorer-table cells to the two frozen models. `check_reset_plant.py` independently reconstructs all 16 representative control00/P03 alternatives and their scores, confirms its leader equals truth, and compares saved complete W/B/q arrays. `actual.py` source review confirms prefix-only fitting, unchanged seed/rule continuation, and full-minus-prefix score totals with carried context and correct explicit-separator denominators. Caps remain bounded-search limits, not certified exclusions. No new scorer or seed band is authorized by this review.

## C09 shared-period aggregate

Cleared before reading the actual aggregate. Twenty independent scalar aggregation/permutation cases include constant columns and tied rank-one panels. All 15 control books/675 units are reconstructed from pinned sources, author/k/page order, source-slice starts, uniform plaintexts, independent seeds and background generation. The 135,000 comparator/background RNG seeds are unique. Three representative control00 feature columns are recomputed from direct zero-seed recurrence and collision histograms for every panel (600 numerator cells), matching denominators, standardized feature scores and the complete saved aggregate.

The aggregate sums same-k page features with equal weights, includes every k with at least two eligible pages, standardizes pooled panel columns and ranks conservative ties. It reuses C07 evidence and its first-rune/equality-mask comparator assumptions; it is not additional seed coverage or independent confirmatory significance. Exact constant-column range checking avoids floating-point pseudo-variance. No arithmetic blocker found. Coordinator may record its clearance marker referencing these files; reviewer did not write outside the owned lane.

### C08 pilot and carried-state addendum

Control adapter now cleared: all eight plants independently reproduce RNG seed draws, fixed literal masks, reset sites and ciphertext, and both loaded model tables equal the separately frozen tables. The complete representative welcome pilot has 29 partitions covering 841 seeds; all 464 retained paths independently re-encrypt and reproduce scores exactly, and the aggregate maximum equals the partition maximum. Its selected plaintext is exactly truth. `literal-plant-review.json` records these checks.

The subsequent optional initial-history/context extension was reviewed against the preserved prior source. One hundred additional exhaustive-mask cases test arbitrary histories of length 0 through k, arbitrary valid context, suffix-zero and internal resets, alphabets 2/3/29 and k1–3. Maximum and every retained path match direct enumeration. `literal-carried-review.json` retains the cases. Seed-slot metadata counts suffix use in these continuation calls; it must not be described as complete prefix-plus-suffix usage.

### Reset-feedback summary addendum

Independent summary reconstruction checked selection across all 320 cells/80 panels, the fixed k5–8 band, prefix-only selection and all lower/upper/conservative-tie rank counts. All 320 cells report certified bounds. `reset-summary-review.json` records this targeted check; no full ordinary-negative searches were rerun. A rank of 1/20 is neither a probability nor a proof of plaintext, and this review does not convert incoherent leaders into candidates.

## R02 histogram-conditioned sensitivity

Cleared sampler and controls-first scoring adapter. Independent review used six complete conditional state sets, including frozen/reducible examples, to compare the actual local step against full-sequence equality checking. Exact integer matrices obey symmetry and row mass. Three-step hub kernels produce identical three-endpoint joint probabilities under every permutation, and conservative tied ranks obey the small exact check. The theoretical construction is the reversible parallel method in [Howes §3.1, Proposition 3.3](https://arxiv.org/html/2310.04924v2#S3.SS1), read directly during review. Conditional exchangeability needs stationarity and the reversal construction, not a mixing claim; the resulting rank need not estimate an independently sampled uniform tail. Adaptive choice of the sensitivity still precludes a programme-wide significance claim.

All 105 real endpoints (five original-plus-19-spoke sets and five hubs) preserve rune inventory, exact F sites and adjacent equality. All 100 trace metadata records match frozen chain lengths/seeds/acceptance counts. Fifteen complete hub/spoke walks were independently RNG-regenerated and replayed: 1,074,000 proposals, including rejected self-loops, exactly reproduce outputs and changed counts. Frozen source and trace hashes match. `histogram-sampler-review.json` preserves results.

Adapter source retains the same keys, models, horizons, normalization and prefix-only selection as R01. Actual endpoint zero reuses the original pinned cells. The controls-first guard precedes actual scoring. All retained outputs in one complete observed-control panel's sixteen cells independently forward-encrypt and reproduce fit/full/prefix totals and continuation scores; pins match. `new-adapter-review.json` records this. No clearance claims mixing or plaintext recovery from a rank.

## C10 fixed known feedback seeds

Core and plants cleared: 140 independent full-mask cases cover k1/2/8/13, alphabets 2/3/29, short/empty text, arbitrary carried normal history/context, resets, score ties and float weights. Block sizes 1 and 4 reproduce the same outputs; explicit state/time refusals work. Every frozen plant identity follows the existing canonical two-key grid and eight source truths, including exact literal masks/reset marks. All retained paths in 32 model/plant results independently re-encrypt and rescore. See `fixed-reset-review.json` and `new-adapter-review.json`.

`fixed_reset_actual.py` source review confirms last-k normal history and scoring context continue across the prefix cut, combined outputs forward-check, and resource refusals cannot enter complete rank summaries. Its max-over-two-key continuation rank selects among two separately fixed-key predictions by continuation score; this is the symmetric exploratory statistic explicitly preregistered, not one key selected from prefix alone. Per-key continuation results must stay separately labelled. No arbitrary key-length sweep is implied by these two source-supported vectors.

### R02 final aggregate/reuse check

`histogram-summary-review.json` independently reconstructs all 400 panel selections and fit/continuation rank counts from the 1,600 preserved cell records, including lower/upper bound intervals and conservative ties. All sixteen reused actual records match every original field and SHA-256; 1,584 cells are new. No optimization was rerun. This clears the final aggregation for publication without changing the sampler's adaptive interpretation or adding draws.

## C11 emitted-history feedback

Core and adapter cleared for the declared k2/3/no-reset construction after author capability assessment. Seed phase counts normal emissions; the history includes every emitted rune, including literal F. These are separate state variables. Independent enumeration covered170 cases (100 unknown complete-seed×mask cases and70 fixed-seed carried-state cases), including history filled before seed completion, arbitrary context/boundaries, integer/float weights, blocks1/4, and resource refusal. Every retained path and maximum matches the scalar recurrence. `emitted-review.json` preserves cases.

All32 frozen plants retain the exact C05 source truth/seed/literal mask and change only ciphertext plus transition diagnostics. Independent encryption and64 opposite-construction decode/error checks match. All16 representative plant00 returned paths forward-encrypt and reproduce frozen-table scores. `emitted-plant-review.json` records this targeted check. This is a material transition change, so prior excluded-literal-history negatives do not cover it.

`emitted_actual.py` source review confirms the prefix249 carry uses last-k emitted plaintext, normal-only seed phase and continuous language context; no major resets are applied. Full family max and continuation after prefix-only k selection are separate, with deterministic k tie order. Combined outputs forward-check and scalar scores add correctly. Any resource refusal blocks complete rank aggregation. No universal perfect language recovery gate is imposed by this arithmetic review; capability results must remain explicit.

### Fixed-mask seed influence

Coordinator affine influence diagnostic cleared before reading real C11 leaders. Independent coefficients came from zero-seed and basis-seed scalar decodes; independent modular rank used all minors with permutation determinants, not the implementation's elimination routine. The crossed field/dimension panel covers240 old/new-construction cases across q2/3/5/29 and k1–4, with sampled/exhaustive seed evaluation and mature-zero suffix invariance. `seed-influence-review.json` preserves this panel; an initial correlated field/dimension panel is also retained separately.

After seed phase completes, a normal emitted-history step is an invertible companion transformation (the departing oldest coefficient is−1). Appending a literal zero can only reduce the coefficient row span. Thus completed-phase rank cannot rise, and rank zero implies later seed independence for a fixed future ciphertext/mask. Before completion, unseen seed coordinates may enter, so history rank zero alone is insufficient. Under old normal-only history, literal F leaves history unchanged and normal steps retain full rank after completion. This qualifies seed identifiability for supplied masks; it does not search masks or establish plaintext.
