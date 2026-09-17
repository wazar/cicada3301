# Selected section image verification (17 September 2026, 08:24–08:27 UTC)

Full original images0,1,2,3 viewed. Images0/1 have12 text rows, image2 has9. Reading order is left-to-right/top-to-bottom including the initial dropcap at section rune0; image0's dropcap visually spans three rows but appears once in its first source row. Native-resolution crops have exact boxes/source/crop hashes in crops.json. No reserved image was opened.

- Heading crop: image0 begins red S plus12 red runes, explicit red13-dot divider after page rune12; black TH at rune13 starts body. Red heading matches `S H E O G M IA F - S Y E NG C`; the enlarged initial does not create extra text rows. The first black group is TH J G AE then a dot, then F J OE then a dot. Direct glyph geometry supports AE rather than A in that group (two descending branches).
- Page0 last row, rune239..261: starts T OE NG U R, ends D A M R dot W. There is no delimiter after final W. Page1 first row starts A I M S N dot. Thus the across-page explicit unit is W A I M S N, not two separate words.
- Page1 last row, rune243..265: starts S T dot M F L F T; ends L X I, without terminal punctuation. Page2 first row begins OE M dot U and then four-dot mark. Across-page explicit unit is L X I OE M.
- Page2 final row, rune182..200: begins C U X T A B J P dot F EA dot H D N IA U P S U W, followed by red13-dot terminal. The mark closes the section; it is not another rune. Image3 then begins a different red initial/heading and scroll marginalia.
- Page0 line3→4 native crop: line3 ends I with no trailing dot; next row starts AE H X TH P G then dot. The unit crosses the physical line. This confirms the F06 whitespace join rather than a boundary at each printed line.
- Page1 line4→5 native crop: next row begins with a dot before P A OE TH R NG AE; this explicit separator closes the prior word despite being printed at the next row's left edge. Do not discard it as a new-line artifact.

## Ornament correction history
v1 packet incorrectly said page2 retained crossed-staff marginalia. Root's initial full-thumbnail review correctly noted staff absence but also inferred no loops; v2 adopted that stronger wording. Native first-row crop visibly retains the top loop, and separate native bbox1050,2900,1350,3050 shows the bottom loop. Root independently inspected the first-row crop and withdrew the no-loop inference. v3 now states: page2 retains the small loops, lacks crossed staffs, and adds the terminal insect. Both previous packet versions remain preserved. No rune, gap, coordinate, key or decoding result changed.

## Limits and uncertain readings
This checks actual row order, selected complete rows, heading/terminal marks, both page joins and two contrasting printed-line joins against images. It is not an independent reread of all729 glyphs or a calibrated99% transcription claim. Remaining glyph identities stay inherited; no new alternate glyph vector was justified, and none was chosen by decryption score. The redheading/body cipher clock is uncertain and remains an explicit competing model. Multi-dot marks are retained in the original image while the P03 scoring boundary token intentionally collapses delimiter types; this loss is declared, not an image-transcription claim.

## Remaining physical joins, checked at native resolution (09:00–09:03 UTC)

All30within-page row joins were viewed in `remaining-joins/*.png`; image-only projection supplied row bands, not glyph labels. Manual classifications in `remaining-joins/checks.json` agree with the frozen source:8have an explicit separator and22are uninterrupted. Source-end/start rune order was compared in the same crops. This extends the earlier two line-join samples to every physical line join of0–2, and the two page joins were already checked. It still does not independently certify every internal glyph.

The seven black four-dot major markers were then inspected as full native rows, with source indices and exact boxes/hashes in `major-marks/manifest.json`. They follow p0rune153; p1runes12,34,87,131,171; p2rune2. The red13-dot heading divider after p0rune12 was already inspected. These observations motivate one precisely frozen third clock policy in A07; punctuation alone does not establish its cryptographic role. No rune or boundary data was changed to improve decoding.
