# Worker G — source geometry, fields, and direct recurrence models

Strategy `outside-box-v1`; no solution or candidate plaintext. Only originals3,7,17 images/rune data were examined. No reserved content, broad visual annotations, Git changes or nestedworkers. Deadline remains2026-09-17T03:30:37Z. All computations use one-thread bounded `run_logged.py` jobs; commands, input hashes, code snapshots and raw logs are in `runs/`. Cards G01–G10 precede runs. Initial G02 failed on grayscale p17 and was corrected by explicit RGB conversion; failure log preserved. G09's follow-up is sensitivity/replay, not new real coverage.

## Main useful result: generic periods erase visual delimiter classes

G06 pixel measurements and exact source-gap mapping distinguish **four-dot** and **thirteen-dot** signs:

- Original3:13-dot at rune gaps16,119,122;40 singleton signs.
- Original7:4-dot at gaps19,162,200;13-dot at gap194 twice (body terminal and footer prefix), and208;45 singleton signs.
- Original17:4-dot at gaps64,105,119,167,217;63 singleton signs.

Both classes are represented as `.` in source text except p7 footer prefix, for which a structural `&` exists but no period. Two geometrically different signs at gap194 must retain their ordered roles; flattening them to a unique gap loses this distinction. `g06-source-gap-map.json` preserves actual component centers/bounds, line, rune gap and preceding source character. `g06-results.json` preserves every pixel component across thresholds90/130/170 and original/JPEG90. Counts remain identical in all six settings. Synthetic4/13 signs and connected-rune exclusion controls pass. No broad OCR claims: source-period matching is row/order based after actual crop inspection, and symbol size filtering can miss unrelated glyph fragments. Frozen map was sent to workerA for optional event-clock/field-reset controls.

This is a representation finding, **not cryptographic evidence**. In these images13-dot signs consistently sit at headings/body/footer edges and4-dot signs in interior clauses. Ordinary typesetting can explain the distinction. Three images do not establish the rest of the book's punctuation system.

## Bounded tests and outcomes

|Test|Measured result|Scope|
|---|---|---|
|G01 mirror/column source-index routes|6routes×3pages;2000 row-cyclic nulls/page; no lower-tail below.288; six arithmetic plants pass.|Not pixel-aligned routes; boustrophedon preserves almost all ordinary adjacencies and has low identification power.|
|G02 two-intensity red ink|Red-tile90–10 percentile spread0 onp3,1 onp7; threshold20. Planted two-level spread60, constantcontrol0. No red onp17.|Strong intensity alphabet only; no general steganography exclusion.|
|G03 red versus black alphabet|Page-conditioned likelihood-ratio58.9516,10000 circular-role null tail.41596. Strong planted role tail.00010.|Counts small; heading and typography roles can explain positive association.|
|G04 red fields as byte records|696nominal cells,674overflow,22valid outputs;20eligible for120checks.0 realCRC hits;100matched shuffles/field yield oneCRC16 hit.2planted full-search controls recover.|Only directbase29, fixedminimal bytewidth and namedCRC16/32 formats; many numeric values exceed bytewidth.|
|G05 five-dot regular-cycle geometry|Five actual large dots detected; regularpentagon normalizedRMS.4692,circle relativeRMS.2296 versus.05 threshold. Regularcontrol~0,displacednegative.2774.|No named constellation identification; irregular cue still possible.|
|G07 ornament template relationship|Fit top-left p3→p7 among289translations gives0,0 andIoU.9624; predicted otherregions.9281,.9626,.9279. JPEG90control.9948–.9968.|Strong geometric similarity; not byte/pixelidentity and not all explained by JPEG. Fixed artwork could still be instruction.|
|G08 red fields as integer metadata|3pairs×2directions×4targets=24exact comparisons,0matches;12encoding controls;3000fieldshuffles0matches.|Only bodylength/indexsum/primesum/distinctcount and directbase29. Secondp3 body may continue beyondpage.|
|G09 direct low-orderGF29 generator|Six framing units minimaldegrees32–91 exceed cap8; zeroeligible generators.12rawdegree4/8 controls exact;5%substitution0/12 and repeat-rejected0/12eligible.|PriorRound10L9 already testedwholebookBM. Novelty only visualfield boundaries/suffixprediction. Highorderinterpolants are diagnostics, never admitted as candidates.|
|G10 local recurrence with rejection|16train+8exactforecast,degree<=8:1052nominal windows across6units,**629unique sourcewindows**,0hits.240/240 filtereddegree4/8 plants detected, minimum12hits each.100permutation and100no-repeat fullprocedure nulls0hits.|A useful detector improvement for this narrow directgenerator; no additivepad, English, highdegree/nonlinear or arbitraryrune relabeling coverage.|

## What changed

We now have an image-backed delimiter distinction absent from generic-period labels and a small direct-generator detector that tolerates sparse repeat rejection by examining intact local runs. Neither yields a decipherment. Visual-route, red-field and raw generator hypotheses remain bounded negatives/observations. The G10 control improvement is a method result; it does not establish how the ciphertext was constructed.

Cumulative counts above are not measures of discovery probability. G01–G08 were adaptive proposal selection on already viewed discovery images; no untouched validation claim. Shared parser/transcription ancestry remains. G09 reused known BM mathematics; G10 reuses its checked function explicitly. Existing C finite-state/rank/digraph tests were consulted before recurrence, and historical L9 recurrence code only after the first G09 run (timing recorded in G09-SCOPE.md).

## Concrete next actions

1. Independently review G06's14 mapped multi-dot signs against the pinned images and source intervals, focusing on the two separate13-dot signs atp7 gap194. Start from `g06-source-gap-map.json`; do not open morepages. This could catch a field-boundary error before A uses it.
2. If pursuing the generator branch, freeze a different observable construction before code: polynomial degree2 state transitions with one observed rune state, infer on an early prefix and predict later suffix, then measure repeat-rejection sensitivity. This differs from linear recurrence/rank deletion but must earn an actual control before any real negative. Do not automatically expand G09/G10order/window bounds.

These are next actions for coordinator allocation, not a request to stop the research mission. WorkerG has no active child process and all evidence is saved.
