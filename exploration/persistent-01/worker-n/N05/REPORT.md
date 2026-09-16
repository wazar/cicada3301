# N05 — horizontal glyph placement

**Outcome: no identifiable binary-placement candidate, and insufficient sensitivity for a channel negative.** The ordinary positioning model remains inaccurate enough that it fails all declared4/8px random-displacement control gates. A shape-correlated8px state is exactly confounded with ordinary glyph leftbearings. This is a measured instrument/model limit, not evidence that the images contain no position channel.

Only I's existing418 mapped glyphs on19 complete rows of original images0/1 were used.29 frozen shape classes;10 training rows(220glyphs),9 held rows with95 prefix coordinates for row placement and103 suffix coordinates for prediction. Global font corrections use training rows; held-row origin, letter spacing and word spacing use prefix positions only. Width, shape or rune identity was not reclassified. No additive/English assumption, new pages or reserved input.

Ordinary model: cumulative training-class median inkwidth plus fitted class advance/leftbearing corrections; row origin, per-glyph spacing and per-separator spacing. Fractional coordinates are permitted before raster rounding. Original-character gaps marked92 delimiter locations independently of their observed pixel gap width. Font correction ridge1 and all splits/thresholds were frozen before scoring; no kerning-pair family was searched.

The initial model conflated ordinary separator shapes. Its held MSE255.938px² included≈30px jumps. Actual cropped row inspection showed four-dot punctuation; independent pixel connected-component counting in the92 fixed gap boxes found **87 one-dot and5 four-dot separators**, with3 four-dot events in training rows and2 in held rows. These are image counts, not inferred source-character dot labels. Their boxes/component areas are saved. One explicitly adaptive repair added only the cumulative four-dot separator count as a font-advance feature; the initial miss and all outputs remain preserved. Because held residuals motivated this diagnosis, repaired statistics are **not fresh validation**.

| Measurement | Initial model | Punctuation-aware repair |
|---|---:|---:|
|Predicted suffix MSE,px²|255.938|37.263|
|Training residual center separation,px|3.742|1.444|
|Held binary-center MSE improvement|14.84%|16.57%|
|4px random-bit fixtures passing geometric gate|0/10|0/10|
|8px random-bit fixtures passing geometric gate|0/10|0/10|
|Mean held bit accuracy,4px fixtures|58.25%|63.69%|
|Mean held bit accuracy,8px fixtures|66.50%|71.07%|

The repaired held residual range remains−3.144..13.505px, and56.3% lie outside±2px. Thus residuals are not explained to a tight rasterization floor; neither broad exclusion nor a stego interpretation is justified. The repair's fitted extra four-dot advance is19.756px; it is a regression parameter under this model, not a measured font advance. No additional spacing adjustments followed its remaining miss.

Actual isolated source-pixel translations by4/8px recover the exact shifts for418/418 glyph crops at each displacement. These controls verify coordinate measurement with frozen shapes, not full-page segmentation after possible neighbor overlap. Full actual-coordinate controls refit the entire predictor and save every planted bit/position; their failures expose the practical prediction bottleneck. The199 ordinary-model quantization sensitivity draws do not constitute independent font renders or a calibrated null for all typesetting. Repaired improvement upper tail.975 is descriptive under that synthetic model only; binary gate fails independently.

**Identifiability:** setting the current-class leftbearing coefficient to8px for odd-numbered frozen classes reproduces the class-correlated planted binary shifts exactly at all418 positions(error0). Therefore those shifts lie within the ordinary font-bearing parameter space: source positions alone cannot distinguish that state from alternate font bearings. The fitted regularized pipeline's low bit recovery is not itself this proof; the explicit design-matrix equivalence is saved in verification.json. Independent random per-glyph states are not covered by this exact ambiguity, but measured control power is weak here.

Preserved evidence: original and repaired code/cards, both full evidence files, predictions/coefficients/masks, all20 paired controls and199 nulls per fit, image hashes, actual pixel separator counts/crops, pixel-control coordinates, and exact feature-span verification. Logged one-thread batches.424s(initial),.258s(separator diagnostic),.422s(repair),.084s(verification). No active process/Git mutation/reserved read.

**Decision:** rotate this lane. A future position-channel test needs independently constrained font metrics/spacing or an observable invariant that removes those nuisance freedoms; another fitted spacing term on these same residuals is not justified. No additional image request follows this miss.
