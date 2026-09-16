# Audit claim index after NEXT-01

Claims and original source excerpts are retained. Status applies only to the scoped evidence in the JSONL record; it never implies archive-wide or image-wide validation. T1 states remain in audit_history. In particular, C-025/C-027 counterexamples refute claimed implications, not prove the actual cipher uses short keys or resets.

| ID | Kind | Status | Inherited claim |
| --- | --- | --- | --- |
| C-001 | data | INDEPENDENTLY_SUPPORTED | The pinned unsolved stream contains 12,956 rune indices with SHA-256 023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585. |
| C-002 | data | INDEPENDENTLY_SUPPORTED | The apparent 55/56 unsolved-page mismatch is explained in R19 by runeless image p50: image p51–55 maps to segments 50–54; p56/57 to 55/56. |
| C-003 | data | SOURCE_CHECKED | Community transcriptions agree rune-for-rune, but the dossier also says they share a 2017 ancestor. |
| C-004 | measurement | SOURCE_CHECKED | R19 per-rune controls report 180/180 solved LP2 glyphs correct and 450/450 O/A/AE disputed sites upheld. |
| C-005 | measurement | SOURCE_CHECKED | R19 forced-alignment analysis reports at most one insertion and one deletion at 95% confidence. |
| C-006 | measurement | SOURCE_CHECKED | The 19 shortlisted separator disagreements are reported resolved in favour of canon; whole-book boundary-position disagreements remain. |
| C-007 | data | INDEPENDENTLY_SUPPORTED | The images are reported byte-identical to archived onion7 originals: 56/56 SHA-1 matches. |
| C-008 | implementation | INDEPENDENTLY_SUPPORTED | The inherited validation script passes five selected-word page checks, not complete expected plaintext comparisons. |
| C-009 | implementation | REPRODUCED | The standalone reproduction suite covers seven named pages but also asserts selected words and lengths, using shared generated code and source data. |
| C-010 | measurement | REPRODUCED | T0 oracle self-test accepts its correct synthetic key and rejects its constructed wrong key. |
| C-011 | implementation | INDEPENDENTLY_SUPPORTED | The oracle self-test constructs a constant wrong key by reinitialising Random(4242) at each symbol. |
| C-012 | implementation | INDEPENDENTLY_SUPPORTED | judge_keystream starts every supplied segment at offset zero under one shared key. |
| C-013 | implementation | INDEPENDENTLY_SUPPORTED | The legacy beam permits a skipped key symbol only when it would reproduce the preceding ciphertext rune. |
| C-014 | measurement | INDEPENDENTLY_SUPPORTED | The English scorer can reject correctly recovered non-English or abbreviated plaintext. |
| C-015 | implementation | INDEPENDENTLY_SUPPORTED | The oracle selects across signs and decoders but calibrates its shuffle null using only beam/sign -1 on the first segment. |
| C-016 | implementation | INDEPENDENTLY_SUPPORTED | threshold_for accepts segment_len but does not use it; its default extreme-value constants are tied to a particular historical calibration. |
| C-017 | measurement | INDEPENDENTLY_SUPPORTED | R19 driftbeam reports recovery of legacy failure cases, with a materially raised wrong-key null and configuration limits. |
| C-018 | measurement | BLOCKED | R19 nine-register adjudicator reports power >=.90 in 27 cells, but its speed gate failed and panel calibration is separate from legacy English scoring. |
| C-019 | measurement | SOURCE_CHECKED | R21 withheld automatic HIT certification after its held-out proxy failed the frozen catch-rate requirement. |
| C-020 | measurement | INDEPENDENTLY_SUPPORTED | The unsolved stream is reported to contain 86 equal adjacent pairs: 86/12,955 flattened or 86/12,901 within pages. |
| C-021 | measurement | INDEPENDENTLY_SUPPORTED | IoC x 29 is reported as .999874 and monogram Shannon entropy as 4.856504 bits. |
| C-022 | interpretation | INDEPENDENTLY_SUPPORTED | For independent plaintext/key increments in an additive model, the expected doublet probability is a weighted sum bounded by the minimum plaintext increment probability. |
| C-023 | measurement | SOURCE_CHECKED | Empirical minimum-increment floors are reported as 1.38–1.83% on four English corpora, later 0.972% for the tested German register. |
| C-024 | mechanism | INCONCLUSIVE | The README asserts a pinned ~83% soft anti-repeat filter over a memoryless base. |
| C-025 | interpretation | CONTRADICTED | The dossier says flat IoC is reachable only by a full-length keystream; later B4 reports finite detection limits around period 400. |
| C-026 | interpretation | INCONCLUSIVE | The headline OTP-class verdict is inferred from a limited statistical battery failing to separate an external-pad model from a derived-key model. |
| C-027 | mechanism | CONTRADICTED | The dossier infers a continuous keystream and no resets from suppressed boundary repeats. |
| C-028 | search_bound | SOURCE_CHECKED | Broad autokey exclusion is asserted, although inherited supplements make it conditional on plaintext statistics and finite feedback families. |
| C-029 | interpretation | SOURCE_CHECKED | The dossier groups substitution and homophonic ciphers as excluded by IoC preservation. |
| C-030 | interpretation | SOURCE_CHECKED | The dossier rejects transposition-only as doublet-transparent. |
| C-031 | search_bound | SOURCE_CHECKED | The README treats running keytexts as closed by exhaustion over ~200 texts; later R26 records a distinct 33-text slice only partially run. |
| C-032 | search_bound | SOURCE_CHECKED | Seeded PRNG exclusions cover specific generators and seed fractions; R25 reports only 0.5015% of one Py2.7 random29 space. |
| C-033 | search_bound | SOURCE_CHECKED | R26 semantic-seed lane reports 4,274 rows as 100% of 323 seeds x 7 generators x 2 decoders. |
| C-034 | search_bound | SOURCE_CHECKED | R26 generator lane describes planned ~747-seed coverage while explicitly recording unfinished baseline execution. |
| C-035 | search_bound | SOURCE_CHECKED | The public-pad branch remains partial and detector-dependent; Marsaglia records 77/756 units and limited prefilter survival. |
| C-036 | implementation | SOURCE_CHECKED | Ledger validation checks declarations and paths; zero unsound-negative flags does not validate the experiments. |
| C-037 | implementation | REPRODUCED | run_t0.py records child failures but has no aggregate failure exit at normal completion. |
| C-038 | data | SOURCE_CHECKED | The four L7 warnings about thresholds not fixed in advance arise from missing/null metadata despite local PREREG claims. |
| C-039 | data | SOURCE_CHECKED | A-05, B-23 and T2-INDEL are negative ledger entries without recorded threshold strings, although T2 has prereg/control rules. |
| C-040 | interpretation | SOURCE_CHECKED | R18 attributes image production to a two-stage Ghostscript/ImageMagick pipeline and compares 11 fonts, but three cited inspection artifacts are missing. |
| C-041 | measurement | SOURCE_CHECKED | PGP verification is reported for 238 held files / 54 distinct messages; missing rerun log limits replay evidence but structured verification tables remain cited. |
| C-042 | measurement | SOURCE_CHECKED | The L1 GnuPG version/timestamp correction is supported by a surviving crosscheck JSON but its textual log is missing. |
| C-043 | search_bound | SOURCE_CHECKED | R19-G3 validates a historical Python generator but explicitly clears no keyspace; its pilot row file is missing. |
| C-044 | data | SOURCE_CHECKED | PROBLEM.json and other navigation documents retain old open/closed descriptions after later ledger work. |
| C-045 | interpretation | SOURCE_CHECKED | Image byte authenticity and render provenance are used alongside a broad no-steganography claim. |
| C-046 | search_bound | SOURCE_CHECKED | PROBLEM.json lists number-theoretic keystreams and the whole number channel as eliminated while later semantic-seed compositions remain finite searches. |
| C-047 | interpretation | SOURCE_CHECKED | The dossier declares fractionation excluded because it cannot produce flat IoC or the doublet deficit. |

NEXT-01 adds scoped evidence to C-002/003/008/009/010/013/015 without changing inherited claim text or broad statuses. The new four-recipe control gate failed; no real puzzle result exists. See [NEXT-01](reports/NEXT-01.md).
