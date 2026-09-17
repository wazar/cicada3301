# Review51 — S15 spatial trace scoped PASS

All four frozen image traces pass independent coefficient, coordinate, parity, payload and pixel-footprint checks. The complete1,417-byte shared default prefix on originals0/26 consists of selected Y DC coefficients339 in footprints whose every raw decoded RGB channel is at least250. This is direct observational evidence for the constant-bit white-background origin of those bytes, not a no-steganography conclusion about the rest of either image.

## Independent route

The audit imports neither S15's trace implementation nor its instrumented IJG decoder. It uses the previously reviewed P10 pure-Python baseline JPEG entropy decoder to rebuild natural-index coefficient arrays, then independently reconstructs MCU/component/block order and the exact0/+1 skip predicate. All2,149,184 usable coefficient rows, including their order, coordinates, signed values and sampling factors, match the streaming traces. The separate saved IJG random-access arrays also agree.

All942,080 selected bits match their addressed coefficient parities. Standalone MD5-domain-seeded ARC4 arithmetic reproduces every header and every complete payload byte, including the historical and planted controls. No OutGuess binary is executed, no crash reproduced, no historical-version build or retrieval performed. This is a review of existing controlled evidence.

A separately authored direct pixel-patch minimum calculation reproduces every header/shared-prefix/initial-one-run/full-body spatial summary. It also verifies all frequency/component/DC/AC totals and bounding boxes. Pixel tests use Pillow RGB without ICC color transformation, as declared. Sampling-scaled block footprints locate support regions; they do not identify individual causal pixels for an AC coefficient.

## Exact observed scope

Both actual headers have32 selected Y DC339 coefficients in white footprints. Both shared-prefix ranges have11,336 selected white Y DC339 coefficients. Luminance quantization DC entry is3; a constant255 block's unquantized DC is8×(255−128)=1016, whose nearest quantized integer is339. The odd parity is thus compatible with ordinary white-background encoding.

Original0's full initial body one-run is11,338 bits; first zero is Y block(142,77), natural frequency4, value−2. Original26's run is16,480 bits; first zero is Y block(75,84), frequency1, value286. Both first-zero footprints span RGB0–255. These facts distinguish the complete known shared prefix from longer runs that include nonwhite coefficients. The bounding rectangles merely enclose the selected supports; no claim is made that every intervening pixel is white.

Historical control is1,136 bytes; planted control is304 bytes. Both complete payloads equal the unchanged P28 files. The one-byte303/304 discrepancy in P28 prose was reported and corrected transparently; no binary control changed.

## Integrity and limits

The two instrumentation diffs only log observed coefficient/index values; they do not change iterator or codec arithmetic. The independent decoder route adds stronger value/order corroboration than S15's two routes that share IJG entropy decoding. All frozen scientific inputs remain hash-identical across the audit. One logged run completed in6.98seconds, exit0, with no audit failure or repair; complete counts/arrays/statistics are in result.json.

This is deterministic source/image reconstruction, not a p-value or unknown-message test. It does not reproduce or repair the four other-passphrase SIGBUS cases, establish compatibility with every OutGuess version, identify image authorship or generation software, prove intentional embedding absent, or authorize further image/key scope. The observational shared-prefix explanation is the bounded supported conclusion.
