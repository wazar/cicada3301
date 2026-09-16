# P11 — exact source-derived JSteg v4 extraction

Neither original 0 nor original 1 contains a complete payload under the frozen JSteg v4 extraction convention. Both begin with 36 eligible one-bits: width 31 followed by declared byte length 2,147,483,647. The available capacities are only 89,296 and 85,898 bytes. This is a direct length/capacity contradiction, not a judgment about whether an extracted snippet resembles text.

| Original | Eligible bits | Header width | Declared bytes | Available complete bytes | Historical sink bytes flushed |
|---|---:|---:|---:|---:|---:|
| 0 | 714,405 | 31 | 2,147,483,647 | 89,296 | 89,088 |
| 1 | 687,226 | 31 | 2,147,483,647 | 85,898 | 84,992 |

The source-derived C sink remains open because it never receives the declared length. It flushes complete 1024-byte buffer chunks; 208/906 complete bytes and 1/6 bits remain pending. The Python state-machine implementation exactly matches these states and emitted bytes. Every available complete byte, all raw eligible bits, the full decoded coefficient stream and source-position maps are retained. None is called a recovered complete file.

Independent review16 reconstructed coefficients directly from JPEG entropy coding and also traversed the saved P10 arrays with a different vectorized route. Both match every eligible bit and the following packed-stream SHA256 values:

- Original 0: `bbc4ca689518c291257d786562a7ec27b03ed0e7785341e713e872dbc7f6ddb6`.
- Original 1: `8f7c2d3d11968de7145d1b5a752654bebf53579258972181ea121dc8e3ca04ed`.

Packed bitstreams use MSB-first bits and zero-pad their last partial output byte; exact bit counts accompany them. Input image hashes remain those recorded in P10 and `actual-summary.json`; originals were never modified.

## Exact source and port

The coordinator obtained the original 1993 `jpeg-jsteg-v4.diff.gz` from [GWDG](https://ftp.gwdg.de/pub/misc/crypt/steganography/jpeg-jsteg-v4.diff.gz) and [ARNES](https://ftp.arnes.si/pub/packages/crypto-tools/ftp.funet.fi-crypto/steganography/jpeg-jsteg-v4.diff.gz). Both compressed files hash `ef9a498c985f38daba1ad8c3632816c7ea73d11a3fdd83b52bf170d0fc65ee15`; unpacked patch hash `c1f02db0e00b4a9861d1d8830b48112f1d569cb00392740fc72c4e8b35bbfb8b`. The full patch and README were inspected. These exact source inputs unblock the JSteg test previously marked NOT RUN in P10; the older record stays unchanged.

The decoder hooks operate on reconstructed quantized DC, then nonzero AC values in zigzag entropy order, before dequantization. The predicate excludes exactly 0 and positive 1. Negative 1 participates. Traversal is MCU raster order, scan component order, component block row/column order. P10 proved these actual files have no dummy edge blocks, so the stored real coefficient arrays suffice. Our adapter explicitly refuses arrays with omitted dummy blocks rather than inventing their values.

The header is five MSB-first width bits, that many MSB-first byte-length bits, then MSB-first payload bytes. It has no magic, checksum or authentication. The README describes occasionally adding a leading zero, but the actual source contains no such randomization; intended 32-bit arithmetic yields minimal width for lengths at least two. The sink accepts positive lengths with nonminimal widths, which is kept separate from exact injector conformance.

The original width function has portability defects: a one-byte input reaches a shift by 32, undefined in C; a native LP64 build invalidates its fixed `33-shift` formula. The local source-derived harness explicitly uses uint32_t and defines masks shifted by 32 as zero, obtaining the intended one-bit width for length one. This is a documented repair, **not an unmodified historical binary**. The ancillary `perror(errno)` call is corrected to a string. Empty source files hit EOF before emitting a header. A zero-length sink header does not successfully close: it returns −2 during the first seven partial payload bits, then continues consuming and can flush full buffers. Controls retain that behavior.

## Controls and accidental acceptance

Eleven source-derived C injection controls use lengths 0, 1, 2, 3, 127, 128, 255, 256, 1023, 1024 and 1025. The carrier repeats signed values −8 through +8, testing exclusion of 0/+1 and inclusion of −1. Independently authored Python code predicts every modified coefficient. Nonempty cases recover every payload byte, including buffer-boundary cases. Empty input correctly makes no coefficient change.

Six explicit reader probes cover width zero, positive-width zero length, truncated width/length/payload and a nonminimal positive header. C sink state, buffering, output and Python simulation agree. A synthetic baseline grayscale JPEG carries a 127-byte payload through a documented libjpeg coefficient transcode, checked P10 entropy decoding and source-derived sink; complete output matches exactly. This validates the adapted bit source/sink and actual JPEG coefficient traversal, not a full build of the original 1993 JPEG framework. Review16 adds independently constructed signed-coefficient and sink-buffer fixtures.

Capacity-valid headers alone are weak evidence. Under explicitly independent fair bits, with only these observed capacities retained, the exact probabilities of a positive length fitting are approximately .511329 and .509710; requiring minimal width as well gives .255665 and .254855. In 999 seeded header draws per capacity, counts are 517/532 and 243/265 respectively. This calculation is **not a JPEG-image null**, and the actual leading one-bits are not treated as random. No complete actual payload exists here, so no format or content validation claim follows. Had one existed, complete bytes would remain even without recognizable structure.

## Evidence, limits and publication

The bound covers the source-defined v4 decoder, its initial header position and exact coefficient order on originals 0/1. It does not cover altered skip predicates, hidden offsets, passwords, other JSteg variants, F5, OutGuess, re-encoded damaged payloads or other images. No such variants were tried after the capacity failures.

`CARD.md`, `p11.py`, `p11_prepare.py`, `p11_build.py`, independently authored `harness.c`, controls, raw bit/position arrays, available payload bytes, C sink outputs, subprocess status and build metadata make the result reproducible. Third-party archives, full diff, extracted original/adapted C files and the linked harness executable remain **local only**, excluded from `PUBLIC-MANIFEST.json`. No redistribution grant was present in the retrieved patch. Public retrieval/build notes identify those required sources by URL/hash instead of reproducing them.

Build and controls exit 0. The first actual run was interrupted after 65.98 s because an NpzFile lookup decompressed an entire array per block. The retry caches each hash-verified array once; extraction conventions are unchanged. It exits 0 in 4.99 s. That interrupted log remains, as do all complete outputs. No installs, new actual images, reserved pages, Git changes or active processes. A subsequent image-channel experiment needs its own exact implementation and prediction; this finite result is not an all-steganography verdict.
