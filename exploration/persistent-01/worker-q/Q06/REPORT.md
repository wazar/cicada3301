# Q06 — internal-rotation detector fails its controls; actual state test not run

The frozen detector cannot reliably recover planted2° states after realistic raster perturbations. Its unchanged identity recognizer rejects82/196 and81/196 held glyphs in the two positive controls. Retained coverage is only58.16% and58.67%, below the95% gate. Even perfect state recovery on every retained glyph could not meet the90% whole-held-set recovery gate. Therefore **no actual glyph-orientation or two-state statistic was evaluated**, and this is not negative evidence about an internal image channel.

| Fixture | Held identity/coverage | Fixed sorted-state accuracy | Fitted separation | Training minority |
|---|---:|---:|---:|---:|
| Actual-crop rotation + raster0 |58.16%|9.18%|1.729°|7.96%|
| Actual-crop rotation + raster1 |58.67%|8.16%|1.918°|6.19%|
| Template raster-only0 |100%|Not applicable|3°|2.55%|
| Template raster-only1 |100%|Not applicable|3°|3.05%|

The normalized24×48 descriptor has median nearest-template RMSE0.05794/0.05589 for unrotated held glyphs but0.23972/0.23964 for the +2° glyphs, above the frozen0.16 rejection cutoff. Only10/91 rotated held glyphs remain classified in either repetition, compared with104/105 and105/105 unrotated glyphs receiving the same raster nuisance. Thus the rotation sensitivity of normalized shape matching dominates rejection; raster perturbation alone does not explain it. These posthoc control diagnostics do not change the detector.

All identified held positive-control shapes have the correct identity; failures are unclassified glyphs exceeding the fixed0.16 normalized-shape RMSE limit. No original class was forced back onto a rotated glyph. Planted state labels enter generation and final accuracy measurement only, never template fitting, classification, parameter selection or state clustering. The low state accuracy uses the frozen low-angle=0/high-angle=1 coding; label swapping cannot remedy the coverage failure.

A second concrete instrument limitation appears in raster-only controls. The narrow straight-stem class1 has a flat orientation-error bank for all12/13 assigned instances. The inset mask covers constant interior ink and removes informative stroke edges. Every tested angle ties, so deterministic first-index selection returns−3°. This creates an apparent3° separation with a tiny minority; it is not a raster-encoded bit channel. The minority and within-class gates reject it. Full per-class error matrices preserve this diagnosis without refitting anything.

## Frozen scope and method

Only I's418 mapped crops from originals0/1 were used, with its29 frozen shape identities and original train/held split. The eligibility rule leaves393 instances in26 classes;196 are held. Every exact grayscale crop is preserved unscaled on a160×128 white canvas. Color and antialias outside the original crop bounds are outside scope; original source coordinates and JPEG hashes remain available. A source montage was visually inspected before running controls.

Training-only normalized24×48 identity templates retain the frozen identities. Every transformed target is reclassified. Training orientation templates group target crops by predicted identity, not planted state or forced original identity. The detector compares template rotations−3..3° in0.5° steps and fixed subpixel translations−0.5/0/+0.5px. Pixel MSE uses the median glyph rectangle inset4px horizontally and8px vertically, deliberately avoiding width/height endpoint measurements. No scaling or rotational registration erases the measured angle first.

Positive fixtures rotate whole glyph canvases by0/+2° while measuring only interior pixels. Bits are balanced within identity and train/held pools. Each also receives independent subpixel translation in[−0.5,0.5] and JPEG92 recompression. Template-derived raster comparisons use source training class means with the same nuisance transformations but no planted state. Those means are not independent clean-font renders, so these are sensitivity fixtures, not a calibrated natural-image null. Both complete procedures rebuild training angle templates and fit the same unsupervised two-center model.

No angle grid, mask, identity cutoff, restart, class assignment or exclusion was adjusted after failure. In particular, the class1 degeneracy was diagnosed and preserved rather than removed to improve scores. I's earlier width controls used known frozen identities under deformation; Q06 demonstrates why that shortcut would overstate this end-to-end internal-shape detector's capability.

## Verification and disposition

A separate checker reconstructs all418 source crops from original images, verifies their stored byte hashes and exact canvas pixels, then replays every saved bank argmin, angle, state assignment, coverage and accuracy count. It confirms no actual-summary file exists. Inputs/maps, all four transformed image sets, control bits/offsets, class predictions, masks, per-class candidate errors and statistics are retained. Preparation logged0.437s, controls5.363s, independent accounting1.079s and saved-control rejection diagnosis0.091s. No reserve image, new page, Git write or active process.

Evidence: CARD.md, q06.py, inputs.npz/inputs.json, maps.json, source-montage.png, positive-{0,1}.npz/json, raster-null-{0,1}.npz/json, controls-summary.json, check.py and check.json. This control failure identifies identity-normalization rejection and an uninformative interior mask as limitations. A future detector would need a separately frozen identity-invariant registration and informative stroke features, validated without forced classes; such a repair was not run or smuggled into this experiment.
