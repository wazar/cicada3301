# P15 — five-bit XOR with invalid-code rejection

The frozen four-stream encoder has **no compatible complete plaintext path** for either original0 or17. All eight failures occur within the first23 runes, with no finite-key exhaustion. A separate support-only inverse reproduces them without the English model. This is an exact obstruction for the specified streams/start/encoder, not a scored language negative or a rejection of XOR generally.

The same four streams also fail all152 null cells (38 packets ×4). Therefore there are no complete scores, selected cells or meaningful rank tails. Raw summaries retain a `best` string naming the first row when every score is null; this is a sorting placeholder, **not a winning key**. Original raw outputs are unchanged; `disposition.json` makes the absent selection explicit.

| Stream | Original0 first impossible index | Original17 first impossible index |
|---|---:|---:|
| prime-minus-one, old sign−1 |22|5|
| prime-minus-one, old sign+1 |5|18|
| integer-phi, old sign−1 |4|1|
| integer-phi, old sign+1 |6|7|

Indices are zero-based. Highest queried actual key index25; all actual EOF-hypothesis counts0. Future key suffixes cannot repair an already impossible prefix: each rejected proposal must be invalid or equal to the previous accepted ciphertext. A valid unequal proposal must accept immediately. This creates hard XOR-domain support constraints beyond the observed equality mask.

## Frozen construction and instrument

Operands are k=(old M25 sign × numeric formula) modulo29, exactly four arrays, natural start0 and finite2048 draws. XOR never receives a negative Python integer. Each trial consumes one draw; p XOR k >=29 is forced rejection, a valid previous-output repeat rejects with.83 and accepts with.17, and any other valid proposal accepts with1. No EOF output is fabricated. Pages independently reset key/prior-output state. These are explicit engineering choices, not an inferred historical cipher.

The inverse enumerates all29 plaintext symbols and allowable acceptance positions. Forced invalids contribute log probability0; soft rejections ln(.83); accepted repeats ln(.17). Exact dynamic programming ranks complete joint paths using the unchanged English rune/boundary LM. It does not marginalize multiple paths into a plaintext posterior. Structural reachability itself does not depend on that LM, since its probabilities are positive and same-state dominance retains a representative of every reachable state.

Controls preserve the four complete M25 held source groups, exact character-to-rune maps/hashes, seeds331500..331503 and original cell pairing:

| Control | Length | Key selected correctly | Rune errors | Exact truth path rank among correct-key top16 | Draws / invalid / soft rejections |
|---|---:|---|---:|---|---|
| welcome |515|yes|6|outside16|575 /44 /16|
| jpg107-167 |319|yes|0|1|370 /43 /8|
| p56 |85|yes|0|1|93 /5 /3|
| p57 |95|yes|6|6|109 /11 /3|

All encoders complete. Key recovery4/4 is not perfect text recovery: only2/4 complete truth paths rank first. These failures are unchanged; no scorer/key/seed variant was added. Full truth paths remain valid and their independently calculated likelihoods are retained in `control-check.json.gz`. Observed repeat counts2/4/1/0 are descriptive; no claim that this encoder matches the entire puzzle's first-order distribution follows.

Eighty tiny exhaustive inverse cases and five direct probes cover forced invalids, soft rejection, accepted repeats and EOF failure. A second scalar encoder matches every RNG/event trace. Review20 independently checked2,900 transitions against exact rational event probabilities,60 tiny exhaustive DP cases,132 saved paths and all source/RNG/key maps before actual execution; no blocking defect was found. The bounded actual pilot followed that review, preserving imperfect detector power.

The actual replay checks all160 cell reachability results using a separate support-only inverse, every first-failure position and all38 null RNG strings. The null draws are uniform conditional on the exact adjacent-equality mask, not on XOR admissibility or rune histogram. Their universal failure illustrates that mismatch; it cannot supply a useful score calibration. All full generated null strings, partial-state histories, key arrays and input maps are retained. No forced plaintext was emitted for failed cells.

## Scope and reproducibility

Narrow prior inspection found byte/blob XOR references and no equivalent forced-invalid rune transducer in the inspected M25/M26/R18L7 material. This does not assert an exhaustive absence from all historical work. Exact coverage is the four signed-residue numeric streams, start0, specified one-draw invalid/repeat encoder, two independent pages0/17 and finite2048 arrays. Failure occurs long before EOF; no claim about other mappings, starts, streams or XOR encoders follows. No second variant was attempted.

Standard logger runs all exit0, one numeric thread: pilot0.256s, remaining controls0.198s, control replay0.089s, actual/null0.146s, support replay0.152s. The complete source/card/results are in this directory; scripts `../p15.py`, `../p15_check.py` depend on inspected `../p14.py` for fixed formulas/LM. The publication record retains all raw null-score placeholders and explains their disposition rather than rewriting evidence.
