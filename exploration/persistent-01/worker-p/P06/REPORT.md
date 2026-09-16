# P06: isolated-glyph pilot does not justify unparking transcription

Three separately frozen reads of the same100random glyph crops scored93/100,93/100and99/100against the existing visible-ciphertext transcription. The first two readers made exactly the same seven errors. Majority consensus scored93/100. This is a measured capability limit of this setup; the single99/100reader is insufficient to establish reliable99%generalization or justify a full transcription campaign. No further control/discovery images were opened after the comparison and no input was corrected.

PARKED P-1 specifies>=99%isolated-rune accuracy on solved controls, with three independent readings and a downstream change additionally required for a finding. This pilot's first reader and consensus fail that gate. Same-model correlated readers on the same100crops are not300independent samples or independent font/transcription lineages.

## Exact control input and segmentation

Only solved LP2 original56and57cached images were used:

- audit/parallel-01/inputs/sources/56.jpg,2400x3600, SHA256a4c1c9ae1246c3197fc1d7bd0155cbc97f60d4bba84a104d45f180feab1814dc.
- audit/parallel-01/inputs/sources/57.jpg,2400x3600, SHA2561dabc100ddbf1fc49715219636984eb6ad96a2bd8035e196c12e66db77a1077b.

Page-map entries have stale/null local-image/hash fields; the actual cached images exist. Mapping is original56->segment55,85runes, global[12956,13041);original57->segment56,95runes,[13041,13136). Comparison uses ciphertext IDs from dataset.json, never decoded solved text.

All10physical rows were mapped by image geometry and ordinal component counts. The initial connected-component attempt found two touching-glyph merges on57rows0/1and stopped before sampling. At highzoom each merged pair visibly has a left lower-right terminal touching the following glyph's vertical stem. Fixed image-only cuts at originalx1290and1679split bboxes[1236,917,1343,1031]and[1625,1105,1732,1220]. Pixel-column ink counts jump1->114and2->114at those cuts. The initial failure and its raw geometry remain preserved; no sampled label vector guided the repair. All row counts then match, with one oversized first-row dropcap accounted separately per image. This validates ordinal geometry, not an independent guarantee of transcription identity.

The declared black/normal-height pool excludes two red dropcaps and ten red heading glyphs:168eligible (80on56,88on57). Seed130106selects100withoutreplacement,41on56and59on57;68remain. Selection.json maps every numbered crop to page,row,pixelbox,runeoffset and original source-character position. Fixed padding leaves thin neighboring stroke edges in some crops; no crop was discarded after revealing labels. This pool alone cannot supply300new independent glyphs.

## Reading and freeze discipline

The worker viewed full images for geometry, then personally read all five randomized20crop contact sheets. Existing source/code context was accessible from earlier tasks; no strong-blinding claim. Only a canonical29Unicode legend rendered using AppleSymbols.ttf was supplied, without inherited target labels or glyph crops. Font-form variation is a limitation. Source familiarity, exposed context and pre-freeze generic-legend adjustments are recorded in CONTEXT.md/vision-notes.md.

First-reader prediction SHA2567adcd28431e039d1ace415e7e65bccce89e3e8716e6c0e6fea6d20cf239ef30a froze22:19:04.732554UTC. Review11second-reader SHA256fb505e5d7e29fe83f53e0ee65fbab6f4ee6a68c55d23676ff4cefa9922a8dd96and coordinator-third-reader SHA2569cde0ef16cea3212f30b368535357e5eb39010c5c74539154eef567d27466ab9were received before comparison. All hashes were asserted by the comparison script. No prediction was amended after truth access.

## Exact observed failures

Readers1and2both labelD(index23)asM(index19)on crops1,20,28,41,57,94,andTH(index2)asW(index7)on95. All seven were marked high-confidence by both readers. Their prediction vectors agree100/100, so treating their agreement as independent confirmation would be wrong.

Reader3labelsM(index19)asD(index23)on66,mediumconfidence, and otherwise matches. Pairwise agreement with each other reader is92/100. All three agree on92crops; discarding the eight disagreements would be post-selection and does not create a new capability pass. No unreadable/abstained labels were entered; first-reader low-confidence cases were retained and happened to match reference. Self-rated confidence did not identify its actual errors.

The one-sided95%binomial lower bound for99/100is below99%; uncertainty.json records numerical bounds as a descriptive iid approximation, not a guarantee across fonts/pages. The sample omits multiple rune classes and all excluded colored/large glyphs. Existing ciphertext transcription is a comparison reference, not newly independently adjudicated truth. The measured shared M/DandTH/Wconfusions dominate the interpretation.

## Evidence and decision

Failed geometry run20260916T221212.103234Z: exit1,0.482448s. Documented two-split run20260916T221407.055170Z: exit0,0.490718s. Three-frozen-reader comparison20260916T222407.842501Z: exit0,0.049417s. Logs/code snapshots, images/crops, selection, hidden labels, frozen predictions, confidence, errors/sourcecoordinates and comparison remain intact. MANIFEST.json pins all retained artifacts. No Git/new reserve/image expansion or active process.

This path stops at the measured failure; full transcription remains parked. A future capability test would need a distinct, predeclared calibration/reader setup and new known-solved control glyphs, not correction of these100answers followed by a claimed100%re-read. Parent reassigned the worker to a different output-role hypothesis. No discovery-page partial reread is justified by this pilot.
