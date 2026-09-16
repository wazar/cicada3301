# OB-E checkpoint — outside-box-v1

No credible candidate emerged. Six bounded, non-English tests executed; all preserve the45-page discovery selection and exclude the ten reserved originals and original50. Parent requested slot rotation after E06; no further experiment started. Fixed mission deadline remains2026-09-17T03:30:37Z. No child process remains.

## Measurements

|Test|Actual scope and result|Limits|
|---|---|---|
|E01 wholeword/numeric magic-square representation|Both source grids satisfy all12line sums:1033 and3301. Each has rank5 overF29.1598consecutive25-cell discovery windows:0passes;1000fullprocedure shuffles:0passes.|Rejects only direct contiguous exact-magic format; singular-operator hypothesis was disproved, not matrix encryption.|
|E02 fixed5-rune matrix operators|2source matrices/inverses×5phases=20candidates. Real maximum pooled concentration42.2003;1000null-family maxima givep=.56244. Planted biased output recovers exactly/rank1,score3167.12 versus controlnullmax64.55.|Fixed matrices/column direction/page resets/no padding; only nonuniform output detectable.|
|E03 direct coordinates|360domain checks:45pages×2grids×word/rune units×0/1base.0complete lists. Maximum discoverypage274runes/79words versus grid maxima366/1311.|No wholebook/otherbook indexing tested. Repeated sourcecells would force centrosymmetry regardless of selectedtext.|
|E04 coordinate-specific detector|Same20transforms; realmax172.4395,1000null-familyp=.45355. Planted coordinate biases cancel in pooled histogram(score25.96) yet recovered detector3336.93 exceedscontrolnullmax205.96.|Concrete E02detector blindspot tested; uniform coordinate marginals with dependence remain invisible.|
|E05 cross-grid procedure|Identity/totient/nthprime followed by affineF29 map, bothdirections:6recipes.0complete relations; best10/25cells versus1000null maximum12. Bothsourcegrids have13distinct cellclasses.|Affine coefficients fit firstindependentpair; sourcegrids already viewed, exploratory; no fresh validation claim.|
|E06 wholeword field symbols|2662rune words, indexsum andprimesum modulo29; concentration andadjacentMI.1000fixed-word-length rune-shuffle nulls. Rawtails .4825,.7782,.06893,.4975; Bonferroni4minimum .27572. All4biased/Markov controls recover exactly anddetect.|Transcriptionline boundaries may splitwords. Null breaks anti-repeat dependence. Uniform independent outputs invisible. No signal warrants heldout reveal.|

## Evidence and reproducibility

Cards were saved before each execution; source/method/input hashes and command/stdout/stderr snapshots are under `runs/`. The initial E06 calculation reached serialization but failed on numpybool; the explicit boolcast is the only fix, with completed result in the `e06-serialization-fix` run. This is not a failed arithmetic control or a new search.

Coordinator requested fuller evidence retention after initial summaries. Deterministic replay is marked **evidence recovery, not new coverage** in labels `e01-e06-evidence-recovery` and `e02-e04-full-null-recovery`. The first recovery batch completed E01/E02/E04/E05 then encountered E06's already-known serialization fault; final focused reruns completed. Prior immutable run snapshots preserve the pre-retention scripts.

Gzip evidence stores every null comparison statistic, control vectors/null comparisons, deterministic seeds and RNG ordering. E02 gzip additionally stores every transformed rune output for all20candidates and45pages. E04 uses exactly those same transforms. E02 mapping records sourcepositions, page/phase, discardedprefix andtail; no inventedpadding. E01cellmap and E06wordmap retain page/line/raw offsets. Shuffled sourcearrays need not be stored: scripts+seed+RNGordering reproduce them.

Replay one test, for example:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-e --label e06-replay --input exploration/persistent-01/worker-e/experiment06.py --input audit/parallel-01/inputs/dataset.json --seconds 900 -- .venv/bin/python -B exploration/persistent-01/worker-e/experiment06.py
```

Use same wrapper and corresponding experiment01..05.py for others. These are replay commands, not proposed new coverage. E01/E02/E04/E05depend on E01result; E03also on E01discoverycells. All source inputs are frozen local files; no network, installations, nestedworkers or Git used.

## Independence and exposure

Initial brief was limited-context withholding, **not strong blinding**: root AGENTS instructions were already in conversation. Before E01 I read only strategy/mission, supplied sourcefiles and the frozen dataset's schema/page0prefix. I proposed representation and operator hypotheses before consulting priorcoverage.

After initial execution I inspected old `armada20/magicsq_keystream.py` (numeric/digitperiodic keys,bothsigns/Atbash), and relevant `campaign18_skip/armada2/numeric2_skip.py` functions (numeric/digit/rowsum periodicstreams). Those are additive-stream procedures; they do not implement E02/E04blockoperators. Later, after E05execution, I read workerD's CHECKPOINT and found it proposed the same matrix/correspondence directions. Thus these were executed independently of that specific note but are not uniquely novel ideas; sourceprime-sum reconstruction was already known.

An overbroad post-E01coverage search accidentally returned historical reservedpage54vision annotations. `exposure.json` records exactcommand, visiblefields and consumption; coordinator notified immediately. No rule chosen from annotations; allreserved pages remain excluded. **Page54is contaminated for this worker's future validation.** Other nine remain unavailable. Do not reconstruct exposure by reopening reservedfiles.

## Next two executable actions for replacement reviewer

1. Independently replay E02/E04 using direct scalar modular multiplication and empiricalnull scores; verify20candidate outputs, sourceposition/tail maps, and detector-control conclusions against savedgzip, without reading reservedpages. No new research hypothesis required.
2. Test E06's strongest representation with an anti-repeat-preserving length-conditioned null and run its planted controls. Freeze the exact sampler and mixing diagnostics before realdata; compare whether prime-sum concentration50.7746 is explained by tokenlength/rune constraints. This would resolve a null-model limitation, not turn rawp=.069 into a discovery.

Alternative if E06nullrefinement has no decision value: treat explicit delimiter classes as inputstate, test a frozen withinword versus crossword transition prediction with withinpage controls. This needs a new card and is not executed here.
