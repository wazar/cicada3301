# P01: original13 ornament half-turn test

A fresh source-image observation and an executed alternative-representation test; no solution claim. Strategy outside-box-v1. Only original13 was inspected; no reserved page or second original image was read. Initial proposals were recorded before looking at prior lane results. Available context included the full supplied repository instructions, parent brief, strategy/mission/config, source map entry and image, so this is not strong blinding. Worker-i implementation code was subsequently consulted to locate the installed Python environment; no previous image-lane result report was consulted.

## Feature and competing explanations

The right-margin tree/root ornament visually pairs top and bottom shapes. A literal duplicated half under a 180-degree turn would be a source-defined operation absent from the flattened rune stream. Independent drawing of balanced branches and roots could create a similar impression without a precise operation. Vertical reflection is a third explicit competitor. The frozen P01-CARD.md specified exact ROI, thresholds, translation range, control and a >=0.80 tolerant-overlap gate for near-pixel duplication.

## Source and exact mapping

Original13 image: `liber-primus/data/relikd/p13.jpg`,2400x3600pixels, SHA256 `3481daeed3ab2bea6effbe36eec22f74955bce87ca4b4ae8674be1d3f84ea08d`. Page-map entry identifies segment13/source-region13,272runes, global stream [3194,3466). Ornament ROI original-pixel bounds [1820,650,2330,2900), right/bottom exclusive. The ROI does not map to rune offsets: it is outside the glyph block. All original images remain unchanged.

Gray ROI was reduced2x with BOX filtering, thresholded128, and the stem region |x-2075|<35original pixels excluded. Rotation180, vertical reflection and horizontal reflection were compared over integer translations +/-40original x and +/-120original y in2pixel increments. Score is the sum of foreground hits in each direction with two reduced-pixel dilation iterations, divided by total foreground. This is a tolerant overlap, not strict pixel Dice. All 3x3threshold score surfaces plus100band-order comparison surfaces are retained as .npy files; raw masks and all random band orders are in raw-arrays.npz.

## Measured result

| Transform | threshold128 maximum | translation original pixels (x,y) | thresholds96/160 |
|---|---:|---|---|
| 180-degree turn |0.437247|22,86|0.417683/0.446034|
| vertical reflection |0.236603|-22,116|0.225044/0.239243|
| horizontal reflection |0.287478|-16,12|0.282522/0.293558|

The exactly duplicated control scores1.000. Translation optimizer selected (0,-4) because the tolerance makes several shifts equally perfect; it is not unique registration. One hundred whole-ROI fifteen-band permutations scored median0.140778,95th-percentile0.234095,max0.326979. They preserve pixel inventory and rough occupancy but are not an independent botanical-drawing null. These figures are descriptive, not a selection-corrected probability.

The predeclared literal-duplication gate fails. Rotation has greater approximate correspondence than the two reflection alternatives, consistent with rough rotational balance. It does not establish the ornament as a cipher instruction. A manually drawn copy, warped motif, topological correspondence or symbolic operation remains possible. No text operation, key, plaintext or hidden bitstream was selected after the score.

Direct array slicing recomputed all three winning128-threshold scores to <1e-12 of FFT correlation. The saved rotation-overlay.png was inspected with view_image: prominent twig differences remain visible; apparent overall symmetry is not exact duplication. This replay independently checks the score computation technique but shares preprocessing and input.

## Execution and next discriminating work

Primary run `runs/20260916T214739.959149Z-p01-ornament-turn`: exit0,5.417587s. Direct replay `runs/20260916T214827.698680Z-p01-direct-replay`: exit0,0.193907s. Commands, code snapshots, hashes, stdout/stderr retained. One CPU/thread, no active process remains.

1. Test the genuinely different topological claim: manually label terminal twigs and branch junctions in upper/lower halves with original-pixel coordinates, freeze correspondences by graph degree/order before inspecting labels, then compare rooted branch graphs under a half-turn. This discriminates manual-copy geometry from merely balanced artwork and requires no further page.
2. If graph correspondence is strong, freeze one explicit text mapping supported by those coordinates (not an arbitrary route family) and test on discovery material. If weak, abandon this ornament as an exact-operation lead and explicitly nominate one other discovery image before viewing it. No reserve release is justified by P01.
