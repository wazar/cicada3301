# R06 source-layout routes

No sustained readable text found. Completed45 discovery originals ×5 exact routes ×820 transform cells =184,500 real outputs and184,500 equally searched shuffled outputs. Runtime17.641s. Best real score−6.366162(original55, alternating line direction, affine8,11), compared with shuffled maximum−6.344981. Its unchanged output begins `CHERNSTHWESLUNGIAHJAFTHOEMNXTHOELBTHJEA...` and is not a reading.

Five routes:normal, full reversal, reversed source-line order, reversed runes within each source line, alternating direction by zero-based source-line parity (first line normal). Each route is an exact permutation with explicit `route_to_original` in retained outputs; concatenated source-line index intervals were asserted to cover every rune exactly once. No padding, fabricated rectangle or inferred missing line was used. Source lines are slash-delimited transcription lines, not certified physical image lines. Source character positions and non-rune tokens are retained without pretending transformed delimiters are reliable reading boundaries.

For each route, full affine `p=(a*c+b)%29`,a1..28,b0..28 (812 cells), plus8 cells from four known recipe keystreams with both additive signs at routed-page start0:DIVINITY exact8-rune key, literal13-rune FIRFUMFERENFE key, ascending primes, prime-minus-one. These are **rigid ordinary arithmetic** probes, not literalF non-consumption or repeat-rejection coverage. They deliberately overlap normal-route R01/R03 baseline work while adding only the four additional routes. No dictionary/layout cross-product.

Every page/control cell retains all4,100 candidateIDs/scores compressed and its20 strongest full outputs. Global `top_candidates.json` has20 output records with original page IDs, exact permutation, transform/key, raw rune indices and separate transliteration. Shuffles preserve rune counts and original layout lengths, not adjacency; comparisons are descriptive exploratory maxima rather than exact null calibration. All retained affine/keyed transforms passed independent scalar inverse arithmetic checks during generation.

Actual full route/affine/recipe search on a493-rune solved reference reversed and inverse-affine-encrypted witha7,b11 recovers the exact plaintext, truth rank1, retained among top20. The control uses one source line, so some route aliases coincide; it validates recovery for a full reversal and affine, not every possible line route's language power. Per-page matched shuffled searches supply corrupted-input behaviour. Exact positive-control outputs in `positive_control.json`.

Resume (complete checkpoint; runs control then exits):
```
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r06-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/parallel-01/inputs/page-map.json --input audit/parallel-01/reference/sources/solved_0_welcome.txt --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/structural.py r06 --seconds 820
```
Replay any artifact by indexing the original page with `route_to_original`, then applying its stored affine or signed keystream. Map back with the inverse permutation. Reserved originals were excluded throughout; all results remain UNREVIEWED.
