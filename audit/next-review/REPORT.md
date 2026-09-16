# NEXT-01 fresh review

**Disposition: accept the three bounded reports, with their stated limitations. No release-blocking defect found.** Experiment 01 stopped at a reproducible positive-control failure; it produced no real-puzzle verdict. The alphanumeric reconciliation agrees with a previously retained corrected input, and the explicit literal-F model is distinct from the failed legacy experiment.

This review inspected the frozen specification, actual execution source snapshots, raw case files, source images and selected prior artifacts, then ran two independent small checks. It did not run a new puzzle experiment, repair inherited code, or extend any worker's hypothesis set. All reviewer writes are under `audit/next-review/`.

## Experiment 01

The preregistration and key/fixture/slice hashes match `FREEZE.json`. Its recorded freeze time is 18:03:27 UTC, preceding the 18:04:24 pilot and 18:05:21 main batch. Main execution input hashes and copied source files still match their contemporaneous records. The source gates continuation behind completion of all 320 positives. Actual retained cases form the contiguous ordinal sequence 0–66: 66 passes followed by one failure, without a removed or bypassed failed cell. The remaining 253 cases are explicitly skipped. The filesystem output inventory and recorded branch outcome show no calibration, held-out, shuffle or real-slice decode outputs. This conclusion is about these retained executions, not a claim that file absence proves all possible activity elsewhere.

The reviewer called the **unmodified production** `encipher_keyskip`, `rigid_decode` and `beam_decode` directly, without importing the worker's trace copy, on ordinals 0, 20, 40, 65 and 66. All 160 page/recipe/sign/decoder output dictionaries matched the saved production fields exactly. Selected planted ciphertexts and accepted-key positions also matched production encryption. An additional read-only pass checked all 67 cases' ordering, encryption arithmetic and saved gate decisions.

Ordinal 66 independently reproduces the reported result: DIVINITY, decode sign +1, rejection-beam case 6. Page 0 has 119/120 exact runes; the only mismatch is index 119. Page 1 is exact. The wrong page-0 output scores −4.0951382033607935 versus the truth's −4.096305974563245. The shared planted recipe/sign still wins. Thus it is the preregistered exact-recovery condition that fails, not identification of the winning recipe. The report correctly avoids attributing this to exceeding max_skip or claiming a general beam-pruning diagnosis.

**Accepted outcome: `BLOCKED_BY_POSITIVE_CONTROL`.** No recipe was rejected on the unsolved pages. Calibration code remains unexecuted and unvalidated by this review. Its prospective flag rule must not be reported as empirically calibrated. A future synthetic terminal-ambiguity investigation is justified; changing the failed gate retroactively is not.

## Alphanumeric material

The reviewer read the actual p49 source raster, after verifying SHA-256 `aa3f89156756edf8b796a470a14a3db96516ad2fedf1ed98ccabc1a1cddc0335`. Native image inspection of `p49-index45-context.png` used original-image rectangle **[1320,2070,1520,2260]**; the disputed token's tighter box is **[1395,2139,1449,2220]**, zero-based index 45, page49 row5 column5. The first glyph has the angled digit-1 head. The second is a taller plain vertical stroke with no L foot. This supports `1l` over relikd's `1L`. The subtle I/l distinction remains a qualitative height judgment. This was an unblinded spot-check, not a fresh full transcription or a measured accuracy experiment.

Recomputing the historical base60 interpretation of all 256 retained tokens reproduces SHA-256 `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`. This is the existing Round19 C1 corrected payload; it is not a newly discovered encoding or byte correction.

All entries in the worker's prior-artifact hash manifest matched. Beyond those identity checks, the reviewer inspected C1's actual `out_b05_sweeprow.jsonl` header and candidate rows, `out_b05_readjudicated.json`, and the relevant `RESULTS.md` passages. They support the limited coverage claim: 20,160 specified corrected-payload choices, legacy key-skip transition model, nine-register adjudication, retained per-choice statistics rather than full plaintext traces. The reported zero escalations and explicitly unrerun B04/R16/R17 uses are represented accurately. This is source/artifact review, not a fresh historical sweep rerun or an all-time coverage audit.

**Accepted as coordinate-linked reconciliation with preserved uncertainty.** The proposed blind transcription check has a sensible distinguishing question, but its controls must demonstrate font/glyph applicability before any quantitative accuracy claim. One-site agreement here does not certify the other 255 sites.

## Literal-F interruption model

Independent arithmetic read all six original ciphertext/expected reference files, reconstructed the two cyclic keys directly, and generated the prime-minus-one key using trial division independently of the worker's sieve. All **919 reference runes** and each position's key-consumption state matched.

One hand calculation makes the non-consumption rule concrete. In `jpg107-167`, zero-based position48 decrypts `(21−18) mod29 = 3`, advancing key index48 to49. Position49 is the declared second ciphertext-F occurrence: it emits 0 and leaves key index49 unchanged. Position50 then decrypts `(11−9) mod29 = 2`, advancing49 to50. Consuming a key at position49 would instead use the next key value0 at position50 and emit11, contradicting the supplied fixture. The interruption label here remains supplied truth, not evidence of automatic discovery.

The independent whole-mask interpreter reproduced all **908 compatible paths** across the six synthetic fixtures, including complete plaintexts and final key consumption, and verified final beam-state membership. Independently recalculated quadgram scores and true-path global ranks match the retained reports. The tiny mixed fixture is also directly checkable: ciphertext `[0,0,2,2,0,28]`, key `[11,2,27,4,14,11]`, literal positions `[0,4]` produce `[0,18,0,4,0,24]` while consuming four keys. Its ordinary encrypted F at position1 gives `(0−11) mod29 = 18`; assuming every F is literal would be wrong. Three observed Fs allow eight compatible paths. The zero-key case has four paths but one plaintext, so exact plaintext does not establish a unique interruption path.

The failed initial main run's source differs from the repaired source only by token K→C in the authored WALK fixture. K is outside the declared token alphabet. The saved traceback occurs while creating the list of plaintext fixtures, before encoding or scoring the main candidates. No beam width, seed, scorer or scientific gate changed. This is a preserved task-code defect, not score-driven tuning.

**Accepted as model/control evidence.** Language ranking is not unique identification; the random-register case's poor truth rank persists even when all paths survive. The evidence justifies designing later bounded controls/calibration for this separate model, not applying it automatically to unsolved pages.

## Reviewer evidence and limits

* `review.py`, `checks.json`, `runs/20260916T180727.110369Z-selected-independent/`: direct production reruns, path enumeration, input checks and actual-source crop generation; exit0, 0.2343 seconds.
* `evidence.py`, `evidence-checks.json`, `runs/20260916T180823.564594Z-evidence-reference/`: independent full reference arithmetic, score/rank checks, all-case arithmetic and execution-snapshot checks; exit0, 0.1874 seconds. All worker artifacts were hashed before and after this read-only check and were unchanged.
* `p49-index45-context.png`: direct source crop, visually inspected with the native image viewer; no synthesized glyphs or enhancement.

Both processing runs used the shared command logger with contemporaneous command, commit, code/input hashes, start/end times, stdout/stderr and actual exit status. They consumed approximately **0.422 seconds** under two 300-second caps, within the reviewer budget of at most three such runs. Historical records were inspected as retained evidence; no missing historical run metadata was reconstructed.

No worker or inherited files were edited. No real ciphertext was decoded, no calibration was rerun, and no general search was launched. The reviewer stops writing after this report.
