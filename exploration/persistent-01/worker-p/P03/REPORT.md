# P03: consonantal English evades the finite pagewise count obstruction

Deleting exactly A,E,I,O,U from the documented GP-to-Latin expansion, retainingY, produces count-partition witnesses on all five frozen discovery pages. Thus O02's finite pagewise obstruction is representation-specific: it does not extend to this fixed consonantal register. This is necessary histogram compatibility only. No shared codebook, symbol-order fit, plaintext or cipher evidence has been established.

The transform was frozen before examining results and motivated by the inherited scorer's measured consonantal-register blindspot. No additional vowel variants or favorable real score selected it. The four source files, GP expansion, five ciphertext histograms and local research context remain shared with J03/O02. This is an actual-register change, not a new independent corpus.

## Exact scope and weights

Canonical GP Latin transliteration followed by removal of characters in AEIOU, retainingY. Every expanded letter is recorded with original source-rune index, rune identity, within-transliteration offset, keep/delete flag and retained-stream index. Every original rune has its retained and deleted character indices; completely deleted runes remain represented in the map. Only the previously long four sources were admitted:

| Frozen source | J03 expanded length | Consonantal length | Deleted letters |
|---|---:|---:|---:|
|0_koan_1|815|490|325|
|0_loss_of_divinity|808|481|327|
|0_welcome|542|324|218|
|jpg107-167|340|195|145|

The fourth source is now shorter than every target page, so it contributes zero windows. It was retained in the manifest, not replaced. Contiguous source windows have lengths exactly equal to observed rune counts. Their boundaries can occur within a multi-letter GP expansion; exact source-rune and expanded-letter spans remain attached. Contraction changes represented passage extent, available starts, source weights and alphabet support together.

All windows were evaluated, without a collision-score prefilter:

| Original page | Target symbols | Windows | Feasible | Infeasible | Unknown |
|---|---:|---:|---:|---:|---:|
|0|262|512|47|465|0|
|1|266|500|113|387|0|
|3|217|647|213|434|0|
|7|208|674|517|157|0|
|17|273|479|141|338|0|

In total2,812windows,2,478distinct sorted count cases,1,031feasible and1,781infeasible. O02 had no feasible Latin-source windows on pages0,3,17; all now have witnesses. Results.json records every source's window weight and feasible count. The descriptive product for independently uniform window draws is82464220971/53473628672000=0.0015421475. This imposed weighting is not a probability of a cipher, and overlapping source windows are not independent natural-language observations. No threshold on this fraction was used as a discovery claim.

## Meaning of the witnesses

For each feasible page/window, all29positive ciphertext-rune counts partition into disjoint groups. Each group's sum exactly equals the count of its assigned consonant. Feasible source-letter-to-original-rune mappings are retained for every window; each page/window receives its own optimistic assignment. This does not require the same letter/rune mapping between pages or constrain homophone scheduling.

A deterministic convenience tuple, lexicographically first by source name/start, is saved in check.json: page0koan start137;page1koan109;page3koan115;page7koan1;page17koan64, all zero-based consonant positions. This is a set of pagewise witnesses, not a promoted plaintext tuple. Testing a single convenience tuple could not reject other tuples. No delimiter sideprediction was added because the count-only model provides no justified delimiter rule.

## Executed validation

The inspected O02 solver's definitions were extracted with AST, without importing its top-level execution or writing old outputs. Exact total/support/minimum/subset-sum/cumulative-small-bin tests precede a complete multiset partition recursion. Per-case limits2seconds/200,000nodes and global240seconds would yield UNKNOWN; none was reached. Rejections preserve necessary witnesses or full rejected-branch DAGs. There are507retained proof-DAG nodes across real cases, including failed branches visited before feasible partitions.

Controls include all29canonical rune transforms (including full deletion of vowel-only expansions and retention ofY), full source reconstruction from retained plus removed maps,200tiny exhaustive labeled-assignment comparisons, five actual-histogram attainable partitions, and five same-total impossible cases. All pass.

A separate checker reuses O02's non-solver certificate-checking definitions, verifies all2,812source window count vectors and source spans, reconstructs all feasible rune assignments, checks exact window-family coverage, and validates all210partition control certificates. It independently filters all2,505expanded source letters and validates every kept/deleted map. This is separate arithmetic checking within the same worker using an already inspected checker; it is not a fresh external review or independent transcription.

Primary logged run20260916T215537.189973Z-p03-consonantal-counts: exit0,0.650744s. Checker20260916T215641.733328Z-p03-certificates-maps: exit0,0.141756s. Raw code snapshots, commands, hashes, exit codes and stdout/stderr remain under worker-p/runs. P03/evidence.json.gz contains all maps, source vectors, window provenance, certificates and controls; P03/check.json and results.json are summaries. No process remains, no reserve/new image/Git mutation occurred.

## Next discriminating steps

1. Fresh review can reconstruct the consonantal streams directly from the four original solved rune files and independently check the feasible letter/rune certificates, avoiding a shared J03 expansion input error.
2. If the register is retained, require a common assignment across all five page histograms. A useful finite bound intersects per-rune five-dimensional count vectors with candidate source-window count vectors, retaining all source choices or explicitly bounding tuple coverage. Pagewise witnesses alone do not imply that any shared assignment exists. Do not test more arbitrary vowel deletions or random homophone books.

The count obstruction has been escaped only in this finite, clearly specified representation. The next unresolved premise is a shared assignment and order compatibility, not a reason to release reserved pages.
