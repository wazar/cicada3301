# P17 — documented Blake source, fixed edition length signatures

No source passage was admitted. One frozen edition of William Blake's The Marriage of Heaven and Hell supplies4,580 words under one H01-compatible rune conversion. Against all45 F06 discovery pages and all contiguous source/page offsets, the maximum exact signature is8 units. The full-procedure999-permutation tail is0.809; admission required at least12 units and tail<=.01.

The two maximal coincidences are fully retained:

| Original page | Starting explicit unit | Starting source word | Length | Decoded-text character interval |
|---|---:|---:|---:|---|
|5|51|1080|8|[7539,7576)|
|46|6|3791|8|[23045,23079)|

These are word-length coincidences, not rune plaintext matches. Their complete unedited spans, original CRLF, source words, rune mappings, F06 rune intervals and all offsets are in actual.json.gz/source.json.gz. Neither clears the frozen rule; no cipher fitting followed.

## Why this particular book

The source/provenance check was bounded to10minutes. The cached2012-01-second-chance signed message explicitly links hkdgl.png and lists22 book-code coordinates. Fresh GPG verification succeeds against fingerprint6D854CD7933322A601C3286D181F01E57A35090F; complete status/exit output is retained. The message itself does not name Blake, and signing a URL does not cryptographically bind the later image bytes.

The image fetched from the exact historical community-mirror path has SHA256 f4be4b74b1cc1479f9482d0e670375450b43d1b500a991de644f1cc9dea00217, matching both the cached community and Wayback manifest records. I personally viewed this363×136 image and the historical gallery's373×504 plate4. The hint corresponds to the lower artwork at crop[5,360,368,496]. A fixed-size translation search on that single identified plate gives grayscale correlation0.9999999764. RGB pixels are not all identical:48.284% exact, mean absolute channel difference0.642, maximum21. This supports image correspondence, not byte identity. An initial rough hand-positioned crop at[6,353,369,489] correlated0.492; the subsequent full fixed-size translation located the registered crop. No other book/plate search was selected for favorable LP scores.

The gallery title and plate4 link identify the work; visible text is headed The Voice of the Devil and corresponds to that section in the official Gutenberg edition. [The Morgan Library's item139](https://www.themorgan.org/collection/William-Blakes-World/139) independently catalogs Marriage of Heaven and Hell plate4. This is an actual puzzle-image/book relation, not inferred philosophical resemblance. It does not establish that this work supplies any unsolved Liber Primus plaintext. The old22-coordinate book-code answer was not independently reconstructed here, and is not needed or credited as a result.

Provenance URLs:
- Signed message mirror: https://raw.githubusercontent.com/jaxonkuipers/cicada3301/main/corpus/communications/2012-01-second-chance.asc
- Hint image: https://raw.githubusercontent.com/cijhho123/cicada3301/main/2012/additional%20media/images/MIDI%20and%20seconde%20chance/hkdgl.png
- Historical gallery: http://www.gailgastfield.com/mhh/mhh.html and http://www.gailgastfield.com/mhh/mhh4.jpg
- Official edition: https://www.gutenberg.org/ebooks/45315 and https://www.gutenberg.org/cache/epub/45315/pg45315.txt

The gallery's HTTPS retrieval failed TLS/502; HTTP succeeded. Library of Congress and Morgan direct page fetches returned403, while indexed Morgan collection metadata was available; no image from those failed fetches was used. The historical gallery is a reproduction source, not claimed an institutional custodian. The primary Blake page itself and its matching text provide the identification.

## Frozen source and representation

Project Gutenberg45315 identifies Boston, JohnW.Luce and Company,1906. The downloaded complete file hash is fc9a76619fcb76c58273d7fc9e034108b0d7fffed3780ad5b8226954a12b289a. Its release is2014 and revision2024: neither these current digital bytes nor this edition's typography is asserted to be the2012 code edition. All later conclusions are conditional on this exact transcription.

Search text begins at THE ARGUMENT and ends after For everything that lives is holy., preserving all interior prose, verse and headings. Frontmatter/license remain in the immutable source file but are outside the search. Character spans refer to the retained UTF8-decoded source with original CRLF. ASCII-letter words allow internal straight/curly apostrophes, then strip those apostrophes; hyphens split. Exactly H01 variant0 applies the inspected published greedy GP digraph mapping and V/K/Z/Q aliases. No ING/IO expansion, spelling change or alternate edition was tried. Explicit ciphertext units come directly from F06; image line fragments are not substituted.

The method asks whether unchanged contiguous source words could preserve explicit delimiter-unit rune lengths. No language model, English score, additive key or plaintext fitting is used. It is a new justified source for an existing length-signature method, not a new cipher model.

## Controls and complete search calibration

Two predeclared40-word source segments at indices1000/2000 were inserted at unit5 of the first actual page with>=50 units. Affine2r+3 encoding preserves all lengths and inverts exactly. Both exact source coordinates are recovered; complete-search maxima40/41 respectively, each tail0.01 against99 full-procedure within-page order permutations. These controls preserve the actual number of units, not necessarily that page's total rune count; they demonstrate signature detection, not a new transcription or full-page cipher recovery.

The real statistic is the complete longest contiguous common length sequence, computed with a suffix automaton. All999 nulls independently permute each page's whole unit order while preserving its length multiset and unit count, then rerun the maximum over all45 pages and every source offset. Permutation indices and all maxima are retained. The null is conditional on that representation, not a guarantee for arbitrary text-generation models.

An independent checker uses substring sets and binary search instead of the suffix automaton. It reproduced all1,197 null maxima, all3 real/control maxima, both tails, every RNG permutation, both complete maximal-hit spans and the rune conversion of all4,580 words. This includes maxima shorter than the admission threshold; there is no left-censoring at six units.

Standard logger exits are all0: provenance9.855s, controls1.017s, actual4.454s, independent replay1.430s, one numeric thread. Complete source, mappings, raw evidence, controls, source hashes and command snapshots are retained. The local GPG scratch keyring is excluded from the public manifest.

The result bounds this one edition/mapping, contiguous unedited passage and preserved explicit word-boundary lengths. It does not exclude Blake quotations under changed spelling, segmentation, cipher expansion, a different edition or an unrelated source. No additional book, route or near-match search followed the miss.
