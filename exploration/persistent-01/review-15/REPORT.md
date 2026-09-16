# Review15 — P10 entropy-tail accounting passes scoped review

Two separately implemented baseline Huffman readers agree exactly on the boundary after the final required MCU of discovery originals0/1. Both have **zero extra entropy bytes before EOI**, with canonical all-one final padding. This is a measured absence in this particular channel on these two files; it does not establish absence of other image channels or cover other pages.

| Quantity | Original0 | Original1 |
|---|---:|---:|
| Image dimensions |2400×3600|2400×3600|
| MCU grid |150×225|150×225|
| MCUs |33,750|33,750|
| Coded blocks / DC symbols |202,500|202,500|
| AC Huffman symbols |845,576|813,723|
| Required entropy bits |5,512,473|5,289,860|
| Final pad bits |1111111|1111|
| Stuffed FF bytes |3,416|3,012|
| EOI byte offset |695,523|667,226|
| Extra whole entropy bytes |0|0|

Each source has one baseline sequential scan, 8-bit precision, component sampling2×2/1×1/1×1, and no restart interval. The MCU count includes six blocks per MCU and all DC/AC magnitude bits, zero runs and EOB codes. Entropy FF00 stuffing is removed with an explicit raw-byte position map. Final partial-byte padding is distinguished from a whole-byte tail and from data after EOI.

The independent reader in independent.py uses explicit Huffman trees and a scalar bitstring traversal; it imports no worker-P code. Initial real counts were sent before P's real results were available. Later cross-parser checks compare exact bits, DC and AC counts, pad values, stuffing, raw endpoint and extracted tails. Same underlying files, shared model family and communicated specification mean this is implementation independence, not independent data or strong blinding.

Controls inspected and executed:

- All16 worker-P clean/planted fixture pairs independently recover the complete framed payload with CRC32 and exact pixel identity. They cover grayscale/RGB, regular and odd dimensions, 4:4:4/4:2:2/4:2:0, and qualities75/92.
- Three reviewer-created17×19 grayscale/4:4:4/4:2:0 pairs recover a different framed payload containing an FF byte, with correct stuffing and exact pixel identity. The4:2:0 case has24 coded blocks,17 retained component blocks and7 dummy blocks; P's parser reports these exact counts. This covers a branch not exercised by P's original16 fixtures.
- Independent code rejects the progressive, restart-declaration, multiscan-header, truncated and illegal all-one-Huffman-table fixtures. Noncanonical final pad bits are detected. The reviewer does not claim restart support: both implementations reject nonzero restart intervals.

Review found one strict validation gap in P's initial DHT check: an all-one code was allowed. P tightened the inequality and added a rejecting malformed-table fixture **before its real execution**. No current real table used that illegal code. Final-parser cross-checks passed after the correction. The parser also intentionally restricts SOS component ordering to the supported SOF order; it is not a universal JPEG parser. Unsupported progressive, multiple-scan and restart cases are explicit failures, never interpreted as empty tails.

Primary references: the locally installed libjpeg-turbo3.2.0 structure.txt and jpeglib.h define MCU and sampling accounting. The official [jchuff.c source](https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/main/src/jchuff.c) documents canonical Huffman construction, forbids all-one codes, and fills the partial final byte with ones in flush_bits. The [jdhuff.c source](https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/main/src/jdhuff.c) provides the baseline decoder reference. These references informed the review; actual endpoint agreement and inverse fixtures supply the executable evidence.

Evidence: independent-results.json, fixture-results.json, comparison.json, p-fixture-check.json and FINAL-CHECK.json; scripts and source hashes are preserved in standard run logs. Independent real accounting logged0.536s, own fixtures0.049s, final cross-parser comparison2.306s, independent P fixtures0.256s, and final manifest/dummy check0.092s. An earlier2.307s cross-parser run preceded the added AC-count assertion; it is not separate scientific coverage. No reserve pages/images, Git writes or worker-P edits. No active process remains.

Disposition: accept P10's narrow zero-tail measurement for originals0/1. Do not label this JSteg or confuse it with an after-EOI scan. Future use on a different JPEG profile requires supported-mode controls before any absence claim.
