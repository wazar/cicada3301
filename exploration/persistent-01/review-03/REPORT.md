# Review 03 — G06 source map and G09/G10 recurrence checks

Strategy `outside-box-v1`, bounded fresh review on 2026-09-16. No solution claim, reserved-page inspection, broad annotation read, nested workers, Git writes, or new parameter sweep. Actual image viewing: originals `p3.jpg`, `p7.jpg`, `p17.jpg`, then all fourteen native-resolution sign crops in `fourteen-signs.png`. Existing worker conclusions were read first, so this is not blinded. No independent full rune retranscription is claimed.

## Checked source observation

All fourteen multi-dot marks visually agree with the proposed classes and source-row ordering. Thirteen-dot signs are three staggered columns with 4+5+4 squares; four-dot signs are diamonds. The source-gap map agrees with an independent count of runes in each raw source row and cumulative page offsets:

|Original|4-dot gaps|13-dot gaps|
|---|---|---|
|3|none|16,119,122|
|7|19,162,200|194 body terminal;194 footer prefix;208 footer terminal|
|17|64,105,119,167,217|none|

At p7 gap194 the black body terminal and red footer prefix are separate visible signs. The exact source between runes193 and194 is `'./\n&\n'`: only the first sign has a literal period; the footer prefix is associated with the structural ampersand. All other mapped marks immediately follow the pinned preceding-rune source character with a literal period. No map correction needed. Worker A and coordinator were notified immediately. A confirms its reset-only operation is idempotent at a duplicate gap; its frozen visual map retains both events while deduplicating executable reset positions. That choice is consistent for this reset model, but would not justify deduplication in a model that advances a clock at each sign.

This confirms an omitted typography distinction in generic periods, not hidden information or a cipher rule. The thirteen-dot marks occur at title/body/footer boundaries in these three images. Shared source ancestry and possible rune transcription error remain; the review verifies punctuation mapping against this transcription, not every rune identity.

## Correction and recurrence checks

**Worker G's report overcounts G10 nominal windows: correct 952, not 1052.** Six lengths are103,95,194,273,217,208; subtract23 each to obtain80+72+171+250+194+185=952. The reported629 unique page/start windows is correct (194 onp3,185 onp7,250 onp17). Coordinator notified; this reviewer leaves worker-owned report editing to the coordinator.

Independent GF29 Gaussian elimination (not the worker's Berlekamp–Massey function) reproduced:

- Zero exact eight-rune forecasts on all952 nominal real windows,629 unique.
- All240 saved degree4/8 repeat-rejected controls detected, with exactly matching per-control hit counts and minimum12 hits. Raw streams satisfy their stated recurrence, accepted streams reconstruct exactly from saved rejected positions, and every rejected item repeats the previous emitted symbol.
- All12 raw G09 controls predict their complete suffix exactly. None of12 G09 filtered controls admits even a degree8 recurrence on its training prefix, confirming the global method's stated failure.
- Saved G10 full-procedure permutation/no-repeat null records sum to zero hits. Null-generation runs were not independently repeated in this bounded review.

The scope is direct generation of the observed sequence using this GF29 basis and order cap, with local stretches surviving the stated repeat-rejection construction. It is not a negative against a linear additive key beneath unknown plaintext, arbitrary symbol relabelling, high-order or nonlinear generators. Raw arithmetic/control checks are independently implemented; control selection, input transcription, field choice, and training/test window choice remain inherited. Prior whole-field BM/LFSR work means novelty is local prediction/rejection tolerance and visual field framing, not the recurrence mathematics.

## Reproduction and next decisions

`check.py`, `checked-findings.json`, `fourteen-signs.png` and `runs/` contain evidence. The first run completed PASS/exit0 in1.317s; the strengthened second run completed PASS/exit0 in1.300s and adds independent cumulative row offsets, raw recurrence/rejection validity, and G09 filtered-prefix checks. Both use the existing bounded logger and one-thread `.venv` Python. Each `command.json` pins exact dataset, raw source, three source image hashes and reviewed result files; raw stdout/stderr and code snapshots are retained. No active child remains after completion.

1. Worker A can proceed with its separately frozen source-reset test; no punctuation mapping defect blocks it. State explicitly when duplicate visual signs have identical reset effects.
2. Before another direct-generator extension, freeze a materially different observable construction (for example degree2 state transitions), require actual control recovery under the proposed transition rule, and predict unused symbols. Do not infer hidden-key absence from the reviewed negative.
