# P13 — complete Huffman tables from exact symbol histograms

All **eight complete Huffman tables** in originals 0 and 1 match the frozen deterministic optimizer byte-for-byte. The comparison includes every code-length count and every symbol's position, not merely the broad classification “custom/optimized.” No unexplained table choice remains relative to this optimizer on these two files.

| Original | Table (class:id) | Observed symbols | Exact match | Tied-selection steps | Length-adjustment steps |
|---|---|---:|---|---:|---:|
| 0 | DC:0 | 135,000 | yes | 0 | 0 |
| 0 | DC:1 | 67,500 | yes | 0 | 0 |
| 0 | AC:0 | 766,150 | yes | 21 | 16 |
| 0 | AC:1 | 79,426 | yes | 24 | 0 |
| 1 | DC:0 | 135,000 | yes | 0 | 0 |
| 1 | DC:1 | 67,500 | yes | 0 | 0 |
| 1 | AC:0 | 746,223 | yes | 32 | 24 |
| 1 | AC:1 | 67,500 | yes | 0 | 0 |

A tied-selection step means at least one of the two selected merge frequencies has another equal-frequency active tree. It is an algorithm diagnostic, not a count of independent hidden bits. The adjustment count records repeated tree-length redistribution operations. Actual equality includes the resulting choices in both cases.

## Distinct question and exact reference

Round18/L1's `jpeg_fingerprint.py` compares a table with fixed standard tables and otherwise labels it custom/optimized. Its report expressly avoids claiming content-dependent Huffman table identity. P13 instead supplies the optimizer with the **exact symbol histogram from the actual compressed stream**. The original rendering document is unnecessary for this narrower comparison because those symbols can be decoded from the JPEG itself. No older report was edited.

The frozen reference is `jpeg_gen_optimal_table` in [libjpeg-turbo 3.1.4.1](https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/3.1.4.1/src/jchuff.c), matching the installed static library. Source SHA256: `4c4ddf29e4a03ba86835212cd2cb6ad47ef9c079dfb435b0d7bd2f03abe4d67f`; library SHA256: `dfee3c454a04cdc8f8ca2619146a1b53187e9ec2b2755ef15e3639105231b63f`. The algorithm inserts pseudo-symbol 256 at count one, prefers the larger symbol when frequencies tie, limits code lengths to 16, then removes the pseudo-symbol. An independently authored Python implementation matches the native routine, including full symbol ordering. No alternative version or tie rule was selected after examining actual results.

This exact match establishes compatibility with a deterministic frequency-based process. It does **not** identify the historical library version, prove the unique best coding, or establish that all image channels are empty. Other implementations could make other choices. A mismatch alone would have required resolving that freedom before any payload interpretation; here no mismatch needs such an explanation.

## Actual histograms and controls

The checked P10 entropy parser was instrumented to record each decoded DC category and AC run/size symbol, including EOB and ZRL, by its actual table selector. This avoids silently substituting a different re-encoding of the coefficients. The actual original bytes were only read. Coefficient hashes match the previous P10 results, and every histogram, table and optimizer trace is retained.

A separate implementation reorders the saved component coefficient arrays into MCU order, recomputes DC differences and AC runs, and counts the symbols. It independently reproduces all eight observed histograms. Thus canonical coefficient reconstruction and actual entropy-token counting agree for these inputs.

Four histogram controls cover a single symbol, equal counts, a highly skewed distribution and an overlength tree. Python and native output agree exactly. The overlength fixture uses the first 34 Fibonacci counts and exercises the 16-bit limiting rule.

Two actual JPEG controls cover grayscale and RGB 4:2:0. A coefficient transcode with native optimization produces tables predicted exactly by the measured histograms. A second transcode swaps a fixed pair of equal-length symbol positions in the first eligible table and re-encodes the entropy data. Grayscale swaps symbols 3/4 at code length 2; RGB swaps 2/3 at length 2. In both cases:

- Decoded pixels and quantized coefficients remain identical.
- Complete symbol histograms and weighted Huffman bit cost remain identical.
- Table count bytes remain identical, but the full symbol-order comparison detects exactly one changed table.

This is a controlled demonstration that the proposed table-choice channel could carry a distinguishable choice without changing the image. It is not an asserted payload format, and no such deviation was found in the actual two-file test. Byte stuffing and total file size need not remain identical under the control permutation.

## Preserved failures and limits

Before actual comparison, the first Fibonacci control reached only length 16 rather than exceeding it; its branch-coverage assertion failed. The corrected 34-count fixture was frozen before actual work. A second control run exposed a variable-name collision between histogram accumulation and existing DHT count parsing. Renaming the accumulator fixed that instrumentation error. Both failures remain logged; neither changed the optimizer or actual input selection.

Only originals 0/1 were tested here. The 43-image P12 coverage concerns a different JSteg channel and is not silently included in this result. No reserved image, page 50, other optimizer, table-permutation search or guessed payload decoding was examined. No installs, image modifications or Git changes occurred.

## Evidence

`CARD.md`, `source-identity.json`, independently authored `helper.c`, build metadata, `p13.py`, `p13_check.py`, all control JPEGs, complete native/Python tables, exact histograms, merge/length-limit traces, `summary.json` and `check.json` retain the measurement. The helper calls the installed optimizer; no third-party source text was copied into the report or implementation.

The corrected controls exit 0 in .202 s; actual two-file comparison exits 0 in 2.527 s; separate coefficient-histogram replay exits 0 in 1.425 s. All eight actual tables and both permutation controls are accounted for. No process remains active. A next experiment must supply a distinct prediction or explicitly justified input coverage; these results do not support inventing a message from ordinary tie choices.
