# N16 — full page-local Morse grammar

**No new cipher coverage or candidate: under the frozen assumptions, full-grammar feasibility is equivalent to P20's binary gap relaxation.** The executable test exposed this degeneracy; its results and controls are preserved, and no nonempty-class requirement was added after seeing them.

The extension allows a different fixed rune→dot/dash/gap map on each page. It therefore leaves P20's shared-map UNSAT intact. The frozen36-character A–Z/0–9 table and one/two-gap serialization are unchanged; punctuation and extra symbols are excluded. Page edges may cut codewords or gap sequences. Visible F06 word boundaries are ignored. No English ranking was used.

## Exact outcome

| Input | Full grammar | Nodes | Seconds |
|---|---|---:|---:|
| Original0 |SAT, plus second distinct observed-rune map|526|.301 first map|
| Original1 |SAT, plus second distinct observed-rune map|435|.255 first map|
|19 matched P20 comparator pairs, pages independently|18SAT /20UNSAT /0UNKNOWN|all retained|38.43 total batch|

All38 comparator pages were tested; no favorable subset was selected. They reproduce the existing P20 first-symbol/exact-repeat-mask streams, not new samples, and do not preserve inventories. These are feasibility frequencies, not a selected significance claim. Full rune/trit maps, complete streams, every decoded run with possible partial-edge letters, source coordinates, explicit clauses and proof trees are saved. Both actual first maps use only dot and gap; output sequences consist mainly of E/I/S/H/5 and are not plaintext recovery. A second distinct mapping was retained for each actual page, with its own explicit blocking clause and proof/witness.

## Why the apparent full grammar adds nothing

Every complete Morse code has at most5marks, and no valid serialization has3consecutive gaps, so full validity implies the binary constraints. Conversely, take ANY satisfying binary gap assignment. Label every nongap rune dot. Each nonempty inter-gap run then has length1–5 and is one of E(`.`), I(`..`), S(`...`), H(`....`) or5(`.....`). One/two-gap sequences satisfy the serialization. Partial page-edge runs of at most5dots are valid fragments as well. Thus the same binary witness always extends to a full grammar witness. This is an exact equivalence, not a empirical inference from SAT counts.

The earlier proposal overlooked that the frozen model did not require both dot and dash classes to be nonempty. The diagnostic directly extends both original P20 page-local witnesses and every N16 SAT witness to all-dot nongaps, retained in equivalence-witnesses.json. No claim is made about an amended surjective model, but no such amendment is executed or recommended as a repair here. The measured fitting freedom makes grammar alone unsuitable for recovery under this format.

## Controls and verification

All four complete source-backed P20 fixtures are SAT (27/35/200/482nodes). Their true trit sequences and full source-transliteration/Morse serialization independently validate. However, each found map misclassifies10rune roles by collapsing the true dash class to dot: trit errors587/283/76/88. This is a failed unknown-map recovery control, preserved explicitly. SAT acceptance is the only instrument capability demonstrated, not recovery or uniqueness.

Eight tiny fixtures exhaust378ternary assignments, including an UNSAT repeated-symbol example, and three complete hand-code fixtures pass. The separate no-import checker rebuilds every clause with set arithmetic, checks each domain propagation/branch/conflict, checks actual source-coordinate maps, verifies all P20 comparator RNG streams and source hashes, and accepts streams using an independently structured finite automaton of code prefixes and one/two-gap states. It verified50,208proof nodes including the two second-map searches and tiny fixtures. SAT trees may terminate at a witness; UNSAT trees cover every allowed branch. All44main instances terminate before the frozen120second/one-million-node bounds. No numerical solver or assumed solver status certificate is involved.

All scientific batches passed; no code repair or parameter tuning occurred. The full-grammar feasibility equivalence was recognized after execution and published rather than hidden as a successful stronger test. Controls/source hash links, complete arrays and exact errors remain. No new images, reserved pages, English scoring, keys or shared files were used. N14's separate transcription-row qualification remains at worker-n/N14-provenance/QUALIFICATION.md.

Decision: freeze this Morse grammar extension as redundant for feasibility and inadequate for unknown-map recovery. Do not advance actual SAT strings or expand timing/class conventions based on them.
