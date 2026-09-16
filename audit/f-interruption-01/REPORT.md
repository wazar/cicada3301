# Literal-F interruption model — NEXT-01 Worker C

**Complete model/control task.** Independent arithmetic reproduces all **919 runes** of the three complete keyed reference groups, retaining each of the 14 documented literal F runes without consuming a key. Unknown interruption choices can be searched under this model, but compatible alternatives remain: score ranking is not proof of the correct plaintext or interruption path. No unsolved page was searched.

## Reference rule and exact checks

At position i with current key index j, normal decryption emits `(c[i] - key[j]) mod 29` and advances j. At a declared interruption it requires ciphertext F, emits plaintext F and leaves j unchanged. Reference labels are **one-based occurrences of ciphertext F**; traces convert these to zero-based rune positions. Keys continue across each complete group, including headings.

| Complete reference | Output runes | Key values consumed | Literal F positions, zero-based |
|---|---:|---:|---|
| `0_welcome` | 515 | 504 | 48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514 |
| `jpg107-167` | 319 | 317 | 49, 58 |
| `p56_an_end` | 85 | 84 | 56 |

Every emitted rune equals the full external expected fixture, including normal encrypted F sites. At circumference position49 the trace is `cipher=0, plain=0, key_before=49, key_after=49`; position58 holds key index57 unchanged. For An End, position56 retains F and holds key index56 unchanged. Full traces cover **every position**, not only interruptions, in the pilot results.

This validates these declared rules against the existing community reference transcriptions. Labels were supplied as reference truth, never inferred. It does not independently certify image transcription, physical page boundaries or an automatic finder. Sources and documented configurations are those retained by `audit/parallel-01/reference/REPORT.md`; no source was downloaded again.

Three behaviours must remain separate:

* Literal-F interruption preserves one output rune and consumes zero key values.
* Deleting F removes a genuine output rune. It shortens the reference output and is wrong for these declared positions.
* Rejection/key-skip filtering discards proposed key draws under a ciphertext condition. It changes key consumption by skipping draws, not by emitting a literal F with no consumption. None of the controls here uses that filter.

## Bounded unknown-choice experiment

`PLAN.md` was logged and hashed before pilot execution. The independent mask enumerator assigns every observed F either normal decryption/consumption or literal F/non-consumption. All other observations must be normal. Truth labels enter encryption and subsequent assessment only; neither search implementation receives them. No interruption-count constraint or prior is supplied.

The prefix search independently expands those transitions, ranks each prefix with an independently implemented normalized English quadgram scorer, and keeps widths2/16/128 **plus every boundary tie**. Consequently width is a target rather than a hard cap. No distinct paths are merged. Exact tiny enumeration agrees with the unpruned prefix search in path, full plaintext and final key index. All larger cases also retain exhaustive compatible outputs for comparison. A separate evidence checker re-encrypts every one of the **908** retained exhaustive paths and verifies every final beam state belongs to its exhaustive set.

Synthetic messages were fixed before scoring: three short prose token sequences and one seeded uniform-rune control. Finite random keys use seeds330101–330104, with selected normal key values adjusted to ensure ordinary ciphertext F is present. Each larger fixture includes three true interruptions and at least three ordinary ciphertext Fs. The prose is deliberately simple and too small a sample to estimate general recovery power. Keys are synthetic streams, not Worker A's recipes. Full fixtures, generated key arrays, encryption traces and outputs are retained.

| Case | Runes | Observed F: literal / ordinary | Compatible paths / distinct plaintexts | Exact-path global score rank | Beam outcome |
|---|---:|---:|---:|---:|---|
| tiny mixed | 6 | 2 / 1 | 8 / 8 | 5 | Width2 prunes truth at rune4; widths16/128 retain it but rank it fifth. No top plaintext exact. |
| tiny zero key | 4 | 1 / 1 | 4 / 1 | 1, four tied paths | All widths retain all four paths and exact plaintext. Interruption path remains ambiguous. |
| prose0 | 49 | 3 / 6 | 512 / 512 | 1 | All widths retain true path and uniquely top-ranked exact plaintext. |
| prose1 | 54 | 3 / 3 | 64 / 64 | 1 | Same. |
| prose2 | 52 | 3 / 5 | 256 / 246 | 1 | Same; some other paths share plaintexts. |
| random register | 80 | 3 / 3 | 64 / 64 | 53 | Width2 prunes truth at rune10; width16 at rune45; width128 retains truth but ranks it53. No top plaintext exact. |

The true path is represented in the model for all six fixtures. The raw per-beam fields separately report representation, first pruning position, survival, rank, top ties, exact true-path plaintext, and whether any/all top plaintexts are exact. A `true_path_exact_plaintext=false` after pruning means that path is absent from the retained result; it does not mean applying the correct model path gives wrong arithmetic. All truth paths produce exact plaintext in exhaustive enumeration.

All exhaustive alternatives satisfy the ciphertext/key transition relation; unique highest language score does **not** make a plaintext uniquely identifiable. Zero-key ambiguity demonstrates that even exact plaintext can leave four indistinguishable consumption paths. The random control demonstrates a scorer/register limitation: widening the beam until it preserves every path still does not make the scorer prefer truth. No score threshold, false-positive probability, or future-search calibration was estimated here.

## Evidence, execution and limitations

New code imports only Python standard-library modules. Before execution, relevant inherited reference/configuration/scorer source was inspected; none was imported. `check.py` duplicates the alphabet and documented key arrays explicitly, uses a sieve for prime totients, and reads the existing English count table as data. Thus cipher implementation is independent while the language evidence is **not** an independent corpus. No inherited code, shared records, production decoder or another worker's directory was changed.

Raw result files:

* `results/20260916T180408.121651Z-pilot.json` — full reference outputs/expected arrays/key streams/every-position traces; tiny fixtures and all paths.
* `results/20260916T180434.839675Z-main.json` — four larger fixtures, every compatible path/plaintext, beam outputs and retained prefix paths.

Each run directory includes contemporaneous command, working commit, environment settings, timestamps, source snapshots, input hashes, stdout/stderr and actual exit status:

| Run directory under `runs/` | Exit | Child seconds | Outcome |
|---|---:|---:|---|
| `20260916T180408.068725Z-pilot` | 0 | 0.0731 | Reference and tiny assertions pass. |
| `20260916T180418.984354Z-main` | 1 | 0.0767 | Invalid fixture token K detected before fixture generation/scoring. |
| `20260916T180434.710356Z-main-repaired` | 0 | 0.1826 | Same matrix after single-token C repair. |
| `20260916T180455.497718Z-retained-evidence-check` | 0 | 0.0360 | 908 re-encryption checks and beam membership pass; complete truth traces printed. |

`AMENDMENT-01.md` documents the task-code defect, its timing and one-token repair. The failed source and traceback remain preserved. It is not a cipher-control failure, and no scientific parameter was changed. Four processing commands used **0.369 seconds** total child wall time under 300-second individual limits; the 1200-second budget was not approached. The first source snapshot and PLAN hash capture the prerepair fixtures; the repair is explicit rather than silently rewriting history.

For a small reviewer rerun, copy `check.py` into `audit/next-review/` and execute that copy with argument `pilot` through `audit/next-01/run_logged.py`, using a fresh reviewer-owned run directory and recording the script, PLAN, six reference text files and quadgram data as inputs. The copy writes results under its own directory. `verify.py` accepts the two result paths and checks them without importing `check.py`. Each run produces fresh evidence; do not overwrite evidence.

## Recommendation

**Include literal-F non-consumption as a separately named candidate model in a later calibrated test; exclude claims that these results already validate automatic puzzle recovery.** Before any new puzzle test, freeze a bounded key/sign/reset/slice set and calibrate its complete selection procedure with controls containing both ordinary encrypted F and true literal-F interruptions, retaining ambiguity and tie handling. Measure truth survival and exact plaintext recovery separately from language ranking. The current simple prose controls justify that next control/calibration step, not a broad search or any inference about unsolved pages. Failure of Worker A's legacy rejection model does not test this model. Production repair and real-input execution remain separate future work.

Worker writes stopped after this report for independent review.
