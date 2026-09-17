# P18 — one Blake text as a finite running key

No verified plaintext emerged. Every eligible finite rune offset and both additive signs were searched for originals0/17 and one exact-repeat-mask null per page. Both real maxima exceed their single comparator slightly; this is a descriptive observation, not a calibrated significance result.

| Packet | Length | Full offset/sign cells | Best score | Best source offset/sign | Consumed key runes |
|---|---:|---:|---:|---|---:|
|Original0|262|36,674|−4.307774067844759|3003 /−1|250|
|Null0|262|36,664|−4.428268376817218|14351 /−1|256|
|Original17|273|36,648|−4.361632903176001|13184 /−1|270|
|Null17|273|36,634|−4.42302069672335|1252 /−1|271|

Real-minus-null differences are0.1204943 and0.0613878. One null per page cannot estimate a reliable tail or establish significance. Complete leading transliterations were inspected; they do not produce readable full plaintext. All16 leading alternatives are retained in full, not selected English-looking fragments. No solve or general negative is claimed.

## Frozen source, operation and finite scope

P17 documented the puzzle-image connection to Blake's Marriage of Heaven and Hell. Here the same exact Gutenberg45315/Luce1906 transcription, body boundaries and H01 variant0 rune mapping play a DIFFERENT role: finite running key, rather than hypothesized plaintext with matching word lengths. The2012 signed link does not establish a2014 key role or historically intended edition. No other book, edition, text normalization or mapping was added.

Concatenating mapped words gives18,584 rune indices, byte-array SHA256 e987eed6a8b7aa6af1cf361ea0af03b0c47275b04464f1a9828a5560aa6e0785. Key word boundaries are not extra tokens. Every rune maps to its source word, within-word rune ordinal and original word-character interval. Those intervals are whole-word spans, not individual-letter spans; the exact rune ordinal resolves the position. Review25 separately reconstructs individual source character positions.

The unchanged corrected worker-c/frozen_finite.py decoder permits ciphertext0 either as literal plaintext0 with zero key consumption or as ordinary additive input consuming one key rune. Every other rune consumes one. Plain=(cipher+sign*key)mod29. This is the existing finite literal-F model, with no anti-repeat/skip2 layer. Both signs are searched at every natural rune offset with at least as many remaining key symbols as nonzero ciphertext runes. No wrapping, padding, arbitrary start-state drift, reverse or ordinary-score shortlist is used. The suffix minimum-consumption guard rejects branches that cannot complete before EOF.

All included cells are feasible by construction of that minimum-consumption offset bound; all293,384 full-grid cells completed. Larger offsets are arithmetically impossible under this model and are excluded by the exact guard, not by a language score. Output replay reaches the source's finite end without overrun. No claim covers a cyclic or infinite extension.

The same frozen English rune/boundary LM is used, with its five fixed training groups. Scores are normalized LM log scores under that instrument; no legacy English threshold or cross-model numerical comparison is imported.

## Unknown-offset controls

Four complete held groups use predeclared offsets/signs and the C15 literal-F encoder rule (plain0 at position%3!=1 remains literal; all other runes consume key). Every control searches the whole eligible source grid and both signs, not a truth-offset shortlist.

| Held source | Length | Planted offset/sign | Cells | Truth job rank | Best rune errors | Exact truth path global rank |
|---|---:|---|---:|---:|---:|---:|
|welcome|515|0 /−1|36,176|1|0|1|
|jpg107-167|319|4096 /+1|36,582|1|0|1|
|p56|85|8192 /−1|37,006|1|0|1|
|p57|95|12288 /+1|37,000|1|2|2|

All four planted offset/sign pairs are selected and unique for their leading paths. Complete text/path recovery is3/4, not perfect: p57's two errors and exact truth at rank2 remain unchanged. Its correct job's best score is−2.2678361338317727 versus true text−2.287929477802066. These are four fixed known-source constructions, not a population estimate or independent new language corpus.

One hundred small exhaustive mask/empty-key/EOF cases agree with exact top16 scores. The256-cell costpilot samples64 evenly spaced jobs per control across the complete grid, and all jobs are recorded. Full control runs took267.46s of child computation, consistent with the pilot's approximately266s forecast. No search dimension was changed after the control scores.

## Complete selection, aliases and retention

Each cell retains its exact top1 plaintext, literal positions, consumed count, score and diagnostics. To obtain global16 DISTINCT (plaintext,literal-position) alternatives, the16th distinct cell-top1 score supplies a safe threshold. Every cell whose top1 meets that bound is rerun with exacttop16. Any globally competitive path must come from such a cell; no shortlist based on a separate heuristic is used. Here16 cells per packet meet the bound,128 reruns total. Ties in which16 distinct paths to return remain deterministic but arbitrary; this is not an exhaustive list of all equal-score paths.

Before the first aggregate, review25 identified that localtop16 ties could hide equivalent source aliases. Bookkeeping was strengthened without changing any cell score/grid: derive the exact required consumed keyprefix for both signs, then scan the entire finite key for identical windows. Exhaustive aliases and originally encountered aliases are both retained. The refinement is recorded in the frozen-card addendum.

All293,384 full cell outputs occupy34,565,030 compressed bytes across eight packet files; largest6,449,278 bytes, each below90MB. Global128 distinct alternatives, full transliterations, key/source maps, per-cell diagnostics, control truths and all command snapshots are retained. Finer nonleader alternatives are deterministically reconstructible from pinned inputs/decoder. The256 pilot cells repeat full-grid work and are not additional coverage.

## Null and independent checks

The fixed seed331819+page generates one full string with exactly the actual adjacent-equality mask: first uniform29, subsequent repeats forced and nonrepeats uniform among the other28. Entire offset/sign search and globaltop16 selection are repeated for each null. This preserves repeat positions, not rune histograms or special-F positions. Real/null F counts are14/9 for page0 and12/5 for page17, so literal-branch and eligible-grid sizes differ; that is an explicit limitation of this matched comparator. No empirical p-value is reported.

Own arithmetic replay verifies every one of293,384 saved top1 outputs, finite consumption and selected-path sourcealiases. A separate sampler implementation regenerates both complete null strings and verifies their equality masks. Full-source coordinate maps and all input hashes remain pinned. Review25 independently passed the four complete control grids, source reconstruction, finite guards, global cutoff and alias classes before the actual searches; final review25 also passed all293,384 cell IDs/accounting,460 sampled/selected scalar paths plus256 pilot paths, every global cutoff/alias map and both null RNG streams. See exploration/persistent-01/review-25/REPORT.md.

Main full searches took442.263s child time in eight logged batches, all exit0, one numeric thread. Aggregation, exhaustive controls and verification are separately logged; no batch exceeded900s. No reserved page, new image, other edition or additional actual page was introduced.

This is finite coverage of one source/mapping, additive signs, literal-F transition model and English rune/boundary scorer. It does not exclude other Blake editions, segmentation, key roles, clocks, ciphers or plaintext registers. The small real/null score differences and imperfect control do not warrant either a solution claim or a family-wide exclusion. The frozen task ends without expanding after the result.
