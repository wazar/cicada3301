# S18 — reversible three-state opcode words

On originals 0 and 1, the only fixed three-state permutation assigned to each rune that makes every explicit word act as identity on **all three initial states** is the all-identity assignment. Thus both pages contradict the frozen requirement of at least one nonidentity observed opcode. This is an exact result for this finite program model, not a general rejection of hidden instructions.

## Model and proof

Each of the 29 rune labels denotes one of the six permutations of three states. Homophones are allowed, and each page may use its own map. A word executes its runes in order and must return every possible initial state to itself. Word boundaries and runes remain exactly as recorded in F06. This differs from fixed-edge graph walks: an opcode can act at every state and its destination depends on that state.

Let A contain a word's count of each rune in each row. Permutation parity is a homomorphism from S3 to GF2, so an identity word necessarily satisfies A·s=0 modulo 2, where s records each rune opcode's parity. Both actual matrices have full column rank 29 over GF2. Therefore every opcode is even.

The even subgroup A3 consists of identity and the two three-cycles, and is isomorphic to the additive group GF3. Once all opcodes are even, each word necessarily satisfies A·e=0 modulo 3 for their cycle exponents. Both matrices also have full column rank 29 over GF3. Consequently every exponent is zero and every opcode is identity. The cyclic subgroup coordinates are a proof invariant, not a proposed additive plaintext cipher.

| Page | Runes | Explicit words | Used labels | Rank GF2 | Rank GF3 | Consequence |
|---|---:|---:|---:|---:|---:|---|
| 0 | 262 | 59 | 29 | 29 | 29 | All opcodes identity |
| 1 | 266 | 63 | 29 | 29 | 29 | All opcodes identity |

For each page and field, 29 independent original word rows and an explicit modular inverse are saved. `s18_verify.py` reloads the original rune sequences, reconstructs those rows by direct counting, checks the stored source maps and verifies both products A·inverse and inverse·A equal identity. It does not import the elimination implementation. All four certificates pass. Independently enumerated S3 composition verifies all 36 parity cases and all nine A3 cyclic-addition cases.

## Controls

Forty positive panels use twenty random surjective 29→S3 maps on each actual word-length schedule. Each generated word has an arbitrary prefix followed by a rune whose opcode is its inverse; one-rune words use identity. Every control codebook and every emitted page represents all six opcodes. All programs close for all three initial states. Full maps, words, inverse choices and state paths are retained, and an independent direct permutation interpreter reproduces every saved path. The rank obstruction never rejects these nontrivial controls.

Sixty-four tiny three-label word collections were checked against all 216 opcode assignments each, totaling 13,824 assignments. Thirty collections receive a rank obstruction and none has a nontrivial solution; 31 have nontrivial solutions and remain unobstructed. Three have no nontrivial solution but insufficient rank for this route, correctly remaining inconclusive. Thus the necessary-invariant method is not claimed complete when ranks are deficient.

## Limits and provenance

The test assumes a fixed opcode per rune, exactly three hidden states, reversible transitions and identity action for every initial state at every explicit word. Closure only for a designated initial state, a nonidentity target action, changing opcode meanings, more hidden states, parameters, multiple programs per word or different units are outside scope. The vacuous all-noop program remains compatible and is rejected only by the explicit nontriviality requirement. No language score, key search, ciphertext edit, new image or checksum assumption was used.

`S18-CARD.md` froze the experiment before controls. Source `worker-f/F06-maps.json` SHA-256 is `74bdf46e10ce11080762e82350004bd95ea1952a866a9778b3e746c20012973b`. `S18-result.json` retains all count rows, ranks, certificate inverses and full maps for certificate words. `S18-controls.json.gz` retains the complete controls, group tables and tiny exhaustive results; seed 1709202618. `S18-proof-check.json` records independent verification. Implementations are `s18.py` and `s18_verify.py`.

Logged runs `20260917T022023.472189Z-S18-controls`, `20260917T022036.627493Z-S18-actual` and `20260917T022125.841109Z-S18-proof` all exited zero without timeout, under one second combined. Exact commands, inputs and executable snapshots remain in their run directories. Reproduction modes are `s18.py controls`, `s18.py actual`, then `s18_verify.py`, through the standard logger with one numerical thread. STOP and the original 2026-09-17 03:30:37 UTC deadline remain binding. No earlier scientific or shared artifact was changed.
