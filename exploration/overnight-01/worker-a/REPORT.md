# Worker A — R01 / R02 final report

No credible new text recovered. The retained outputs remain score-ranked noise candidates, all UNREVIEWED pending the separate reviewer. No score is a solve; no cipher family is excluded.

All 45 discovery original pages were processed, including original 55. The initial <=54 cutoff omitted55; preserved legacy 44-page files were followed by separate -p55 catchups. Reserved 4, 9, 14, 19, 24, 29, 34, 39, 44, 54 were never decoded. Full frozen source-page rune sequences were used throughout, without prefix cuts.

Logged processing so far: 285.81 seconds across 17 recorded invocations (last report invocation still running is excluded from its own elapsed total). All search/checkpoint stages completed; no search process remains active. Single compute job, one thread. Initial 60-minute allowance not exhausted because finite searches ran quickly.

| Stage | Executed / planned | Best quadgram |
|---|---:|---:|
| r01rejection | 360 / 360 | -6.733137 |
| r01zero-p55 | 16 / 16 | -7.036223 |
| r01rigid-p55 | 1366 / 1366 | -6.542537 |
| r01f-p55 | 546 / 546 | -6.552281 |
| r01rigid | 60104 / 60104 | -6.360734 |
| r01widen | 10 / 10 | -6.360734 |
| r01zero | 704 / 704 | -6.601528 |
| r01f | 24024 / 24024 | -6.360734 |
| r02/widen | 10 / 10 | -6.318303 |
| r02/ordinary | 186056 / 186056 | -6.395755 |
| r02/literal_f | 512 / 512 | -6.318303 |

## R01 coverage

Four frozen recipes: DIVINITY period 8, literal FIRFUMFERENFE period 13, PRIMES and the frozen TOTIENTS array (prime-minus-one, not integer totients). Both signs p=(c+sign*k) mod 29. Ordinary and literal-F cover every periodic phase and numeric offsets 0..127 on all 45 pages. F start zero was searched first at width 256. Full affine 812 transforms per page is a deliberate baseline recheck. R01 executed 87,130 real attempts: 87,120 before widening, plus 10 width 1024 selected followups. The pre-widening count includes 360 ordinary start-zero duplications across initial/start-offset batches. There are 86,760 unique declared ordinary/F/affine/rejection cells when width reruns are ignored. Legacy repetition-rejection covers all 360 recipe/sign/page cells at offset zero only, beam 400 and max skip 3. No cross-product of affine and F.

Literal-F emits rune 0 and does not consume key. Beam prunes by normalized prefix Latin quadgrams, stable tie order; pruning counts and discarded-cutoff ties are recorded for retained candidates. It is separate from repeat-rejection, which accepts skipped key positions only when each would encrypt the current plaintext rune to the preceding ciphertext rune. Legacy rejection uses cumulative beam scoring, normalized final reporting, and independently checked fixed-path re-encryption for every real result. No combined mechanisms.

R01 full solved WELCOME fixture, eight signed-recipe F hypotheses: planted rank 1, best planted rune errors 0, truth in retained top 16=True. Three exact reference arithmetic fixtures passed. Corrupt first-key check produced 1 errors.

ordinary eight-hypothesis control: true rank 1, planted errors 0, top errors 0, actual rejected keys 0; corrupt first-key errors 1.
rejection eight-hypothesis control: true rank 1, planted errors 0, top errors 0, actual rejected keys 4; corrupt first-key errors 1.
Full 812 affine search control true rank 1, errors 0.

## R02 coverage

Frozen 256 distinct exact rune arrays from ordered one/two-word phrases, length 4..32, in verified solved sources. Source character ranges, verbatim rune phrases, aliases and exact conversion are in r02/keys.json. No Latin digraph crosses word boundaries because conversion uses source runes directly. The first 256 distinct source-ordered phrases were accepted before real scoring; this prioritizes early listed sources and does not represent all solved-text phrases. All within-period phases (2024 phase cells) and both signs were run at each of45 page boundaries.

Eight short solved source texts were also used as finite running keys at natural/source-line starts. Each source is an internal documented clue connection, all already held locally; offsets are listed in keys.json, at most 1024 each. No running-key wrapping/padding or insufficient-key trials. Total ordinary 186056 = 182160 periodic cells + 3896 valid running-text cells. Literal-F covered only top 256 ordinary cells plus fixed independent Random(330102) sample 256: union 512. That weak ordinary filter does not cover discarded F cases. F width 1024 reran ten selected cases per lane; no selected best output changed.

R02 ordinary control: ordinary pool 4182, expensive F 0, planted rigid rank 1, survived True, final hypothesis rank 1, planted/top errors 0/0, truth retained True; corrupt first-key errors 1.
R02 literal_f control: ordinary pool 4182, expensive F 499, planted rigid rank 2, survived True, final hypothesis rank 1, planted/top errors 0/0, truth retained True; corrupt first-key errors 1.

## Retention and limits

Deduplicated final exports R01/top_candidates.json and r02/top_candidates.json retain every stage top plus R02 ordinary shortlist (more than 20 each), preserving equivalent origins. Separate fixed-rule replay.py reproduced all 388 retained candidate outputs and every stored F alternative. Alternatives may number below 16 when the complete compatible population is smaller. Full raw output, rune positions, keys or key references, path choices, scores and replay manifests are retained. Candidate files were handed to the fresh reviewer; worker replay is arithmetic verification, not independent validation.

All sweep score tables are compressed JSONL and resumable cursor checkpoints persist candidate ordinals and exact enumerators. R01 legacy 44-page IDs remain unchanged; p55 uses separate directory-qualified IDs. Append-only unique logger directories contain PID/start/end/exit/source snapshots and hashes. Minor setup patch invocations are logged. No old evidence was modified.

Scores are English transliteration quadgrams and are length-sensitive; shorter pages rank conspicuously well and cross-page top ranks are not calibrated evidence. IoC*N, minimum distinct 32-rune symbols and zlib ratio are persisted for every sweep candidate. Non-English LM is unavailable/null. A delimiter-aware exact-rune solved-word fraction is descriptive only, added before p55 and R02 searches; not present on earlier 44-page rows, and not independent of the solved-text register. Source slash lines are provisional; no image-boundary certainty is claimed.

Coverage is conditional on exactly the listed key spaces, ordinary/literal-F/repeat-rejection transition relations, and English register. Small successful controls do not establish universal power, nor do a first-key corruption or incidental words calibrate a false-discovery threshold. No holdout reveal, no sustained-text candidate, no unsupported p-value.

## Resume and replay

The finite queue is complete. There is nothing left running. To verify retained fixed rules:
```sh
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-a --label replay-again --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/experiment-01/keys.json --input exploration/overnight-01/worker-a/r02/keys.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-a/replay.py
```

Search stage commands and immutable code snapshots are in runs/*/command.json and runs/*/code/. For a partial checkpoint, the same command resumes from its saved cursor. Completed cursors are not a request to rerun. A fresh expansion requires its own named finite plan, such as broader F-only clue coverage independent of ordinary ranking; the current noise does not justify a sweeping expansion.
