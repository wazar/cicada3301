# P30 — plaintext FIFO autokey with nonconsuming literal F

The fixed search recovered all four planted complete plaintexts and seed cells at rank one. Originals0/17/55 gave matched full-procedure upper tails .80/.25/.25. No coherent complete output was apparent in the 48 retained global alternatives. This is a bounded English-register, literal-F, additive-feedback result; it does not exclude arbitrary autokey constructions or seeds.

## Relation and prior scope

An ordinary rune satisfies p=(c−sign*queue_head) mod29, followed by popping that head and appending p. The alternative at ciphertext F emits plaintext0 and does not change the FIFO. Boundaries affect only the frozen P03 rune/boundary LM. Initial queues are precisely the first16 existing clue keys, all phases and both signs (162 cells), at natural page start. There is no wrapping of the seed, padding, repeat rejection or extra seed inference. Queue length is invariant; the appended plaintext creates subsequent key material.

The targeted checks found C1 round12's history-function/all-equal-seed family, campaign18's autokey with rejection consumption and future zero-padding, worker-a EVENT-CLOCK-01's append-on-rejected-draw/no-literal-F model, and M28's ciphertext feedback. These overlap feedback arithmetic but do not implement this combined clock and literal-F rule. This is an existing-method extension, not new-family credit or exhaustive historical novelty.

Width64 stable beam search retains at most16 paths per cell; normal branches precede literal branches in score ties. There is no state deduplication or stochastic branch prior. The LM uses five previously frozen solved sources, .5/8/5 interpolated smoothing, rune29 boundaries and start context(29,29). All candidate seeds receive identical complete-page search. Global alternatives are distinct by (plaintext,literal positions); encountered aliases are retained. Higher-scoring pruned paths remain possible: maxima are beam-retained, not exact global maxima.

## Controls and cost

The four held sources welcome, jpg107-167, p56 and p57 have515/319/85/95runes. They plant clue indices0/5/10/15, phases0/1/2/3 and alternating signs. At plaintext0, the frozen index%3 rule selects literal positions. All four unknown162-cell searches select the exact seed and plaintext, true path rank1, zero rune errors and no reported truth pruning. Complete control forward traces and source-character maps are retained. Cipher doublets are22/12/6/5: this raw encoder does not explain observed repeat suppression, and no rejection wrapper was silently added.

All100 tiny ciphertext cases (length≤6) exhaustively enumerate every literal-F choice; the beam's top16 scores match. The pilot takes2.56seconds for the long first control, forecasting164seconds for64searches and roughly20.7MB compressed. Completed searches take48.67seconds and11,462,463compressed bytes. Four control searches plus three actual searches and57 nulls total64searches,10,368cells,139,968retained paths and79,062,804recorded beam expansions. Fewer than16 paths exist in some short-page cells; none were invented to fill the table.

## Actual conditional comparisons

Each null preserves both exact F positions and exact adjacent-equality locations, choosing other nonF runes uniformly excluding the preceding nonF value. The number of choices at each position depends only on the fixed masks, giving a uniform conditional reference law. Histograms and longer-range structure are not preserved. This is not an asserted ciphertext generator. All19 nulls/page undergo all162 cells and the same beam/selection budget; resolution is .05.

| Original | Runes/boundaries | Best nats/token | Null maxima at least actual | Upper tail |
|---|---:|---:|---:|---:|
|0|262/59|−4.50581569|15/19|.80|
|17|273/69|−4.48776029|4/19|.25|
|55|76/17|−4.36176391|4/19|.25|

These are reused exploratory discovery inputs, not new independent confirmation. All48 complete global alternative strings were read without repair. Word-like fragments are not evidence of a message, and no candidate is advanced. The register, fixed seed list, optional-F relation and finite beam jointly delimit this miss; no key/phase/beam expansion follows it.

## Reproduction and audit

`p30.py` implements the production queue and search; `p30_check.py` independently uses an append-only key stream with an advancing cursor, reconstructs the LM from five raw sources, and checks every retained plaintext/literal path, final queue, consumed count and forward ciphertext. It reproduces all139,968 path scores (rounding below1e−12), all key grids, control source maps/events, all57 null RNG streams, retained maxima/global aliases and tails. It does not independently replay full beam pruning histories; those diagnostics remain subject to fresh review.

The first local control checker failed because it demanded exact float equality for tiny scores accumulated in a different grouping. That failed log is preserved. It was corrected to1e−12 tolerance, matching the already declared arithmetic comparison, without changing scientific outputs or search parameters; corrected controls and full replay pass. All scientific search jobs exited zero. Source files, raw pages, full cell outputs, complete inputs and consumption/literal maps are retained. No reserved page, image, installation or Git mutation was used.

Fresh independent review62 passed: `../../review-62/REPORT.md` reproduces all139,968 retained paths,10,368cells, all57null RNG streams and complete scoring/selection/tails. Its separate ring-buffer/heap stable beam matches the four true control cells and three actual winners, confirming truth survives all four controls. P29's separate review58 has already passed and is linked in its own report; it is not evidence for this experiment.
