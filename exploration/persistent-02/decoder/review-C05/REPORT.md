# Independent C05 algorithm review

PASS for the specified unknown-seed sum-feedback construction excluding literal Fs from the normal history, at the reviewed k2/3 scope. No arithmetic or backtrace blocker found. This does not validate the construction as the puzzle's cipher or certify language recovery.

Reviewed engine SHA256:`1617455979d4b38277a1279751eb72c7ecabae6421905b89036464d3545fae2d`.

Before reading the implementation, I read the coordinator's construction proposal and froze72independent full seed×ciphertext-F-mask fixtures in `cases.json`/`expected-manifest.json`. The expected manifest SHA256 is`514c806360924426ba50344b7a78c86d2b25699cddf8f330a55b5d36ed8047d2`. These cover1,352,328complete seed/mask paths, exhaustive29² seeds on binary short inputs and selected29³ cases, leading/consecutive/ordinary/literal F, boundaries, empty input and fewer-than-k normal runes. Integer, zero and original P03 scalar weights are included. Full scores/plaintexts and seed grids are retained in compressed NPZs; no optimized implementation was imported by the enumerator. Scalar independent decoding checks multiple seeds per mask in addition to full vectorized seed enumeration.

After freezing, comparison with `literal_feedback.Engine` reproduced every global maximum exactly (maximum absolute discrepancy0). Every returned representative was checked against the stored full seed/mask/plain arrays and direct scalar decoding. Unused seed suffixes correctly appear as None with29^missing equivalent completions. Partial-seed outputs are not silently treated as unique complete keys.

Checkpoint reconstruction was tested at block sizes1/2/3/4/7/32; complete returned path/seed representatives stayed identical. Source inspection confirms sorted packed state IDs, maximum selection per identical history/context, normal0 advancing history, literal0 leaving history unchanged, and deterministic checkpoint recomputation. The uint32 packing bound is asserted. A max_states=1 fixture correctly raises MemoryError rather than returning an approximate maximum.

The state budget is **not a hard RSS limit**:candidate arrays are allocated before retained-state-count rejection, and temporary sort buffers plus checkpoint/backtrace arrays also consume memory. Current measured k2/3 plant scope is reasonable; do not extrapolate the500,000-state guard to a memory guarantee or arbitrary larger k. Reported snapshot/backtrace byte counters are components, not whole-process peak.

For all32complete held/fresh plants, independent scalar decoding verifies the planted cipher/seed/literal mapping and all512returned alternatives with score discrepancy0. Local source hashes and every truth rune/end match were independently checked against the four full held sources or B's frozen fresh packet. I did not rerun all32optimized searches or re-fetch remote sources. Stored claims of29/32zero-error selected plaintexts are correct; residual fresh Guest0/k3, Shelley0/k2 and Shelley1/k3 have1/1/2errors and positive objective advantages over truth. Those are scoring/selection limits, not arithmetic failures.

The returned alternatives are correctly labeled **one best path per selected final state**, not global top16 decision paths, all tied paths, distinct plaintext enumeration or exact truth-rank coverage. The proof of sufficient state concerns ordered last-k normal plaintext runes plus two score tokens and capped history length; it does not transfer to a literal-F-inclusive history or whole-text scorer.

All commands, source snapshots, raw outputs and exit codes are logged under `runs/`. Review fixtures were frozen before implementation inspection; this review is independent of C's implementation author but not blind to the assignment or shared repository.
