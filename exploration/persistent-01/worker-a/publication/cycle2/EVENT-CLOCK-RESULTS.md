# EVENT-CLOCK-01 and FIELD-RESET-01

No candidate or predictive continuation was found in either bounded real-data pilot. These are negatives only for the 16 frozen complete source primers × two signs, specified per-attempt feedback transition, beam128 and English transliteration quadgrams. They are not an autokey exclusion. No larger keyspace follows from these results.

EVENT-CLOCK-01 appends current plaintext to a fixed-length queue on every attempted draw, including rejected attempts (cap3). All four full reference controls recover exact plaintext and searched key rank1, retain the true path, and recover exact frozen-prefix continuation. Their matched full-procedure shuffle controls do not recover a comparable signal. The inherited accepted-output-clock decoder, given the correct key, makes480/515,296/319,71/85,0/95 errors; the last control has no rejection and cannot distinguish clocks. The other controls have20,17,1 rejected draws. Exhaustive short-input checks cover372 cases, and an explicit forced-accept-at-three control passes. All retained paths are scalar re-encrypted.

The pilot covers pages0,17,55:96 real plus96 matched-null full-key hypotheses, the same192 prefix fits, and6 frozen continuations. Real best full scores are -6.844815,-6.821957,-6.617363; matched null -6.826533,-6.787600,-6.697230. Real continuation tails are -7.079233,-6.976161,-7.765613 versus null -7.176052,-7.178327,-6.908586. Leaders inspected as full text remain incoherent. One shuffle per page is a comparison, not a calibrated significance estimate.

Original event score rows accidentally omitted structural statistics. Original evidence is preserved. A labeled deterministic replay of all448 control+pilot full-key cells reproduced scores/retained alternatives and records supplemental IoC*N, minimum distinct32 and zlib ratios in checks-and-replay-stats.json. These are postpilot diagnostics on English-selected paths, not an independent language-free search. nonEnglishLM is explicitly null. Current writer includes statistics directly.

FIELD-RESET-01 separately tests resetting queue and previous cipher at image-backed13-dot source gaps, retaining language context. The G06 map SHA is d9532e234811d2b99a03ef07ad692c8438f934fbedc70749b3be3f8147340443; independent review3 confirms all14 signs and gaps. That validates representation, not cryptographic reset semantics. Page3 gaps16/119/122, page7 gap194; duplicate signs at194 are idempotent under this exact reset policy. Terminal gaps produce no empty field. Page17 has no internal13 mark and reuses its unchanged prior result.

Both reset-shaped planted controls recover the exact searched key, plaintext and continuation. Page-continuous decoding gives212/217 and10/208 plaintext errors.32 no-reset identity checks reproduce the original event decoder. Full matched shuffles preserve each field's rune counts.

| Page | Model | Real full | Null full | Real frozen tail | Null frozen tail |
|---|---|---:|---:|---:|---:|
|3|continuous|-6.828278|-6.848642|-7.391572|-7.014532|
|3|13-reset|-6.813698|-6.917351|-6.800095|-7.086303|
|7|continuous|-6.769188|-6.835133|-7.799108|-7.679819|
|7|13-reset|-6.767442|-6.798039|-7.221496|-7.070378|

The real/null reset pilot executes256 full-key hypotheses,256 prefix fits and8 continuations. Page3 continuation freezes at119 (98 remaining runes); page7 at194 (only14 remaining, weak power). All leaders inspected remain incoherent. Data/alternatives/all scores are in field-reset/pilot-results.json; control evidence is in field-reset/controls-results.json. No keyspace widening is justified.

Finally CLOCK-REPRESENTABILITY-01 removes the inherited scorer/pruning confound. Exact pointer-set propagation constrained to planted truth, independently checked against1360 exhaustive short cases, proves the first three event-clock truths impossible under the accepted-output relation: first incompatible zero-based rune14,9,17 respectively. This remains true even if future plaintext is fully known, rather than only the causal prefix. The fourth no-rejection control is representable. Full per-position sets are retained in event-clock/representability.json. This proves a narrow transition gap; it says nothing about the real cipher mechanism. Encoder beyond-end fallback zero is a source-code finding and is not adopted as a mechanism.

Logs: event-clock-controls10.662s, real-pilot4.537s, edge-controls-and-replay10.985s; field-reset-controls6.789s, real-pilot7.336s; representability0.086s. All exits0; raw command/output and script snapshots reside in runs/. After two nonpredictive feedback pilots, this family stops. Next actions: freeze this evidence for coordinator checkpoint; hand off the compute slot for a materially different research lane.
