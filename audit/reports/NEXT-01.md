# NEXT-01 — recipe gate stopped; input and literal-F checks completed

**The real four-recipe puzzle experiment did not run.** A required positive control
failed, so the frozen rule stopped it before calibration or real decoding. The
independent alphanumeric and literal-F tasks completed, and a fresh reviewer
reproduced their key results. No key search was expanded or production code repaired.

## Owner summary

1. **Recipe experiment: `BLOCKED_BY_POSITIVE_CONTROL`.** The planted DIVINITY key
   ranked first, but one synthetic page decoded 119/120 runes exactly. That fails
   the required exact-recovery gate. It is an instrument limitation, not evidence
   that any of the four recipes fails on the puzzle.
2. **Alphanumeric block:** pages 49–51 contain256 two-character tokens in 32 rows.
   A coordinate-linked transcription agrees with the previously corrected Round19
   payload under its historical base60 interpretation. Substantial prior work
   exists; this material was not ignored by the community.
3. **Literal-F model:** all 919 runes of three keyed references reproduce while
   preserving 14 Fs without consuming key values. Unknown-choice tests demonstrate
   both successful recovery and genuine ambiguity. This separate model has a
   justified next control/calibration step, but no unsolved-page application yet.
4. **Recommended next experiment:** a narrowly scoped synthetic diagnostic of the
   retained terminal-rune failure, to distinguish compatible-path ambiguity,
   scoring preference and pruning before proposing another real-input gate.

## 1. Frozen recipe test and its stop

[Experiment report](../experiment-01/REPORT.md),
[frozen specification](../experiment-01/preregistration.json),
[cell accounting](../experiment-01/ACCOUNTING.json).

The specification hash was frozen before any control decode:
`ed0fdd288c12a705f3688924a813960d489b20c504116002ef6a811adfced9ea`.
It retains four complete 2,048-symbol arrays: DIVINITY, literal FIRFUMFERENFE,
ascending primes and prime-minus-one totients. Both arithmetic signs, rigid and
legacy beam400/max_skip3, offset0 and per-page resets remained fixed. All eight
signed arrays are distinct. Images 0/1's first 120 rune indices and hashes were
prepared from `parallel-01-inputs-v1`; preparing those arrays was not decoding them.

Sixteen recipe/sign/model cells each required 20 two-page positive cases. All
executed controls used the actual structured keys and messages frozen before
scoring. The first full-choice pilot passed. Its measured0.0812-second decode time
supported one 300-second main batch, which stopped after 5.80 seconds at the first
required failure. No budget increase or scientific retry followed.

| Stage | Actual outcome |
|---|---|
| Positive pairs |67 executed:66 passed,1 failed;253 skipped |
| Candidate page outputs |2,144 complete outputs retained, including scores and key-use traces |
| Calibration |0/100, skipped after failed positive |
| Held-out negatives |0/100, skipped |
| Separate shuffle panel |0/100, skipped |
| Real candidate page outputs |0/32, not executed |

The failure was ordinal 66, DIVINITY/sign+1/rejection beam, case6. On page0 the last
rune should be A (index 24), using key index 123. The decoder emits S (index 15), using
key index 122. Its output scores −4.0951382034, slightly above truth's −4.0963059746.
Page 1 is exactly correct. The planted recipe/sign remains the top joint hypothesis.
The encryptor never required more than one consecutive rejection, so exceeding
max_skip3 does not explain this failure. We do not infer that pruning caused it.

[Complete failure record](../experiment-01/outputs/20260916T180521.719679Z/case-066.json)
retains plaintext, ciphertext, key, encryption state, every candidate output and
alignment. Trace instrumentation matched the unmodified production decoder on
every beam call. The reviewer independently reproduced selected cases and all 32
choices for each, including this failure. Later recipes appeared as competitors;
their unexecuted planted cells are not credited as passing.

**No calibrated false-flag estimate, puzzle miss or recipe rejection follows.**
Continuous keys, other offsets/registers/pages, different per-page methods and
literal-F interruptions were not tested on unsolved material.

## 2. The alphanumeric input and previous coverage

[Input report](../alphanumeric-01/REPORT.md),
[versioned transcription](../alphanumeric-01/v1/transcription.json),
[readable text](../alphanumeric-01/v1/transcription.txt),
[uncertainty table](../alphanumeric-01/v1-review/UNCERTAINTY.md).

The block has 10/13/9 rows on pages 49/50/51, with 80/104/72 tokens respectively.
All 256 tokens have two characters;161 are distinct, and 59 symbols occur. Case,
leading zeroes, page cuts, pair order, source whitespace, surrounding rune text
and inspection coordinates are retained separately from the rune stream. Its
established rune hash is unchanged.

A fresh small relikd retrieval matches the local copy. Five token disagreements
with scream314 and additional decimal-column conflicts were inspected directly;
the current reconciliation supports the already corrected text. Twenty sites have
explicit alternative readings and coordinates. The new coordinates also correct
three inspection rectangles where an inherited grid merged or split visible pairs.
No inherited transcription or grid was changed.

Under the **historical base60 hypothesis**, this text reproduces Round19 C1's
resolved 256-byte payload, SHA256
`3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`.
Agreement supports input consistency, not proof of the intended encoding. The
reviewer inspected index 45 against the original image: the tall footless glyph
supports lowercase l in `1l`, rather than the old uppercase-L reading.

The specific prior-work check found campaigns VII/IX/XX and rounds13/18/19, among
other references. Some retain code and narrative results rather than complete
outputs. C1 retains 20,160 candidate rows for a corrected-input grid, with explicit
decoder/register/offset bounds; its records are stronger than a broad negative
label. None of that establishes a universal exclusion. Other later references
were located but not exhaustively traced. Shared-source errors outside inspected
sites remain possible: copied-source agreement is not an independent blind read.
The worker proposes a bounded blind transcription check; it was not performed.

## 3. Literal F is a separate, tested rule

[Model/control report](../f-interruption-01/REPORT.md),
[frozen plan](../f-interruption-01/PLAN.md).

At a labeled interruption, ciphertext F emits plaintext F and leaves the key index
unchanged. Normal encrypted F still consumes a key value. Deleting F and skipping
key draws under a repeat-rejection rule are different operations.

| Complete reference | Output runes | Key values consumed | Literal interruptions |
|---|---:|---:|---:|
| WELCOME |515|504|11|
| Circumference |319|317|2|
| AN END |85|84|1|

Independent arithmetic matches every expected rune and records every key transition.
These supplied labels validate the rule, not an automatic finder or an independent
image transcription.

Two tiny fixtures and four larger fixed fixtures compare exact path enumeration
with prefix searches at widths 2/16/128, retaining boundary ties. All 908 compatible
paths re-encrypt correctly. The true path is represented in every fixture, but:

- Three short prose cases recover the exact top-ranked path at all tested widths.
- A tiny zero-key example has four paths with identical plaintext and tied scores.
  Exact plaintext does not uniquely identify consumption history.
- A tiny mixed case ranks truth fifth; width 2 prunes it.
- A uniform-rune case ranks truth 53rd of 64; widths 2/16 prune it, while width 128
  retains it without selecting it.

This distinguishes model compatibility, pruning, ranking and exact output. These
few cases do not measure general language power or false-positive risk. The English
count table is shared evidence even though the arithmetic/search code is separate.
A later literal-F puzzle test needs its own actual-key controls and complete
selection calibration. A's failed key-skip gate is not a test of this model.

## 4. Review, evidence and task-code defects

Entry commit: `beee1b995e142ba920280736e9e45835abbf650a`.
Actual native workers: `/root/next_experiment`, `/root/next_alphanumeric`,
`/root/next_f_model`; fresh reviewer `/root/next_reviewer`. No nested agents.
[Coordination record](../next-01/COORDINATION.md),
[review report](../next-review/REPORT.md).

Three workers ran concurrently with separate directories. The existing environment
was reused, numerical libraries had one thread, and at most two heavy jobs were
permitted. Every processing run has a unique evidence directory, actual timestamps,
command/commit, input hashes, code snapshots, stdout/stderr and exit status. No
previous run directory was overwritten. No full audit or T0 rerun was performed.
Only one small public text retrieval was needed. No installs, training, paid APIs,
large downloads or puzzle binaries. All commands finished within 300 seconds.

Two new task-code defects were preserved and corrected:

- C's first larger-fixture attempt contained Latin K outside the declared rune-token
  alphabet. It failed before generation/scoring. A one-token K→C correction retains
  the failed source/traceback and a separate rerun; no scientific parameter changed.
- A's post-stop accounting helper tried to read elapsed time from its own still-running
  log record. Its KeyError and original source remain recorded. The correction
  reread existing results only; it did not retry the failed scientific cell.

The reviewer independently matched 160 production decode choices, reconstructed
all 919 reference runes and key transitions, checked all 908 F alternatives, and
viewed a disputed alphanumeric glyph. Two reviewer runs passed without changing
worker artifacts. It found no release-blocking defect and accepted only the stated
scope. The real continuation code remains unexecuted and unvalidated here.

Private checkout prefixes in two failure tracebacks are replaced for publication;
original bytes remain locally excluded from Git, and original/published hashes are
recorded. Scientific outputs, frozen specifications, code snapshots and input bytes
are unchanged. Complete passing and failing candidate outputs are retained despite
their volume; no best-looking-only selection was published.

## 5. One next experiment, and the stop point

**Prioritise a synthetic terminal-path diagnostic of retained case 66.** Freeze its
ciphertext, key, plaintext and prefix state. Independently enumerate compatible
endings over the last six positions, preserving every path and the true path;
compare model validity, score and whether the finite beam retains each. Use the
original full prose to predefine the first complete-word boundary strictly beyond
rune 120 as one extension, without selecting a stopping position by score. This tests whether the observed failure
is tied to terminal context, path ambiguity or search approximation. It does not
assume a scoring repair will make exact recovery identifiable.

Stop at that fixed case and extension with a 300-second limit. Do not change the
old gate, tune thresholds, rerun the four-recipe puzzle test, or apply either model
to additional real pages. Any proposed decoder/gate revision requires a separate
preregistration and fresh controls. This is the smallest next experiment that
addresses the actual blocker without drawing a puzzle conclusion from it.

The alphanumeric blind-read proposal and a separately calibrated literal-F test
remain distinct later options. All inherited research code/data, earlier audit
reports and raw logs remain unchanged. Reviewed task work is published to the
owner's fork; unrelated setup work is excluded. **Stopped after NEXT-01.**
