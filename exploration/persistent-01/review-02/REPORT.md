# Review 02 — reproducible layout association, no cipher finding

The numerical F01/F03 association is reproducible. F04 supplies a concrete ordinary-layout mechanism that produces the same scale of association, so these results do not support a cipher reset claim. No untouched validation was performed or needed for this bounded review.

## Independently checked

Only the filtered 45-page F01 maps were read for rune data (10,466 runes, 480 source lines). Reserved pages were asserted absent. Only discovery image p1 was opened; it visibly has 12 text rows. No reserved image/layout/text was inspected.

An independent contingency implementation reproduced all 1,998 F01 real/trim rotation draws (maximum absolute difference 4.50e-12). Line-start G=79.444675, tail 1/1000; trimmed G=65.809024, tail 1/1000. All 32 controls' observed statistics and stored null tails checked; 64 selected control rotations replayed, rather than all 6,368. Detection was baseline 0/8 and each of alphabet/successor/repeat 8/8. Eight controls per class gives limited precision; these are broad boundary mechanisms and do not validate the interpretation of a visual-wrap effect.

All 1,999 F03 saved start maps were checked for page/stratum count invariants and their scores recomputed (maximum difference 9.17e-13). G=65.929391; predictive total=13.537924, folds -0.788776/3.315640/11.011061; both tails 1/2000. Counts by rune agree exactly. Deleting the three most positively influential pages 17,23,41 leaves G=51.154625, a descriptive deletion diagnostic with no postselection significance claim. Fold imbalance matters; the effect is not equally predictive across folds.

A prewritten cheap falsifier added within-page position tercile to the F03 page × capped parsed-word-offset × capped parsed-word-length strata. Of 435 starts, 356 remained movable. Across 999 fresh draws, maximum G=64.970073 versus actual65.929391, tail1/1000. Broad within-page nonstationarity of this specified form did not remove the association. This was adaptive discovery work and does not rule out fine positional or visual-layout effects.

## Parser and inference limits

Saved words partition each page exactly; source-line first/last word endpoints agree with line-start/end masks and source character coordinates increase strictly. F01 words are regex rune runs formed separately for each raw source line. Therefore every line start is a parsed word start by construction. A physical wrap can split a true word into fragments, so F03 controls fragment length/offset, not underlying linguistic word length/offset. Saved maps cannot independently certify raw source transcription or all image alignment.

F01 rotates labels relative to a fixed stream. This is valid for its random-phase hypothesis, not for a null where wrapping depends on glyph identity. It retains observed rune doublets but changes the layout/rune relationship. F03 assumes exchangeability within its strata; greedy wrapping violates this too. Its randomization destroys distances between line starts. Rejecting both convenience nulls is compatible with completely ordinary typography.

F01's eight primary endpoints and eight secondary sensitivity endpoints must remain distinguished; family8 applies only to the predeclared primary set. F03 was selected after F01 and family2 does not erase the prior adaptive selection. Modulo3 discovery folds share the discovery-selection history, parser, typography and scoring choice; they are not untouched confirmation. Report plus-one Monte Carlo tails, never p=0. They are not a campaign-wide family error bound.

## F04 independent source and control check

Independent column-run extraction directly from p1 bytes reproduced every stored component, every accepted/rejected row, all width samples and all29 median-width-plus5 estimates. Eight rows passed count matching (1,3,4,5,7,8,10,11); four failed and remained excluded. Comparing source rune IDs used only the filtered map. This verifies component/coordinate arithmetic and compatibility with source row counts, not a from-scratch rune transcription: count agreement can in principle hide compensating split/merge errors. Repeated per-rune samples are tight, making wholesale accidental component assignment less plausible.

Independent remaining-capacity implementation reproduced all1,000 seeded greedy simulations, all saved start maps, and all200 equal-width controls exactly. Raw and width-corrected tails are .395604 and .310689. Variable width moves simulated G median from equal-width25.731 to59.367; actual multinomial G62.459 is ordinary on that modeled scale. F04's G differs from F03 by design: multinomial against full-stream frequencies versus a 2×29 table after removing initials.

This is a plausible counterexample, not a proven reconstruction of the original renderer. Ink width+5 is not measured advance; bearings/kerning, page margins, title/dropcap styles and separators vary. The simulation imposes separator cost14 at every parsed word end, including source-line endings that need not be actual separators. The fixed1180 budget yields466–484 starts against435 observed. A layout fitted from p1 and tested on overlapping discovery material is not independent validation. Nevertheless, it decisively defeats the inference that a small rotation/conditional-null tail itself establishes cipher structure.

Next useful action: preserve F01/F03 as a measured layout association; require a source-calibrated layout model predicting held-out discovery row breaks or residual identity effects before considering cipher-reset work. Estimate actual inter-glyph advances and true separator positions on count-matched p1 rows first, then test frozen parameters on allowed p0/p17 while explicitly treating them as previously inspected discovery material. Do not spend reserved pages on the current result.

## Exact evidence

- `checked-findings.json`, `falsifier-evidence.json.gz`, `width-findings.json`.
- `runs/20260916T201850.072124Z-independent-boundary-review/`: exact command, input SHA256s, copied review/worker code, stdout/stderr, exit0,19.534s.
- `runs/20260916T201953.074320Z-independent-width-review/`: same evidence plus p1 image hash, exit0,1.581s.
- Both used `.venv/bin/python -B`, single-thread environment, logger deadline900s; scripts checked fixed mission deadline/STOP during the longer loop. No Git mutation, no nested worker, no additional controller. Logger's standard read-only commit capture was retained.

Strategy outside-box-v1; bounded review complete while other research continues.
