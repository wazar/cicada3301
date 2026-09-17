# Review48 — historical carrier and OutGuess mechanism support

## Concrete compatibility control

The existing corpus documents the2016 carrier4gq25.jpg, a no-key `outguess -r` command and expected seed230/length1136. Its image was absent from this checkout. Under the coordinator's permission to retrieve a missing documented public artifact, fetched exactly the URL pinned in corpus/A-primary-artifacts/MANIFEST.json:
https://raw.githubusercontent.com/cijhho123/cicada3301/main/2016/2016/additional%20images/4gq25.jpg

The retrieved carrier at review-48/4gq25.jpg is26,342bytes, SHA256 `a8340ad04b83fb3130e7ed9172867a440812e87089d6aa2b932d97c6ae38aebe`, exactly matching the earlier manifest. Expected payload is1,136bytes, SHA256 `fe89e77519dfaca998a257ed39c2861303029de2a49183db00eea0fda3a28010`. Existing micheloosterhof_cicada-2016/stage01/4gq25.jpg.outguess and armada_osint/extracts/T5-4gq25-2016.outguess.txt are byte-identical; both are copied here. Carrier, expected output and provenance were sent to P before their compatibility extraction.

This is a pinned community mirror of a historical public artifact, not an original publisher network retrieval. The historical README records a good Cicada-key PGP signature and fingerprint, but this support task did not freshly verify that signature. Matching an extracted output will qualify the installed0.4 tool on this carrier/command; it will not establish universal agreement with historical0.2, especially on negative extractions. The Fandom rendition was deliberately not used: its own manifest reports different bytes/hash and failed wiki-declared-hash agreement. No new reserve image was retrieved/read.

## Narrow source findings

Inspected the pinned upstream0.4 source selected and built by P; no duplicate build or extractor modification. In src/jpg.c, `steg_use_bit(unsigned short temp)` excludes exactly0 and+1 via `(temp & 1)==temp`. Negative−1 converts to65535 and is retained. The decoder's jdcoefct.c loop calls it for all64 coefficients, including DC. Consequently ordinary zero AC coefficients disappear from the usable-bit stream, while a blank block's nonzero DC may remain. A pixel-margin argument needs a usable-coefficient path trace or controlled image experiment; common dimensions alone do not establish it.

`finish_state` sets capacity to ceil(usable_bits/8). `steg_retrieve` separately decodes a four-byte header: two little-endian seed bytes and two little-endian length bytes. The decoded length is compared with capacity, not calculated from image dimensions. The iterator starts key-seeded at skipmod32, is reseeded with the header seed and then adapts skips to usable-bit count and remaining length. Thus shared-key initial behavior does not guarantee identical body paths across images with different usable-bit counts.

## Measured scalar prediction

A separately logged Python implementation of the inspected MD5/ARC4 initialization yields default encryption stream prefix `3f5ed71c`. Four raw all-one header bytes `ffffffff` decrypt to `c0a128e3`, giving **seed41408,length58152**. Four all-zero bytes decrypt to seed24127,length7383. The reported historical58152 length therefore has an exact alternative explanation as default decryption of an all-one header; it is not intrinsically an image capacity. Full all-one extracted bodies would XOR against the reset default encryption stream. A4096-byte stream and its hash are retained for concrete comparisons.

This scalar result does not establish that actual LP coefficients follow that pattern, prove the historical0.2 implementation, or locate the shared prefix spatially. P's actual control/extraction work is separate. The old STEGO-VERDICT's universal image-steganography conclusion is not adopted; only the inspected operation and this finite arithmetic consequence are asserted.

## Preservation

Pinned-carrier retrieval and scalar-mechanism jobs passed with recorded commands/input hashes. Read-only lookup issues are retained in LOOKUP-NOTES.md: a nonexistent shell glob, a mistaken jpeg.c filename (actual jpg.c), and an overbroad metadata search producing truncated output. They did not run a scientific experiment or alter data. No tool build duplication, shared-file edits, Git operations, reserved-image reads or expanded key searches occurred.
