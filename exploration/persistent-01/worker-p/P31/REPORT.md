# P31 — canonical cyclic Burrows–Wheeler format

Originals0/17/55 are not complete cyclic BWT last columns under the frozen canonical rune order. Every possible primary row was inverted and every distinct preimage necklace was retransformed in full; none matched its input. All four actual-source encoded controls recover the original source up to rotation. This is an exact format miss, not a language or general compression exclusion.

The hypothesis is one standard reversible text-preprocessing stage, speculative rather than inferred from a puzzle instruction: sort all cyclic rotations and emit their last column, no sentinel, move-to-front, unknown alphabet, word reset or extra operation. Primary row is unknown. Distinct valid plaintext rotations cannot be identified from this column alone, and a format pass would not constitute a puzzle solution.

A prior proposed word-local BWT inequality was rejected as redundant with S16 reversed-order constraints; this whole-page LF/retransform experiment has different scope. The narrow grep did not find an executed equivalent, but is not a universal historical novelty claim.

## Frozen controls and comparisons

All617 possible binary strings of lengths1–7 and ternary strings of lengths1–5 were checked against exhaustive forward-transform image sets, including periodic inputs. Multiple LF cycles are not automatically rejected. Four complete held solved sources (welcome515runes,jpg107-167319,p5685,p5795) were transformed forward, then recovered up to cyclic rotation with their raw source/character maps retained.

Each control and each actual page receives19 independent uniform inventory permutations. These preserve only symbol counts, not equality masks or boundaries. They are descriptive format controls, not an encryption-law null. All140 inputs receive the same full primary-row treatment, with32,500 primary rows overall.

| Input | Main compatible | Distinct candidate necklaces | Compatible inventory permutations |
|---|---|---:|---:|
|welcome|yes|1|0/19|
|jpg107-167|yes|1|0/19|
|p56|yes|1|0/19|
|p57|yes|1|0/19|
|original0|no|250|0/19|
|original17|no|269|0/19|
|original55|no|74|1/19|

The one compatible short-page permutation is retained completely and is not interpreted as plaintext. Its existence illustrates that mere format acceptance cannot establish a message. No readability selection or alternate alphabet/route/compression stack followed the misses.

## Exact accounting and verification

Production constructs LF from occurrence ranks, follows it n steps from every primary row, reverses the collected symbols, and groups complete candidates by cyclic equivalence only to avoid redundant forward transforms. Every candidate array, primary-row group alias, LF permutation, complete group representative, complete forward column and validity flag is saved in compressed arrays. Grouping discards no possible primary row. Complete input bytes/rune IDs and source maps are retained.

`p31_check.py` imports no production algorithm: it reconstructs the full inverse rotation table by n rounds of prepend-and-sort and compares the entire candidate multiset. It separately sorts rotation indexes for every forward check, replays all133 inventory permutations, verifies all raw control source maps, and checks the exhaustive tiny image-set cardinalities. All140inputs/32,500primary candidates pass. Unlike a single-cycle shortcut this verifies periodic inputs and exact retransform equality.

Pilot20fits took1.70seconds; the remaining60controls0.60seconds and60actual/comparison fits0.79seconds. The deliberately scalar/index-sorted independent matrix checker took136.07seconds. All logged jobs exited0 without timeout. No scientific or checker failure occurred. No reserves/images/50/Git/install/new key search were used.

Coverage is three complete pages, one fixed rune order, cyclic no-sentinel last-column BWT and all primary rows. Sentinel-bearing formats, other alphabets, preprocessing/postprocessing, separate blocks or damaged inputs are outside the result. Fresh independent review65 passed: `../../review-65/REPORT.md` verifies all140inputs/32,500primaryrows/29,591necklaces using independently implemented Psi forward inversion with explicit row-index correspondence and integer-packed forward rotation sorting, plus all617tiny cases,133null RNG streams and source maps. No defects or reviewer failures. No expansion follows this miss.
