# M28: historical reset-clock mismatch confirmed; bounded pilot frozen

The historical `encipher_ctfeedback` resets its seed pointer to output index i on every rune, then advances it locally on rejection. Its companion `_feedback_beam` carries the previous accepted pointer forward. These are different cipher constructions. The discrepancy is exact source behavior, not an inference from old prose. All historical files remain unchanged.

On four complete held solved-source controls, the reset inverse can represent every true plaintext; the cumulative inverse cannot represent any of them. First impossible positions (zero-based) are 34, 4, 24 and 30. This reachability comparison allows cumulative skips through the entire finite source, so failure is not merely a beam-width or maximum-skip limit. Actual coefficient/sign search ranks the true cell first on all four, and each defeats all 19 conditional-repeat nulls. The best-ranked plaintext still has 2/515, 1/319, 0/85 and 2/95 rune errors. True plaintext ranks within the winning cell's saved top16 are outside16, 2, 1 and 4. Thus arithmetic capability, key recovery, plaintext ranking and detection are separate findings.

## Exact scope and source substitution

Only one source version is tested: `liber-primus/data/keys/armada18/mabinogion_vol1_guest_edwards_ed.txt`, full 132,028-rune finite sequence, start0, no wrapping/padding. Header text is retained. Historical greedy `eng_to_idx` transliteration and aliases V→U, K/Q→C, Z→S are reproduced. `source.json` holds raw-byte and loaded-value hashes, all values, source character intervals, and exact AST-extracted historical encoder text/hash. The original optional `data/keys/mabinogion.txt` is absent. This is explicitly an extant-source substitution, not reproduction of that absent source version or proof that an old optional-key sweep ran.

Frozen family: k=1 feedback f0=0; fi=a*C[i−1] mod29; a=1..28; signs±; 56 cells. Reset retry starts K[i] for every output. Rejection probability .83, with historical forced-output behavior when a rejected draw reaches the finite key's end. No key/coefficient/offset expansion follows this pilot.

Constant-seed controls hide the clock defect: every retry gives the same key value, so it gives the same ciphertext rune regardless of the clock. Moreover retries with a constant seed cannot suppress a repeat: eventual acceptance (or forced EOF) emits the same repeated rune. A successful constant-seed control therefore does not validate nonconstant-key clock semantics.

## Inverse and independent verification

For fixed previous ciphertext, feedback is known. A rejected draw fixes plaintext to c_prev+sign*(K[j]+f). All subsequent rejected draws must have the same key value. The inverse therefore has a direct candidate plus, when compatible, a candidate that rejects the initial equal-key run and accepts its first differing key. Repeated-output retry traces for the same plaintext are summed, not ranked as distinct plaintexts. If an equal-key run reaches EOF, the final mass combines ordinary acceptance and forced output. The saved `forced` field on that aggregated terminal trace means forced EOF is possible; it does not mean every event in that probability mass was forced. Actual encoder traces separately record forced EOF exactly.

The fixed LM objective is frozen P03 English-register log probability plus the log of each marginal local encoder probability. Exact DP retains sufficient last-two-token state and selects the best complete plaintext; no held-continuation claim is made. All 56 cell winners and the selected cell's top16 distinct plaintexts are preserved. There may be more than16 viable plaintexts; exact local options remain reconstructible from retained cipher/key/code, and truth reachability is checked independently of the ranked subset.

`kernel-check.json` passes 60,204 conditional probability-table comparisons against independent recursive forward probabilities and 60,204 normalized plaintext-conditioned forward distributions, 100 AST-versus-port finite-buffer encoders, and 80 tiny exhaustive top16 comparisons. Full output replay passes all 19,916 stored plaintexts, 274 exact-stuttermask nulls, and all 280 search packets. The largest checked key index is515; no unsupported outputs or control EOF fallback occurred in the real-size test.

## Real discovery pilot

| Original page | Best cell | Joint score | Conditional-null tail |
|---|---|---:|---:|
| 0 | a8/sign+1 | −4.58957979 | 2/100=.02 |
| 17 | a13/sign−1 | −4.75965723 | 80/100=.80 |

Page0's isolated upper-tail fluctuation is not supported by page17 and its complete output is incoherent. These two-page descriptive tails do not include all earlier experiments. Nulls preserve every observed repeat position exactly, choose uniformly among the other28 runes on nonrepeat positions, and repeat all56-cell selection. They alter histograms; this is a model-specific comparison. In particular, neither a .02 tail nor English-looking short fragments establish a decode. No oracle claim or source-family exclusion follows.

Raw selected outputs and alternatives, their key-reuse/source maps, all null inputs/scores, and language-free diagnostics (IoC, distinct-symbol count, compressed length) are retained. The English-trained scorer and overlapping solved-source register limit interpretation; no claim is made about other plaintext registers.

The 280 searches contain 15,680 top1 cell fits plus280 selected-cell top16 fits. Cost pilot .0538 seconds per search; full run28.62 seconds; independent replay4.97 seconds. No failed M28 runs. All commands, code snapshots, input hashes, stdout/stderr and exit codes are under `runs/`; final `manifest.json` hashes evidence. No reserved pages, historical edits, Git operations or nested workers.
