# OVERNIGHT-01 — Search the real puzzle, then test the strongest candidates

## 1. Assignment and permission

Work in `wazar/cicada3301`. Reviewed starting point: `cf3e07b68570a2b04d83252276d8c1bec62308f0`. Preserve newer commits and unrelated local work. Do not reset the checkout.

Run an autonomous, bounded exploration session aimed at recovering new Liber Primus plaintext. Use native sub-agents and actual local computation. This is permission to search the unsolved material, not just write another plan or run synthetic diagnostics.

**This assignment replaces the earlier audit-only limits, stop-after-one-test rules, prohibition on search expansion, and requirement for perfect recovery on every control before exploratory decoding.** It does not change historical results. Experiment 01 remains blocked under its original specification. Create a separately named exploration with the policy below.

The owner authorises execution, small new search tools, repairs to those tools, bounded adaptive follow-up, independent review, and publication to this fork without approval between ordinary steps. Work until the finite queue is exhausted, the hard budget expires, or a genuine operational blocker prevents useful work. Do not stop the whole session because one method, control, or candidate fails.

Use an **eight-hour elapsed wall-time ceiling**, measured from session start. This is a resource limit, not a promise to use all eight hours. Reserve the final 30 minutes for checkpoints, review, and reporting. Record the start and hard deadline with the host timezone. A user-supplied earlier stop time takes precedence.

## 2. The research policy: finding a candidate is not proving it

NEXT-01 case 66 ranked the planted DIVINITY/sign pair first. Its selected plaintext differed at the final rune on one page. That failed the exact-recovery gate. It did not show that looking at real candidate outputs would be meaningless.

Use these separate standards:

- **Arithmetic and data integrity are hard requirements.** Input identity, rune mapping, normal cipher operations, and declared fixed-path re-encryption must work. Quarantine or repair a mode with wrong arithmetic or unreproducible output. Other modes continue.
- **Search quality is measured, not assumed perfect.** Record truth rank, survival, top-k recovery, rune errors, and missed controls. Imperfect beam ranking or compatible endings do not globally prohibit candidate generation.
- **A score only prioritises review.** No language score, keyword match, or script PASS establishes a solution. Preserve the actual rune output and any alternatives.
- **A miss has a narrow meaning.** Report “no candidate found with this implementation and budget.” If a control failed, state that limitation. Do not exclude a cipher family or claim impossibility.

The central target is a justified rule that produces sustained readable text, without manually selecting letters to fit a story. A partial page can be useful. Do not require two pages to share a key or method before retaining a candidate.

Do not choose between true OTP, derived keys, or an anti-repeat mechanism as settled starting assumptions. Literal-F non-consumption and repeat-rejection key skipping are different models.

## 3. Read briefly; start computing

Coordinator reads `audit/reports/NEXT-01.md`, the relevant sections of `PARALLEL-01.md`, and the existing worker reports/code needed below. Give workers their specific paths and tasks. Do not make everyone reread the whole archive.

Reuse:

- `audit/parallel-01/inputs/dataset.json` and `page-map.json`.
- `audit/parallel-01/reference/` complete fixtures and independent arithmetic.
- `audit/f-interruption-01/` literal-F search and compatibility checks.
- `audit/experiment-01/` frozen recipes, controls, and retained failure.
- `audit/alphanumeric-01/v1/` corrected token field and its uncertainty records.
- `audit/alphanumeric-01/REPORT.md` for exact previous payload coverage.

Check that imported modules do not execute tests or write files on import. Do not rerun old scripts that overwrite fixed-name evidence. Use inert helpers or isolated copies in this session's directory.

**Limit initial orientation and common scaffolding to 45 minutes.** Start the cheap real-data searches as soon as their basic arithmetic works. Do not use all the setup budget when less is needed. Do not build a new research framework or stop to regenerate a missing multi-language model.

## 4. Team and execution

Use one coordinator plus up to three concurrent workers, subject to the actual runtime limit. Record real agent IDs. No nested agents or pretend delegation.

Initial assignment:

- Worker A: R01 known methods, then R02 clue keys and running texts.
- Worker B: R03 numeric recipes, then R04 periodic-key search.
- Worker C: R07 block as key, then R08 block as message.

R05 cross-page relations and R06 layout routes enter the shared ready queue. Give them to the next available worker. Use a fresh reviewer when a slot opens; review must overlap continued searches where possible.

Each worker writes only its own lane directory under `exploration/overnight-01/`. Only the coordinator writes shared configuration, status, candidate registry, or Git changes. Shared helpers become versioned, read-only inputs once workers use them.

Start with up to three single-threaded compute jobs if the shared CPU and memory budgets allow. Set a global CPU budget no larger than half the host's logical cores, with at least one core available. Coordinate any process pool against that total; do not allow each worker to start its own full-machine pool. Reduce concurrency under memory pressure or sustained swapping. Use the existing Python environment and installed tools.

Use resumable batches with a normal ceiling of 15 minutes. The coordinator can authorise a named finite batch up to 60 minutes within the total session budget after measuring a pilot. Avoid idle polling and unbounded retries. Use runtime waiting/continuation tools correctly. If persistent execution is unavailable, report the limitation rather than claim overnight activity.

Keep the Mac awake only with an available process-scoped mechanism. Do not change global power settings. Do not install packages, buy compute, invoke paid APIs, run downloaded binaries, or access unrelated private files. Small relevant public-source downloads are permitted, with sources and hashes. No unrestricted web or onion crawling. Existing ordinary public pages can support a specific clue, but do not turn this session into creator-identity research.

## 5. Minimal shared search contract

Create a small `SESSION.md`, `config.json`, and append-only `events.jsonl`. Each batch needs an exact enumerator/configuration, seed, input hash, code revision/hash, trial budget, and checkpoint. A short record is sufficient; do not write a long preregistration for every loop.

Use original LP2 filenames. Rune-bearing unsolved images are represented by the frozen map; p50's alphanumeric field is separate. Do not confuse a parsed segment number with an image number. Preserve existing boundary uncertainty. Never flatten byte/token data into the rune stream silently.

Reserve original images **4, 9, 14, 19, 24, 29, 34, 39, 44, and 54** for possible later validation. Other unsolved rune-bearing pages are discovery material. The mixed pages 49 and 51 remain available for the block tests. Metadata inspection is allowed on the reserve set, but do not decode it to choose keys or tune scores. If a candidate needs a reserved page, freeze its rule first, then record the reveal. A revealed page cannot remain labelled unseen. Existing public knowledge of these pages means this is an operational holdout, not a pristine scientific sample.

Prefer full pages or complete source-delimited passages over arbitrary 120-rune cuts. Where a prefix is required for speed, preserve its offset and reserve the continuation for that candidate's first check. Do not reject a useful prefix merely because its terminal rune is ambiguous.

Keep rune indices authoritative. Display transliteration separately. Respect word boundaries when mapping Latin source text to runes; do not silently combine letters across separate words into one digraph. Document spelling aliases. Reuse verified rune-form keys where available.

Use the existing score as one ranking view. Add a simple delimiter-aware word/rune-language view if feasible from already held texts. Keep training/tuning text separate from controls; do not count the same corpus under two score formulas as independent evidence. Do not delay real searches to train a sophisticated model. Retain top candidates even if no inherited score floor is crossed.

For each mode, use a small representative control sample and one corrupted-input/key check. Continue compatible exploratory searches while measuring limitations. Record whether the exact search, rather than only a known-key decoder, recovers controls.

## 6. Actual exploration queue

Start with the explicit bounds below. They are search limits, not claims of exhaustive coverage. Use cheap passes before expensive variants. Record exactly which combinations ran; a stage filtered by a weak first-pass score does not cover candidates it discarded.

Before repeating old work, spend at most ten minutes per lane checking its exact prior input/method/offset scope. Skip a provably identical run, or label a deliberate reproduction. A broad old “eliminated” label is not sufficient reason to abandon a lane.

### R01 — Reuse the actual known decoding methods

Run the four frozen recipes on complete discovery pages: DIVINITY, literal FIRFUMFERENFE, primes, and prime-minus-one. Use both arithmetic directions and explicit key starts. Begin with start zero; then test each phase for periodic keys, and numeric offsets 0–127 for the nonperiodic sequences.

Test these models separately: ordinary rigid arithmetic; corrected literal-F non-consumption; and the existing repeat-rejection decoder where applicable. Plaintext F must be emitted at a literal interruption. Do not apply two unrelated skip mechanisms at once without a separately named, controlled model.

Also run the cheap full affine family `p=(a*c+b) mod 29`, for a=1..28 and b=0..28. This includes direct reading, shifts, and Atbash-type rules. It is a baseline recheck, not a claim of novelty. Do not multiply every affine transform by every later model.

For unknown F choices, enumerate when affordable; otherwise use a bounded beam starting at width 256. Retain at least 16 alternative outputs and consumption paths for leading candidates. Widen selected cases to 1,024 or use exact local enumeration. Record ties and pruning; do not store only a fabricated unique winner.

Prioritise the literal-F model because it now has correctly reproduced reference rules and was not included in the blocked recipe test. Apply it to real pages in this assignment.

### R02 — Clue-derived keys and existing texts

Freeze up to 256 distinct rune-key arrays derived from verified solved text and explicit puzzle instructions. Start with exact clue terms and short adjacent phrases. Record a source location and conversion for every key. Preserve all aliases when different spellings map to the same rune array. Do not invent hundreds of vaguely related words.

Search ordinary and literal-F models with both arithmetic signs. Start at each page boundary. Test within-period phases for keys of at most 32 runes; enumerate longer phases only for retained candidates within budget.

Separately select at most eight short public texts already held locally, each justified by a specific documented connection. Use them as running keys. Begin with their natural starts and source-defined paragraph/chapter starts; permit at most 1,024 pre-listed offsets per text. Larger full-text offset scans require a recorded adaptive tranche, not an implicit unlimited expansion.

Apply expensive F-path searches to shortlisted ordinary candidates **and an independent fixed sample of other keys/offsets**. That sample is necessary because interruption handling can make a poor rigid score become a good decode. Record this limited coverage honestly.

### R03 — Numeric recipes tied to actual clues

Test a finite grammar, not arbitrary numerology. Initial sequences: ascending primes, prime-minus-one, integer totients, integer indices, Fibonacci numbers, and prime gaps. Fix indexing conventions explicitly; verify tiny terms before use.

Permit at most 32 named sequence families, including compositions or prime-index recurrences only where a specific authenticated/verified clue motivates them. Every composition needs a formula and source. Reduce modulo 29 at the declared step; do not conflate reducing before and after a nonlinear operation.

Use offsets 0–127, both arithmetic directions, and page resets first. Test a limited continuous-state or source-supported section-reset version as a separate model. Include literal-F handling on selected families. Retain large-number safety limits; do not start expensive factorisation of rapidly growing terms.

Save all sequence definitions and hashes. Do not expand into every arithmetic expression that happens to improve a short score.

### R04 — Recover a short repeating key without guessing its words

Search periods 1–32 per discovery page, then 33–64 only where the pilot is useful or remaining budget permits. Start with ordinary mod-29 Vigenere/Beaufort-type additive models. Do not claim the F model or arbitrary feedback was covered by this stage.

Use period statistics and rune-language scores to initialise an actual key search, such as coordinate improvement or simulated annealing. Use up to 16 deterministic restarts per initial cell. Cap and record the number of score evaluations.

Penalise or explicitly compare model complexity: a long adjustable key can fit a short passage by chance. Measure behaviour on matched random/wrong-key controls. For each fitted key, use roughly the first 75% of a page to select it and freeze it before scoring the remaining 25%, with unchanged key phase. Do not optimise on that continuation afterwards and still call it validation.

Preserve delimiter information where justified. Single-rune words are a soft constraint, not a forced A/I rule: rune transliteration is not a one-letter Latin alphabet. For strong periodic candidates, later test explicit F handling as a new model, with its own fit/check split.

### R05 — Shared keys, alignments, and reset points

Test whether pairs of discovery pages share a keystream under declared equal-start or small-offset models. Begin with offsets -16..16 and no free drift. Under the appropriate additive sign convention, subtracting aligned ciphertext can cancel a reused key; it does not automatically reveal either plaintext.

Use cross-page differences, repeated sequences, and delimiter patterns to generate constrained candidates. Where using a crib, draw from a frozen, small set of real solved-text phrases with compatible rune lengths. Never present text used as a crib as a prediction. Require the implied key or alignment to explain additional, non-crib text.

Test page-start, line-start, and source-supported section-start reset models separately. Filter state is distinct from key state. Do not invent section boundaries or let arbitrary free alignment fit a preferred message.

Report candidate relationships even without a full decode, but compare them with the actual amount of pair/offset searching. Reuse of a key is a hypothesis, not an established property of LP2.

### R06 — Page layout and reading order

Define at most eight deterministic reading routes from existing layout: normal order, full reversal, reversed source-line order, reversed runes within lines, alternating line direction, and other routes only when a real rectangular field or explicit clue supports them.

Preserve token/line identities and an invertible mapping back to original positions. Do not insert padding or manufacture a rectangular grid. Slash-delimited transcription lines are provisional image lines; label that limit and check relevant images for a serious candidate.

For each route, try cheap direct/affine transforms and at most 32 already justified key/sequence candidates. Do not cross every layout, dictionary, offset, and skip policy. Compare top results with matched route searches on controls.

Transposition preserves symbol counts but changes adjacency; neither property alone closes this lane. A layout pattern without a reproducible decoding is a structural lead, not a solved message.

### R07 — Use the pages 49–51 block as key material

Use the corrected, versioned 256-token field. Start with its previously studied base-60 byte interpretation; call that an interpretation, not ground truth. Do not spend the session re-transcribing already reconciled glyphs.

Test the corrected bytes against surrounding rune text first, then other discovery pages. Initial views are forward/reverse byte order and the physical 32-by-8 row/column routes. Use byte modulo 29 and explicitly defined rejection conversion accepting bytes below 232. Preserve each mapping's output length and leading zeroes. Do not pad, wrap, or discard bytes without declaring that rule.

Try both arithmetic signs and valid key offsets 0–255 where sufficient mapped key remains. Treat repeating a short mapped key as a separate periodic hypothesis. Prioritise literal-F non-consumption: the reported corrected-payload grid used a different skip model.

Permit up to eight further clue-justified representations or hash expansions, with complete definitions and hashes. No open-ended generator or KDF sweep. Keep uncertainty variants to a small pre-listed set supported by actual glyph alternatives, not arbitrary byte changes chosen to improve text.

Compare exact old coverage to the new input/model so the report distinguishes a repeated experiment from a genuinely different test.

### R08 — Treat the block as a message or structured binary object

Inspect the corrected byte interpretation for strictly verifiable format, checksum, compression, or public-key relationships using available inspected code. A 256-byte length does not identify RSA, a key, or ciphertext by itself. Do not start generic large-number factorisation or hash-preimage brute force.

With up to 128 source-backed clue keys, run a small explicit byte-cipher matrix using installed libraries and standard, recorded parameters. Start with repeating-key XOR and already implemented historical byte-cipher tests whose exact corrected-input coverage is absent. AES/stream-cipher modes require declared key derivation, IV/nonce handling, and their own known-answer checks. Skip unavailable tools rather than install a new stack.

Rank binary outputs by validated structure as well as readable text. Valid padding, a short magic prefix, or a few words is not proof. Limit decompressed output size and never execute recovered content. Verify full parser/checksum consistency when available.

Record which key/parameter combinations were actually tested. If the exact corrected-input matrix is already covered with adequate records, spend the lane's remaining budget on R07, R05, or R06 instead of repeating it without cause.

## 7. Diagnostics and adaptation must support, not replace, exploration

The terminal-rune diagnostic gets **at most 15 minutes** and runs alongside real searches. Preserve case 66 and inspect alternative compatible endings and one source-defined longer continuation. Do not tune a scorer until that one known answer wins. The purpose is to decide whether to retain more paths or more context.

Workers may implement small new search modules and fix their own code with regression checks. Leave inherited production code and old evidence unchanged. There is no requirement to repair or certify every old detector before using separate correct arithmetic.

Give every feasible lane an initial real-data batch before spending most of the budget on one favourite. As an initial scheduling guide, allocate about 30% of search compute to known/literal-F and clue-text routes, 25% to numeric/periodic routes, 20% to the token block, 10% to structural routes, and 15% to targeted follow-up and verification. These are budgets, not estimated chances of success. Record actual use and explain deviations.

At checkpoints, the coordinator can extend a promising lane in finite tranches: more declared offsets, a wider beam on a specific candidate, longer context, or another justified key family. Log the reason before execution. Count all attempts, including unsuccessful adaptations. Do not describe an adaptive maximum as a pre-registered significance result.

A lane that returns noise moves on. A failed control limits its conclusions. Missing optional models do not stop other methods. General housekeeping and new audits must not consume the session.

## 8. Candidate handling and independent checks

Maintain a shared candidate registry with input positions, exact key/recipe, transform order, offsets, reset rules, F/skip choices, full rune output, score components, and code/config hashes. Deduplicate identical plaintexts or equivalent transformations while retaining their origins. No silently corrected spelling or inserted letters in the raw output.

Keep at least the best 20 candidates per lane plus structurally distinct leads. Do not filter everything through the old -5.5 threshold or an automatic two-page requirement. Retain uncertainty around endings and multiple compatible paths.

Use labels with explicit meanings:

- `UNREVIEWED`: ranked by a program only.
- `REPRODUCIBLE_CANDIDATE`: independent code reproduces the claimed transform/output.
- `VALIDATION_SIGNAL`: an unchanged, frozen rule predicts material not used to choose it, under a documented test.
- `PARTIAL_SOLUTION_CANDIDATE`: sustained coherent text and a justified mechanism merit external scrutiny; not automatic proof or community acceptance.

Do not promote a result merely because it re-encrypts. Many adjustable keys and latent paths can fit a chosen message. Record free parameters, manual choices, key origin, and competing explanations.

For strong candidates, a fresh agent must read the original symbols at the relevant sites, independently implement the proposed rule, test the withheld continuation or appropriate reserved page without tuning, and compare with matched search controls. A reviewer must see raw text, not only a polished interpretation. Use unavailable context as an explicit limit, not an invented success.

Repeated tests on the same reserved material consume the holdout. Preserve that history. After adaptive selection, report exploratory ranks and control comparisons rather than an unsupported tiny p-value. Wider searches and more flexible models need stronger follow-up evidence.

A credible partial result triggers immediate preservation and deeper independent checking, not automatic shutdown of all unrelated workers and not a public claim of a full solve.

## 9. Logs, checkpoints, and publication

Use unique run directories and append-only event records. Save timestamps, actual process/agent IDs, commands, source hashes, input hashes, seeds, exit codes, durations, completed work counts, and resumable state while executing. Do not reconstruct missing execution history later.

For large searches, keep per-candidate identifiers/scores in compressed tables, exact recipes/seeds, and full outputs for retained candidates and sampled controls. A deterministic replay must recover any referenced output. Do not commit gigabytes of redundant arrays or model caches. Record any discarded information.

Update `exploration/overnight-01/STATUS.md` at batch completion and roughly every 15 minutes during long work. It must show what is actually running, progress, current candidates, remaining budget, and the next queued task. Low-cost checkpoints must not repeatedly interrupt useful computation.

If context or token limits approach, save the queue and exact resume commands and use supported continuation/compaction. If continued supervision is impossible, state the actual remaining process state. Do not claim that a session will continue after it has stopped.

Only the coordinator makes focused commits and pushes completed checkpoints/final reviewed work to the owner's fork under the standing permission. Stage only this assignment's files. Do not force-push, mix in unrelated setup work, publish secrets/private paths, or contact upstream. Preserve failed and inconclusive scientific results rather than hide them.

## 10. Final deliverable

Write `exploration/overnight-01/REPORT.md` and a short pointer/summary at `audit/reports/OVERNIGHT-01.md`.

Lead with plain-language answers:

1. Did we recover any credible new text? Show it unchanged, with location and limits.
2. Which real puzzle paths ran, on which pages, and how much actually completed?
3. What are the strongest surviving candidates and why are they stronger than random fragments?
4. What failed or remains inconclusive, including imperfect controls?
5. What should the next session continue, and what exact commands resume it?

Include a path-by-path table of candidate counts, compute use, real-data coverage, control behaviour, and output locations. Distinguish planned work from executed work. State that no candidate survived if that is the result; do not turn weak fragments into progress claims.

**This session must prioritise actual exploration. A report consisting only of a new synthetic diagnostic and a recommendation to ask for another assignment does not satisfy the task when runnable real-data paths remain.** Finish with results, checkpoints, honest limits, and published commit hashes.
