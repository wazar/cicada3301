# T1 accounting for all 18 ledger warnings

The warning text and order are preserved from the T0 strict-validator log. Every row is **ACCOUNTED_FOR_UNRESOLVED**; no ledger entry was changed. All nine distinct missing paths remain absent on the T1 filesystem check.

11 missing-file references (nine files), three missing threshold strings, four null preregistration flags. “Accounted for” means traced to a claim, impact and next action; it does not mean repaired or scientifically disproved.

| Warning | Ledger entry | Missing item / condition | Disposition and surviving evidence | Claims |
| --- | --- | --- | --- | --- |
| W-01 | A-05 | `threshold absent/null` | T2 RESULTS/PREREG and separator JSON survive. Missing ledger rule; 24 boundary-position disagreements remain outside the stated resolution. | C-006, C-039 |
| W-02 | G-01 | `liber-primus/analysis/round18/L1-toolchain/font_match_sheet.png` | Font-match numeric results and verdict survive; the visual comparison sheet is unavailable. | C-040 |
| W-03 | G-01 | `liber-primus/analysis/round18/L1-toolchain/pdf_hunt.jsonl` | pdf_hunt_summary.json survives; per-PDF scan rows are unavailable. A summary does not establish complete 493-file coverage. | C-040 |
| W-04 | B-11 | `liber-primus/analysis/round18/L1-toolchain/runes_observed.png` | Glyph metadata and font-match results survive; the exact observed glyph sheet is unavailable for visual audit. | C-040 |
| W-05 | B-11 | `liber-primus/analysis/round18/L1-toolchain/font_match_sheet.png` | Same absent sheet as W-02, cited by a second entry. Count both warnings, only one missing file. | C-040 |
| W-06 | B-11 | `liber-primus/analysis/round18/L1-toolchain/pdf_hunt.jsonl` | Same absent PDF log as W-03. Count both references without treating them as independent evidence gaps. | C-040 |
| W-07 | B-23 | `threshold absent/null` | Same separator work as A-05, with a second missing-threshold field; coverage is not a second independent experiment. | C-006, C-039 |
| W-08 | B-13-MARSAGLIA | `liber-primus/analysis/round18/L6-offset-marsaglia/data/MANIFEST.json` | Marsaglia result/control JSON survive, but acquisition manifest is absent; original input identity is not established by sweep counts. | C-035 |
| W-09 | L7-A-SCORER-ENGLISH-ONLY | `threshold_fixed_in_advance is null` | Flag is null. PREREG A rules and out_a1.json exist; no historical ordering checked. Evidence list is absent in this ledger row. | C-014, C-038 |
| W-10 | L7-A-ARCHIVE-RESCORE | `threshold_fixed_in_advance is null` | Flag is null. PREREG A-iii and out_a2.json exist; operative contrast versus prereg raw-z criterion needs review. Evidence list absent. | C-014, C-038 |
| W-11 | L7-B-BEAM-ENVELOPE | `threshold_fixed_in_advance is null` | Flag is null. PREREG B and out_b1.json exist; no chronology checked. Evidence list absent; later I1 modifications are separate tools. | C-013, C-038 |
| W-12 | L7-C-THRESHOLD-CALIBRATION | `threshold_fixed_in_advance is null` | Flag is null. PREREG C and out_c1.json exist; no chronology checked. Evidence list absent; calibration claims remain conditional. | C-016, C-038 |
| W-13 | R19-C2-MARSAGLIA-GATE | `liber-primus/analysis/round18/L6-offset-marsaglia/data/checksums.sha256.txt` | Independent verifier script and out_verify.json survive; published checksum reference file is absent. | C-035 |
| W-14 | R19-C2-MARSAGLIA-GATE | `liber-primus/analysis/round18/L6-offset-marsaglia/data/marsaglia-cdrom_files.xml` | Same gate: archived XML manifest is absent. Existing output reports a historical comparison, not a fresh byte match. | C-035 |
| W-15 | CORPUS-G-02 | `liber-primus/analysis/round19/C3/verify_rerun.log` | PGP-VERIFICATION-TABLE.json and verifier script survive; textual rerun transcript is absent. Signatures were not executed in T1. | C-041 |
| W-16 | L1-F6-CORRECTION | `liber-primus/analysis/round19/C3/l8/crosscheck.log` | crosscheck.json and RESULTS survive; textual crosscheck log is absent. Keep file/message/version denominators distinct. | C-042 |
| W-17 | R19-G3 | `liber-primus/analysis/round19/G3/pilot.jsonl` | Generator source, validation.json, pilot.py and READY survive; raw pilot.jsonl does not. Lane explicitly clears no keyspace. | C-043 |
| W-18 | T2-INDEL | `threshold absent/null` | T2 control/PREREG and indel outputs survive. threshold_fixed_in_advance is true, but threshold text is absent; derive no new field here. | C-005, C-039 |

The JSONL companion preserves each exact warning, ledger source lines, parsed threshold fields, current path-existence check, surviving evidence paths, claim IDs and proposed next action. None of these metadata checks reran the ledger validator or a research experiment.

For missing artifacts, later work should first locate the original or establish an explicitly new reproduction. It must not fabricate a historical log or treat a summary as the missing raw evidence. For missing preregistration metadata, inspect implementation, operative decision rule and history before deciding whether a metadata repair is justified. The four L7 evidence-list omissions are an additional source-level observation, not extra warnings emitted by T0.
