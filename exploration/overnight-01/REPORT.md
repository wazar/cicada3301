# OVERNIGHT-01 — completed bounded exploration

**No credible new plaintext or validated binary message was recovered.** All eight real-puzzle paths ran. Independent review reproduced retained transformations, but no candidate earned `VALIDATION_SIGNAL` or `PARTIAL_SOLUTION_CANDIDATE`. This is a bounded miss, not exclusion of a cipher family, evidence of an OTP, or a claim that the puzzle cannot be solved.

Experiment01 remains failed under its original exact-recovery specification. Its evidence and conclusions were not edited. This separately authorised exploration used measured search controls rather than treating perfect recovery as a universal entry gate.

## Actual scope and results

The session began **2026-09-16 20:28:27 SAST (UTC+02)**. Its eight-hour ceiling was **2026-09-17 04:28:27**, with no new searches after03:58:27. The finite queue completed early; worker logging finished by20:40:00, about12 minutes after the session anchor. The ceiling was not a requirement to spend eight hours. Review, reporting and publication followed; final closure time is in `STATUS.md`/`events.jsonl`. No background search is continuing.

All45 discovery original images were used where the declared method allowed. Original50's alphanumeric field was kept separate. Originals **4,9,14,19,24,29,34,39,44,54 were not decoded or revealed**. Some initial workers used an incorrect <=54 selector; original55 was added through explicit catch-up batches, preserving initial results and stable IDs. R04-wide intentionally excludes short49/55 and other page/period cells that have fewer than two training observations per phase.

One coordinator used native workers `/root/overnight_a`, `/root/overnight_b`, `/root/overnight_c`, followed by fresh `/root/overnight_review` while searches continued. B took the queued R05/R06. At most three single-thread computation jobs ran; the global budget was9 of18 logical cores on128GiB RAM. Process-scoped `caffeinate` was used. No installation, external compute, downloads, creator-identity investigation or terminal-rune diagnostic was performed.

| Path | Actual work | Controls and result | Evidence |
|---|---|---|---|
| R01 known methods |87,130 attempts, including10 beam1024 follow-ups;86,760 unique base cells. Four recipes, both signs, all periodic phases/numeric offsets0–127 for ordinary/F; full812 affine transforms;360 separate legacy repeat-rejection start-zero cells.|Small ordinary/F/rejection/affine searches rank planted truth first, exact selected output; first-key corruption changes a rune. No readable result. Width256 F and width400/maxskip3 rejection are different models.|`worker-a/REPORT.md`, `worker-a/R01/top_candidates.json`|
| R02 sourced keys/texts |256 exact sourced rune keys, all short-key phases;8 held solved running texts at prelisted source starts.186,056 ordinary outputs;512 F cells (shortlist plus independent fixed sample);10 width1024 follow-ups.|Planted ordinary/F hypotheses rank first with exact recovery in representative controls. F selection does not cover discarded keys. Best output still noise.|`worker-a/r02/keys.json`, `worker-a/r02/top_candidates.json`|
| R03 numeric |138,240 ordinary outputs:6 sequences×128 offsets×2 signs×2 reset models×45 pages;540 selected F cells.|Exact planted numeric key ranks first; representative F truth top1/top16. Corrupted checks recorded. No coherent result.|`worker-b/r03/REPORT.md`, `worker-b/r03-f/`|
| R04 periodic fit |1,440 period1–32 cells plus1,307 allowed period33–64 cells;133 wide cells skipped. Each real cell has an equally searched shuffled control:5,494 fitted keys total.94,347,316 training-objective evaluations.|Known-period synthetic searches recover periods1,3,8,16,32 exactly. Strong training fragments fail unchanged-phase continuations. Shuffled maximum continuation exceeds real maximum in both tranches.|`worker-b/r04/REPORT.md`, `worker-b/r04-wide/REPORT.md`|
| R05 shared-key relationships |990 pairs×33 offsets×page/ordinal-line resets=65,340 relations;778,504 directional crib implications, with matched shuffled comparisons.|Planted strong alignment ranks first; corrupted truth rank10. Real best relationship0.30044 vs shuffled0.35819. No non-crib prediction.|`worker-b/r05/REPORT.md`, `top_candidates.json`, `top_crib_implications.json`|
| R06 layout |5 invertible source-layout routes×45 pages×820 affine/recipe cells=184,500 real and184,500 matched shuffled outputs.|Actual route/affine search recovers planted reversed control exactly; control has one source line, limiting route-power inference. Real max−6.36616 vs shuffled−6.34498. No coherent text.|`worker-b/r06/REPORT.md`|
| R07 block as key |388,208 ordinary outputs;12,860 feasible F outputs plus8 pilot cases;14 F cells had no retained key-sufficient path.8 physical routes×2 byte conversions; finite offsets and separately declared periodic wrapping.|Three representative F truths recovered exactly; fixed-path checks pass. No full-search null calibration. F all finite offsets focused on49/51; other pages use limited starts/shortlist, not full offset coverage. No readable output.|`worker-c/REPORT.md`, `routes.json`, `top_candidates.json`|
| R08 block as message |46 source-backed spelling variants×13 cipher settings plus direct bytes=599 outputs.|AES/RC4 known answers and checksum/decompression-cap controls pass. Zero full valid structures; maximum printable fraction47.66%.|`worker-c/REPORT.md`, `R08-keys.json`, `top_candidates.json`|

Counts are attempts/cells appropriate to each method, **not independent hypotheses or a single statistical sample**. R01/R03/R06 intentionally overlap; beam widenings and start-zero passes repeat some rules. R05 differences are relationships, not plaintext. R04 counts94,347,316 objective evaluations, including baseline/final-restart calls, rather than misleadingly counting only91,181,162 variant evaluations. Reporting/continuation scores are additional calls. Four deterministic restarts and at most five coordinate sweeps were used, below the allowed16-restart ceiling.

Logged child durations, including preparation/control/export commands, were approximately **A285.88s, B223.24s, C53.24s**; these are summed process elapsed times, not CPU-meter readings or session wall time. Main search allocations therefore differed from the suggested percentages because the bounded matrices completed quickly. `execution-summary.json` inventories every invocation, command, PID, timestamp, exit and duration; individual lane reports separate core search times. Normal900-second limits sufficed; no60-minute batch or timeout was needed.

## Strongest retained outputs and what they mean

No candidate survives as credible text. The registry retains **608 source rows, deduplicated to584 distinct outputs/relationships**, with all origins and alternatives. Every registry output has an independent reproduction record; `REPRODUCIBLE_CANDIDATE` here means the declared transform reproduces, **not** that the text is meaningful. The word “candidate” is an evidence-management label. No score-only promotion occurred.

The high training score in R04 is particularly instructive. Original49/period32 emits a training prefix beginning `HOETHETINGITHINGTOTHEMEATTHEINTHING...`: training−3.51234, unchanged-phase continuation−6.98401. The ellipsis marks truncation for display; complete raw runes are retained. It is flexible-key fitting, not a reading. Initial real continuation maximum−6.33215 was below matched-shuffle maximum−5.81089; wide real−6.38472 was below shuffle−6.18452. Choosing the maximum continuation after examining many periods is exploratory selection, not untouched validation.

R05's highest-scoring implied fragment is exactly **`NWEATHATHEOURG`**, original8 positions0–9, conditional on placing the real solved phrase `ULTIMATELY` on original53 positions15–24. Its−3.81834 score is close to the shuffled search maximum−3.86290. No rule predicts anything beyond the imposed crib span. Neither the supplied phrase nor its short conditional counterpart is a recovered solution.

A leading R02 F result on original55, clue099/phase6/sign+1, remains unchanged:

```text
E-NGEAU-OG-OEA-LTOWEX-FNGEOGDI-EOH-X/
EOFUEAPEDTHBYAN-OTHEONGUF-GYNGI-/
TS-EOCEAFTHAR-IALTEASCR-AEI-DBMA/
NJ-WIAM-JGEA.
```

Its exact-rune word view finds zero matched words; widening256→1024 does not change it. Full source rendering, including leading line break, remains in the candidate payload. These are not silently edited spellings or inserted letters.

## Review, failures and limits

The fresh reviewer independently regenerated sequence/key construction, full forward outputs, F/rejection paths, affine/layout permutations, crib implications and binary parameters for retained leaders. See `review/REPORT.md`, `checked.json`, `binary_checked.json` and pinned manifests. Review overlapped ongoing searches. No output merited fresh image-symbol verification or a reserve reveal; that stronger verification stage was **not performed**, and no visual transcription certification is implied.

The inherited English quadgram score is a ranking instrument with register and length biases. A small delimiter-aware rune-word view in later A outputs shares solved-text sources and is not independent evidence. Short pages disproportionately populate leaders. A/C do not have a calibrated equal-size whole-search null. B's shuffles preserve rune histograms, not the observed adjacency mechanism; their comparisons are descriptive, not exact significance tests. Successful representative controls do not establish general power for another language, skip construction or phase/pruning regime.

R04's optimiser omits quadgrams ending within its first three runes, a declared speed surrogate; final scores use the complete scorer. R05's strongest planted test checks an identical shifted signal, not sensitivity to arbitrary different plaintexts sharing a key. Provisional slash lines are not certified physical lines. Source-supported section resets were not invented; no such R05 section test ran. R06 does not cross routes with the whole dictionary or F models. Optional extra numerical families/KDFs were not added without a clue. Inadequate finite running keys were not padded.

Recorded operational failures were C's first pilot selecting a nonexistent JSON field, B's NumPy-integer serialization, and reviewer schema assumptions while exports evolved. Each failed command, raw traceback, exit code and successful rerun is retained. They were repaired only in new exploration/review tools. No inherited research code, input data, old conclusions or Experiment01 evidence was repaired. Review found no unresolved arithmetic error that invalidates the reported bounded searches.

## Evidence, publication and next work

`config.json` pins dataset/page-map and session policy; `coverage-correction.json` explains original55. `candidate-registry.jsonl` embeds complete unchanged worker payloads, full rune/byte outputs, parameters, F alternatives, source hashes, source paths and execution-manifest references. Compressed score tables retain attempted IDs/scores; deterministic replay recovers other outputs. `runs/*/code/` contains execution-time code snapshots. Only regenerable scorer caches/bytecode are excluded. Publication log redactions, if present, replace a personal checkout prefix only; original bytes remain local and both hashes are recorded in `publication-redactions.json`.

The finite queue is complete; there is no unfinished cursor to conceal or unattended process to resume. Exact replay/checkpoint commands are collected in `RESUME.md` and worker reports. Completed checkpoints should not be mistaken for permission to repeat all searches. The useful next bounded work is **broader F-only R02 coverage selected independently of rigid ranking**, or **R07 finite-offset F coverage on the remaining discovery pages**. Either would be a separately declared tranche, with measured control/ranking limits and its own count; neither is justified as a promising solve by these results. Better justified language views or source-confirmed layouts could change sensitivity, but this session supplies no evidence for a particular new key.

Reviewed results are published only to the owner's configured fork. Publication hashes are recorded in `audit/reports/OVERNIGHT-01.md` and `PUBLICATION.md`; unrelated macOS setup/root assignment files remain outside the commit.
