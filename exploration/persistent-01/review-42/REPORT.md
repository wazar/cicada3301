# Review 42 — Q05 Latin corpus and model

Original numerical implementation passes; original source boundary is defective. The separately named Q05-latin-clean correction passes independent reconstruction. No original model, experiment, or source bytes were modified by this review.

## Independent checks

The reviewer extracted the canonical rune table as data and implemented a separate longest-match trie and ASCII-word scanner. All original training words, decoded-string character spans, rune spans, three omitted internal headings, and four held Virgil passages agree exactly. Source bytes agree with recorded retrieval hashes and metadata (HTTP 200); this is a local provenance replay, not a new network authentication. UTF-8 BOM removal and preserved CRLF determine the reported character coordinates.

Independent Counter-based unigram, bigram, and trigram counts agree in every cell. Scalar interpolation independently reproduces all 27,000 original log probabilities exactly. Maximum probability-row normalization error is 3.33e-16. Continuous history begins with two boundary symbols, and a boundary follows each word; removing a book heading does not reset context. Punctuation and digits delimit words, and body abbreviations/Roman numerals remain. Aliases V/U, K/C, Q/C, Z/S and greedy multiletter GP tokens are part of the representation, not proof of a historical Latin encoding.

The held inputs are the first 60 complete words of Virgil books I, IV, VII, and X: 303, 339, 331, and 383 runes. All 240 word maps, rune maps, and boundary positions replay and their source intervals do not overlap. They are four passages from one author, not four independent language sources. They are absent from the Caesar training source; this alone does not establish general Latin-register coverage.

## Retained source defect

The modern Gutenberg end marker at character 150971 follows an older English footer beginning at **150887**: “End of Project Gutenberg's Cæsar's Commentaries, Books I-IV, by Julius Cæsar”. The original extraction includes 16 ASCII word fragments, 59 runes and 16 boundaries, totaling 75 training tokens. The two æ characters split Cæsar into ASCII fragments. Original counts are 20,500 words, 120,913 runes and 141,413 tokens.

A targeted scan for publication metadata and common English words found matches only in this footer. The only non-ASCII alphabetic characters in the selected body are the footer's two æ characters. This scan bounds the inspection; it is not a proof that every remaining word is Latin. Source body starts at the Latin GALLIA sentence, and the three internal heading removals are verified.

The first model is preserved by input hashes and original source/code/report snapshots. Its arithmetic passes while its claim to exclude English boilerplate fails. This is a newly detected preparation defect; it must not be attributed to inherited decoder code.

## Separately retained correction

The clean extraction ends at 150887. Its 20,484 words are exactly the original prefix; counts become 120,854 runes and 141,338 tokens. Both source files and all held objects are unchanged. Independently reconstructed clean counts and all 27,000 probabilities exactly equal the separately produced Q05-latin-clean model, SHA256 `f4667652da86ab021af47cfcba098226454415a809ff3b1ecce84a1b4023e92e`.

All 27,000 probabilities change through normalization/backoff. The greatest absolute log-probability change is 18.608995414 at context Y, boundary → J: −1.791515657 becomes −20.400511071. The footer supplies 'by Julius' and both original J occurrences ('Project' and 'Julius'); clean J count is zero. Therefore the 0.053% token contamination fraction does not imply negligible decoder effects. Review42 does not adjudicate P25 search outcomes; original and corrected searches require separate labels and preserved outputs.

## Audit execution and bounds

Both logged scientific checks passed, with no reviewer failed attempts. Review inputs, source snapshots, scalar code, original result, independent clean expectation, and clean comparison are retained locally. No reserve pages, Git mutations, shared scientific edits, or parameter/search expansion occurred. This verifies source extraction and the stated probability model, not adequacy for arbitrary Latin plaintext or cipher constructions.
