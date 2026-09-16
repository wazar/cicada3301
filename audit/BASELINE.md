# T0 baseline — 2026-09-16

All four assigned commands completed with exit code 0. Eight benchmark tests were
collected and passed; none were skipped. The strict ledger check reported 18
warnings and 27 notes. This establishes a runnable baseline, not scientific
validation of the repository.

Code baseline and actual working commit: `396001a9ce55e0e85ddef19e405afc6a13954588`.
This is the **post-macOS-setup working environment**, not an untouched fresh clone.
The pre-existing `.gitignore` modification and setup files were preserved.

Run: [20260916T165851.125236Z](runs/T0/20260916T165851.125236Z/manifest.json).
Started 2026-09-16 16:58:51 UTC (18:58:51 Africa/Johannesburg).

## Commands and results

All commands ran from the repository root with `python3` resolved through the
existing `.venv/bin` PATH. Python 3.12.14, macOS 27.0 arm64, pytest 9.1.1.
Each command had a 300-second wall limit. One child process at a time, no parallel
workers, numeric thread limits set to one. No limit was increased.

| ID | Command | Exit | Outcome | Wrapper seconds |
| --- | --- | ---: | --- | ---: |
| 01 | `python3 liber-primus/tests/validate.py` | 0 | PASS: 5/5 keyword checks | 0.293 |
| 02 | `python3 liber-primus/verify_solution.py --selftest` | 0 | PASS: correct control accepted, wrong control rejected | 0.726 |
| 03 | `python3 -m pytest liber-primus/benchmark/ --collect-only -q` | 0 | PASS: 8 tests collected | 0.130 |
| 04 | `python3 -m pytest liber-primus/benchmark/ -q` | 0 | PASS: 8 passed, 0 skipped | 0.934 |
| 05 | `python3 liber-primus/analysis/handoff/validate_ledger.py --strict` | 0 | PASS with 18 warnings, 27 notes | 0.041 |

All five stderr logs are empty. No test failures, launch errors, timeouts or missing
required execution inputs occurred. The runner itself exited 0. Its PASS labels
denote command outcomes only; stdout was also inspected rather than relying on exit
codes alone. Pytest reports 0.80 seconds for the suite; wrapper timing includes launch
and shutdown overhead.

## Raw evidence and reproducibility

The run directory contains separate `<ID>-<name>.stdout.txt`, `.stderr.txt`, and
`.json` files. [manifest.json](runs/T0/20260916T165851.125236Z/manifest.json) records
commands, UTC times, durations, exit codes and timeout flags. Additional records:

- [environment.json](environment.json): interpreter, platform, installed distribution
  versions, explicit environment controls, limits and audit-plan checksum.
- [inputs.json](runs/T0/20260916T165851.125236Z/inputs.json): raw input sizes and SHA-256.
- [sources.json](runs/T0/20260916T165851.125236Z/sources.json): relevant source hashes.
- `git-status-before.txt`, `git-diff-before.patch`, `git-status-after.txt` preserve
  the existing local setup changes.
- `tracked-before.json`, `tracked-after.json`, `tracked-content-changes.json`:
  every initially tracked file was fingerprinted; **zero content changes** occurred
  during the run. `inputs-after.json` matches `inputs.json`.
- [inspection.md](inspection.md): import tracing, inputs, seeds and side effects.
- [run_t0.py](tools/run_t0.py): timeout/logging wrapper. Re-running
  `.venv/bin/python -B audit/tools/run_t0.py` creates a fresh run directory.

The environment record retains duplicate `liber-primus-rig` distribution metadata
as returned by `importlib.metadata`; it has not been silently deduplicated.
Before publication, the private checkout prefix in JSON metadata was replaced
with `<REPO_ROOT>`. Commands ran from that repository root; raw stdout/stderr and
input/source hashes are unchanged. No full environment dump or tokens were captured.

## Collected tests

All belong to `liber-primus/benchmark/test_gates.py`:

1. `test_running_key_no_filter_rigid`
2. `test_running_key_skip_filter_beam`
3. `test_running_key_rewrite_filter_beam`
4. `test_derived_sha256_ctr`
5. `test_seeded_prng`
6. `test_rigid_scores_correct_key_as_noise`
7. `test_shuffled_plant_is_not_recovered`
8. `test_all_gates_pass`

The eighth test reruns the seven gate functions; these are not eight independent
experimental replications. Test collection code has no skip markers. Wider `tests/`
and historical campaigns were outside T0 and were not collected or run.

## Available and missing inputs

`english_quadgrams.txt`, `scream314_lp.md`, `keys/self_reliance.txt`,
`krisyotam_runes.txt`, `LEDGER.json` and `PROBLEM.json` were present and hashed.
The first three support the exercised decoding paths. The oracle self-test uses
synthetic pages, so it does **not** check the actual LP2 transcription or its
normalised-stream hash. `krisyotam_runes.txt` and `PROBLEM.json` were fingerprinted
for context, not scientifically verified. No image-byte or transcription checks
were performed in T0; fetched training books were not used by these paths.

The ledger reported 11 missing-path warnings covering these nine distinct files:

| Path below `liber-primus/analysis/` | Ledger IDs |
| --- | --- |
| `round18/L1-toolchain/font_match_sheet.png` | G-01, B-11 |
| `round18/L1-toolchain/pdf_hunt.jsonl` | G-01, B-11 |
| `round18/L1-toolchain/runes_observed.png` | B-11 |
| `round18/L6-offset-marsaglia/data/MANIFEST.json` | B-13-MARSAGLIA |
| `round18/L6-offset-marsaglia/data/checksums.sha256.txt` | R19-C2-MARSAGLIA-GATE |
| `round18/L6-offset-marsaglia/data/marsaglia-cdrom_files.xml` | R19-C2-MARSAGLIA-GATE |
| `round19/C3/verify_rerun.log` | CORPUS-G-02 |
| `round19/C3/l8/crosscheck.log` | L1-F6-CORRECTION |
| `round19/G3/pilot.jsonl` | R19-G3 |

The remaining seven warnings: no recorded threshold for A-05, B-23, T2-INDEL;
threshold not fixed in advance for L7-A-SCORER-ENGLISH-ONLY, L7-A-ARCHIVE-RESCORE,
L7-B-BEAM-ENVELOPE, L7-C-THRESHOLD-CALIBRATION. These are validator reports, not
independent adjudications of those historical experiments. The script reports 27
notes but prints only the first ten; the raw output preserves that truncation.

## Interpretation limits

- The five validation entries check selected words, not complete expected outputs.
- The oracle accepted its planted key on three synthetic pages (scores -4.139,
  -4.307, -4.321) and rejected its wrong key on all three. The source recreates the
  wrong-key RNG on each iteration; varied wrong-key rejection is not established.
- Benchmark results apply to the inherited plants, decoder, scorer and fixed
  controls. No independent generator or search-recovery calibration was introduced.
- The strict ledger returned zero errors and zero entries it labels unsound
  negatives. Missing evidence and threshold warnings do not fail strict mode.
- No claims about cipher family, anti-repeat mechanism, transcription correctness,
  historical search exclusions or puzzle solvability were established or revised.

Stop point reached. Next proposed task: T1 claim/dependency inventory, after review.
