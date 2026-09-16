# P10 — exact JPEG post-MCU entropy-tail test

Originals 0 and 1 contain **zero whole bytes after the final required image data and before EOI**. Their remaining partial-byte bits are all normal one-padding. Neither has marker fill bytes nor bytes after EOI. The independent review15 parser agrees on the exact endpoints and decoded block counts. No payload was found in this particular location.

| File | Bytes | MCUs | Blocks | Entropy bits used | Final pad bits | Stuffed zeros | EOI offset | Tail bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| p0.jpg | 695,525 | 33,750 | 202,500 | 5,512,473 | 7, all ones | 3,416 | 695,523 | 0 |
| p1.jpg | 667,228 | 33,750 | 202,500 | 5,289,860 | 4, all ones | 3,012 | 667,226 | 0 |

Both images are 2400×3600, baseline Huffman, one interleaved scan, sampling 2×2/1×1/1×1, with no restart interval. Decoded AC Huffman symbol counts are 845,576 and 813,723. Every compressed coefficient array is retained, with per-component hashes, but no coefficient-LSB payload interpretation was attempted.

Input identities:

- `liber-primus/data/relikd/p0.jpg`: SHA256 `197e1e153958b9a2736b09c10eea7d8bb00e0632fd22a8d9606840becc79942e`.
- `liber-primus/data/relikd/p1.jpg`: SHA256 `f804fae06a68315eb6206158a2b34f55fe157c7d663fa961639fbe8dfc52a39f`.

Original bytes were never edited. Only these two discovery images were read for the actual test; no reserved page or new visual interpretation was involved.

## Scope and source-backed parser

The initial requested JSteg extraction is **NOT RUN**: a targeted repository/cache/tmp lookup found no exact JSteg implementation or header convention. Available cached libjpeg-turbo documentation describes coefficient access, not that payload format. We did not invent a coefficient order or call arbitrary LSB extraction JSteg.

The substitute channel is extra entropy bytes after the required final MCU, distinct from already-tested bytes *after* EOI. The inherited `stego_scan.py` stops its marker walk at SOS and explicitly names DCT extraction as an untested gap. Other inspected scripts scan decoded spatial LSBs or invoke steghide. Archive byte identity is provenance evidence, not an absence proof.

The parser follows baseline coefficient/Huffman and MCU rules, separates FF00 stuffing from markers, and checks final one-padding. It is restricted to 8-bit SOF0, one complete scan in SOF component order, grayscale or three components, and no nonzero restart interval. It decodes padded edge blocks but excludes entirely dummy blocks from stored coefficient arrays. Progressive, arithmetic, multiscan and restart inputs are unsupported, not negative findings. The primary reference is [ITU-T T.81](https://www.w3.org/Graphics/JPEG/itu-t81.pdf), Annexes A.2, C, E and F.2.2, with padding/stuffing in B.1.1.5/F.1.2.3. Cached libjpeg documentation independently specifies normal-order coefficient arrays and omission of dummy edge blocks.

A strict table check was tightened before actual execution after review15 noted that a full Huffman code space admits an impermissible all-ones code. The new malformed-table control verifies rejection. No actual outcome or source byte was changed to satisfy a test.

## Controlled validity

Sixteen independently generated clean/injected fixture pairs cover grayscale and RGB, sizes 128×96 and 123×91, RGB sampling 4:4:4/4:2:2/4:2:0, and qualities 75/92. The deterministic pixel seed is 330110. Clean entropy tails are empty. Positive fixtures insert one fixed complete binary frame before EOI: `LP10TAIL`, big-endian 32-bit length, payload, big-endian CRC32. FF bytes are stuffed. The payload contains every byte value plus a fixed sentence; the entire extracted frame, payload and CRC must match, not a printable snippet.

All 16 pairs pass exact extraction, CRC, coefficient identity and decoded pixel identity. Their original entropy streams include 266 stuffed zeros in total. Bad CRC, inconsistent length, truncated entropy and an all-ones Huffman table are rejected. Progressive encoder output is unsupported; separately constructed restart and partial-scan headers exercise explicit unsupported-mode gates rather than claiming valid full restart/multiscan decoder coverage. A deliberately altered pad bit is flagged while decoded pixels remain identical.

The local 123×91 controls test partial edge samples but round to component grids without entirely dummy blocks. Independent review15 adds 17×19 grayscale/4:4:4/4:2:0 controls: its 4:2:0 case has 24 coded blocks, 17 stored real blocks and seven dummy blocks, covering that branch. Its separate tree-based entropy parser agrees with ours on actual endpoints and its own fixtures; it also replays all 16 local fixture pairs and malformed/unsupported cases. Review artifacts are under `exploration/persistent-01/review-15`.

## Bound and retained evidence

There is no byte capacity at the measured post-MCU location in either actual file. That observation excludes a direct payload in **that location on these two bytestrings**, irrespective of our synthetic frame convention. It does not exclude payloads carried by coefficients, quantization, other metadata, other files, JSteg, F5 or OutGuess. The synthetic frame is only an instrument test and has no asserted Cicada provenance.

`CARD.md`, `p10.py`, `p10_run.py`, all clean/injected fixtures, complete extracted frames, malformed probes, `controls.json`, actual metadata, coefficient archives and zero-length tail artifacts are retained. Standard logger records source/code hashes and exit codes: strict controls exit 0 in .553 s; actual two-file parse exit 0 in 1.976 s. Initial pre-refinement controls also remain logged. No installs, native-library execution, broad stego sweep, Git changes or active processes. Next work would require a separately sourced, exact channel implementation; this result does not authorize guessing JSteg conventions.
