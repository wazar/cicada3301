# Worker I: measured glyph geometry, images0/1

**Outcome:** no candidate extra channel from the tested binary height, baseline, or width mechanisms. This is geometric measurement, not decrypted text and not a solution.

Strategy loaded outside-box-v1 SHA256 `eac5f90b963597464862cadbd2f8245375c844d2d0b6f9e52f418bcad617517c`. Neutral assignment preceded two explicit hypotheses; no earlier worker conclusions were read. AGENTS headline was inherited in context, and doctrine contains repository conclusions: do not describe this worker as strongly blinded. Only original images0/1 read.

## Actual tests

502 retained connected full-height black components:242 on page0,260 on page1.23 body rows. Page0 first coloured row/large initial, art, separators, touching components outside80–140px height/5–90px width were outside scope. All source bounding coordinates and rejected component rectangles are preserved. Visual segmentation overlay was inspected; it tracks individual glyphs with occasional touching pair. Height112–115px; within-row bottom coordinates span at most2px. These source facts directly fail the preregistered >=4px binary-state separation criterion.

| Mechanism | Fitted source separation | Training minority | Heldback MSE improvement | Planted8px bit accuracy |
|---|---:|---:|---:|---:|
| Height |1.365px|31.5%|68.9%|100%|
| Baseline |1.038px|10.0%|99.85%|100%|
| Width conditional on shape |1.222px|10.8%|54.6%|100%|

Large MSE improvements alone are misleading: ordinary integer pixel quantization also clusters. All actual models failed the preregistered4px separation gate; baseline and width additionally failed20% minority gate.

After the height/baseline null, I03 changed to horizontal squeezing. One fixed complete-link clustering pass on aspect-normalized24x48 images produced30 shape classes,29 with>=4 train and>=4 heldback instances. These cover500 instances. The montage shows29 distinct glyph silhouettes; the30th is an excluded touching pair. No transliteration, rune mapping, or English scoring was used. Each eligible class's widths vary by0–3px. Shape class6 has3px width range; all others<=2px. No class reaches4px. The width+8px control uses frozen original class assignments and therefore measures extent detection, not end-to-end reclassification under arbitrary deformation.

100 raster null draws translate original glyphs by random subpixel shifts in[-0.5,0.5] and JPEG-recompress at quality92. Maximum fitted separations1.559px height/1.366px baseline are of the same scale as actual observations. These nulls start from actual glyphs and are sensitivity controls, not independent clean font renderings or a significance test. Threshold96/160 and blur0.35 comparisons are saved. An initial crop included nearby ink and produced a spurious15px perturbation delta; raw original results are preserved. Repair replaced source-padding context with white padding around exact glyph boxes. This bounds inward stability only, since antialias expansion beyond original boxes is clipped.

## Evidence and reproducibility

`PREREG.md`: hypotheses, exact thresholds, Aiming Test, repair and pivot addenda.
`inputs.json`: actual JPEG SHA256s.
`coordinates.json`, `rejected-components.json`: source provenance.
`arrays.npz`: height/baseline raw arrays, split, planted bits/control values, perturbations,100 matched-null statistic rows.
`width-arrays.npz`: normalized images, classes, templates, eligible indices, raw widths, residuals, planted bits/output widths, perturbations.
`results.json`, `width-results.json`: complete statistics.
`p0-segmentation.png`, `p1-segmentation.png`, `shape-classes.png`: visual QA.
`runs/*/command.json`: input/code hashes, command, exit code, elapsed time; frozen source snapshots and stdout/stderr alongside.

I01 initial8.43s exit0. I02 isolation repair8.26s exit0. I03 width0.45s exit0. I04 retains per-instance positive-control arrays, a deterministic archival rerun rather than new coverage; see command record for final exit and time.

## Bounds and next decision

This tests three observable coarse geometry channels in retained black full-height glyphs on two discovery images. No keyspace, additive transform, rejection decoder, or language register assumed. Does not address subpixel/font stroke modifications, colour, separators, excluded/touching glyphs, interglyph placement, rotation internal to fixed bounding boxes, or other pages. Row baseline registration uses all-instance medians, so baseline split tests are descriptive within-page prediction, not clean heldout estimation of page baselines. No positive result was advanced from them.

Two executable next tests, requiring a new preregistration rather than adjusting this result:
1. Test internal stroke-angle/branch-length variation using frozen29 templates and within-template skeleton landmarks; plant2-degree rotation and5px branch edits, then compare actual residuals with subpixel raster/JPEG controls. Identity-normalization may hide affine variants, so preserve source-pixel geometry.
2. Fit a single-font fractional positioning model to the saved glyph left edges and widths, then test whether heldback coordinate residuals exceed subpixel raster bounds. This challenges micro-position rather than glyph identity and must account for ordinary kerning/justification.

No active child process should remain after I04. Root coordinates reassignment; no Git changes performed by this worker.

## I05/I06: source-pixel column adjacency (continued assignment)

Parent requested a materially different operation after the geometry checkpoint. Read only page0/1 entries from existing dataset/page-map. Mapped418 glyph instances on19 complete rows (page0 rows1–11; page1 rows1,3,4,5,7,8,10,11) to exact source indices. Every shape class maps consistently to a single rune index: zero conflicts. Incomplete rows were skipped wholesale, so no fabricated shifts or inferred rune identities. Source label consistency is not a from-scratch transcription audit.

A fixed position-only complete-link x-band rule at diameter half median horizontal glyph-center spacing (25.25px) yielded53 bands and138 consecutive-row edges. Missing rows, empty/ambiguous bands, column wraps and page wraps create breaks. This is an adjacency graph, not a completed decoded stream; it intentionally refuses undefined traversals.

Actual:8 equal-rune pairs/138 edges=5.80%.10,000 permutations of whole labelled row profiles preserve position/identity typography correlations and give mean repeat rate3.15%; lower-tail p=.9624. Page0:7/99; page1:1/39. No cross-page repeat deficit. Horizontal within-complete-row reference:3/399, descriptive only; row-profile null preserves that reference by construction and cannot test its significance.

Route-specific synthetic85%-suppression controls:18/100 met the preregistered p<=.01 detection threshold; uniform controls0/100 false positives. Thus the recognizer is weak for this sparse graph and cannot justify a broad negative about geometric routes. Actual graph shows no repeat-deficit candidate under the frozen rule. Do not claim typography route approaches ruled out. The specific generator's direct counts are retained descriptively in `column-control-counts.json`; this posthoc count summary is not a new preregistered hypothesis test.

Evidence: `route-mapping.json`, `column-graph.json`, `column-arrays.npz`, `column-results.json`, `column-control-counts.json`. Arrays include every route edge, actual labels,10,000 permutation indices/counts/denominators,100 planted and100 uniform fields, their1,000-control permutation rates and p-values. I05 completed arithmetic but exited1 on NumPy integer JSON serialization; I06 changed serialization only, exit0/0.374s. Full scripts/source hashes in run records. No new image beyond0/1; no reserved pages opened.

Next decisions: preserve this as measured bounds, not a solve. A useful next route test would preregister continuous nearest-x links rather than global bands, and account for merge/branch ambiguity and gaps; this is a different graph assumption, not re-tuning53 bands. Alternatively switch omitted channel entirely to internal stroke skeletons as proposed above. Root controls assignment and research deadline.
