# P12 — unchanged JSteg v4 over remaining authorized discovery images

All 43 frozen inputs completed. Every exact v4 header declares **2,147,483,647 bytes with width 31**, exceeding its available capacity, which ranges from **49,167 to 104,090 bytes**. No complete payload exists under this extraction convention on these inputs. There were no missing images, hash mismatches, unsupported profiles or parsing errors.

This is additional input coverage of the P11/review16 implementation, not a new algorithm, key search or steganography format. Combined with P11, the exact convention has now been measured on the 45 F06 discovery images in this authorized scope. Original 50 and all ten reserved originals remain unexamined; originals 0/1 were not rerun here. No claim extends to other payload conventions or other images.

## Frozen inputs

The input set was derived from F06 mapped originals and the current configuration, subtracting 0/1, 50 and every reserve before opening an image path:

`2,3,5,6,7,8,10,11,12,13,15,16,17,18,20,21,22,23,25,26,27,28,30,31,32,33,35,36,37,38,40,41,42,43,45,46,47,48,49,51,52,53,55`.

All 43 cached paths and full image SHA256 values matched the pinned page map. `inventory.json` was frozen before extraction and retains the complete mapping, headers and profile decisions. The profiles are 25 RGB 4:2:0 and 18 grayscale JPEGs; all are 2400×3600, baseline 8-bit, single complete scan, no restart interval and no entirely dummy edge blocks. Header inventory alone was not counted as a completed extraction; the full strict parser subsequently succeeded on every image.

## Identical method and controls

The P11 source-defined order, eligibility, header and portability adaptation are unchanged: reconstructed quantized DC followed by zigzag AC, MCU/component/block order, excluding only 0 and positive 1, retaining negative 1. The five-bit width and declared byte length start at the first eligible coefficient. There is no password, offset selection, header substitution, reverse order or second extraction variant.

P10 already tested the JPEG parser on grayscale and subsampled color controls. P11 provided the source-derived bit source/sink controls and a full grayscale JPEG round trip. Before this batch, a corresponding RGB 4:2:0 JPEG round trip inserted the unchanged 127-byte payload through the source-derived C injector and cached libjpeg coefficient writer. P10 decoding plus both Python and C readers recovered the complete identical payload and sink state. That control passed before any additional actual image extraction.

Actual coefficient arrays were created in memory and hashed by component. Their values are reproducible from the pinned original images and parser, avoiding 43 large duplicate array archives. Every eligible packed bitstream is retained with its true bit count, along with available payload bytes, exact capacity, coefficient hashes, coordinate-map hash and historical sink output/state. No output was filtered or modified according to text appearance.

The 43 images contribute 27,826,276 eligible bits. Available complete bytes after their headers total 3,478,073. The emulated historical sink flushes 3,458,048 bytes in full 1024-byte chunks and remains open on every file because the declared length is never reached. These are retained partial outputs, **not complete recovered files**. `results.csv` gives every image path/hash, bit count, declared length/capacity and output hash; individual `page-N.json` files preserve complete metadata.

## Verification and scope

A separate check reconstructs each header directly from the packed bits, validates final packing padding, and reproduces every available byte. It then feeds an equivalent signed −2/−1 coefficient stream to the source-derived C sink, exercising exactly the saved eligible bits. All 43 output hashes and complete sink states match the Python results. This validates extraction/header/buffering over every newly retained stream; independent JPEG coefficient-order validation is inherited from P10/review15 and P11/review16 rather than falsely described as a second full image decoder on all 43.

The classic header has no magic or checksum. P11's explicitly limited fair-bit calculation shows that capacity-compatible headers can occur frequently by accident; it is not a JPEG image null. Here capacity fails directly in every case, so no claimed complete content or format requires interpretation. This does not exclude altered JSteg variants, damaged/re-encoded payloads, F5, OutGuess or another carrier mechanism. Shared initial one-bits are recorded without assigning them a hidden meaning.

The exact source-vs-README discrepancies, 32-bit adaptation, one-byte shift repair, empty-file behavior and zero-header sink quirks remain documented in P11. Third-party archives, extracted C and the linked harness stay local; P12 uses them without redistributing them. No new downloads, actual image changes, reserved inputs, new formats or Git changes occurred.

## Reproduction artifacts

`CARD.md`, `inventory.json`, `control.json`, `summary.json`, `results.csv`, `check.json`, all `page-N` packed streams/available bytes/historical outputs, code and manifests retain the complete table. Reproduce with the frozen P11 source-derived harness, then `p12.py control`, `p12.py run`, and `p12_check.py` under the standard logger. The named batch verifies every image hash before decoding.

The 43-image run exited 0 in 86.07 seconds on one CPU, below its 900-second cap and 2–4 minute forecast. The independent header/C-sink replay exited 0 in .656 seconds. Inventory and color control also exited 0. All intended work in this batch is complete; no active process remains. Further work needs a separately justified channel or prediction, not more variants of this now-measured convention.
