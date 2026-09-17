# P29 — ordered digraph-codebook membership, finite Blake source

None of the18,323 complete source windows is compatible with original0 under the frozen arbitrary bijection of rune digraphs. Every source window has an exact first-conflict certificate. The maximum consistent prefix is34 of131 pairs; its full-search block-permutation upper tail is.935. Four planted codebooks each recover their unique true source window and complete pair action. This is a finite source-and-format result, not an exclusion of digraph ciphers or a claim about other plaintext.

## Hypothesis and provenance

Pairs of consecutive runes are treated as841 atomic symbols, related to plaintext pairs by one unknown bijective codebook. Ciphertext phase is fixed at0; complete original0 supplies262 runes/131 pairs. No word-boundary correspondence is assumed. Original F06 boundaries and source-character coordinates are retained but are not scored. No additive key, language model, cipher-alphabet search, reversal, shifted ciphertext phase, padding or truncated page is used.

Only P17's pinned Blake Marriage of Heaven and Hell text, Gutenberg45315, is tested as plaintext. P17 established a specific2012 artifact-image connection to that work, not a signed claim about these exact edition bytes or2014 plaintext. Its canonical greedy conversion, body bounds, apostrophe/case/punctuation treatment and18,584-rune flattening are unchanged. All18,323 contiguous262-rune windows are admitted, including starts within words. This differs from P17 word-length signatures and P18's role for the same text as a running key. It does not provide independent corpus evidence.

Every word, raw character position and rune map is preserved in source-maps.json.gz, using the previously independently reconstructed review25 character map. Raw text SHA256 is `fc9a76619fcb76c58273d7fc9e034108b0d7fffed3780ad5b8226954a12b289a`. No new source edition or spelling correction was selected.

## Exact test and certificates

A finite source window admits an injective pair map exactly when the ordered equality partitions of its pairs and ciphertext pairs agree. Repeated source pairs must retain the same output, and different source pairs cannot share an output. Any compatible partial map can be extended to a full841-symbol permutation; unused assignments remain unidentifiable.

Production checks both directions with dictionaries. For every window, its NPZ row stores consistent-prefix length, conflict reason and earlier conflicting pair index; the row number is source rune start. Those indices plus source-maps.json.gz reconstruct the two source pairs and exact character positions, and the corresponding cipher pairs and coordinates. A complete witness would retain the full plaintext window, partial map and a deterministic completion of unused entries. No actual witness exists.

Actual contradictions split into13,894 repeated-source/inconsistent-output cases and4,429 repeated-output/different-source cases. Four windows attain the34-pair maximum. For example, source start2416 maps source pairs[10,21] and[20,23] to the same cipher pair[21,26] at pair positions25 and34. That violates injectivity. The source characters are[4921],[4922,4923] versus[4947],[4950]; original joined cipher positions are[64,65] and[87,88]. All four longest-prefix examples are retained. These prefixes are diagnostic constraint lengths, not proposed plaintext fragments.

## Controls and comparison

| Source rune offset | Complete compatible windows | Truth offset recovered | Observed pair assignments | Prefix tail,99 nulls |
|---|---:|---|---:|---:|
|0|1|Yes|88|.01|
|4096|1|Yes|92|.01|
|8192|1|Yes|89|.01|
|12288|1|Yes|97|.01|

Each control uses an independently seeded uniform random841-permutation codebook and the same262-rune length. Complete unknown-window search recovers all131 encoded pairs and their observed map action. The remaining744–753 unused map assignments are not recovered; deterministic completion is merely a witness. Two deliberate mapping violations per plant reject at their specified source windows. No source or codebook tuning follows actual results.

Each null independently permutes the131 complete ciphertext blocks and repeats the entire18,323-window search. It preserves exact pair multiplicities and within-pair equalities, but not cross-block stutters or word structure. It is a conditional block-order-exchangeability comparison, not a general cipher distribution. All seeds and permutations are retained and distinct across the four control ensembles and actual ensemble.

None of396 control nulls or199 actual nulls admits a complete window. Control null maximum prefixes range5–42; actual null maxima range17–59. Of199 actual nulls,186 equal or exceed34, giving(1+186)/200=.935. The primary finite result is zero complete memberships; the secondary prefix calibration quantifies sensitivity without converting a partial constraint fit into a message. Sparse841-symbol occupancy is a real limitation; measured control behavior does not prove power for other texts, codebooks or richer models.

## Independent verification and limits

An independent checker imports no production test. It constructs previous-occurrence distances for both pair streams: equal distance patterns are equivalent to ordered equality-partition isomorphism. It reproduces every first-conflict index/reason/witness for all600 panels and10,993,800 windows, all control permutations/map actions, every null permutation, source/cipher maps, complete-witness sets and tails. Both the pre-actual400-panel check and completed600-panel check pass. All600 compressed array files total9,654,874bytes; full data, complete source and maps are retained.

The pilot took0.39seconds; remaining controls9.97seconds, actual7.13seconds, full independent replay0.56seconds. All logged jobs exit0 with one numerical thread. No reserve, image50, new image, Git mutation or installation occurred.

The exact bound is one pinned source conversion, complete original0, phase0, and a fixed bijective digraph substitution without insertions/deletions or alternate word treatment. Other texts, phases, block sizes, noninjective/homophonic codes, stateful or polyalphabetic mappings remain outside the experiment. No expansion follows this miss. Fresh independent review58 is complete: `../../review-58/REPORT.md` independently reconstructs the raw source/18,584 rune maps and verifies all600 panels/10,993,800 windows using canonical first-occurrence labels, all controls/nulls/certificates and the .935 tail. Scoped PASS; no scientific outputs changed.
