# S15 — spatial origin of the default OutGuess common prefix

The complete 1,417-byte prefix shared by P28's default extractions from originals 0 and 26 comes from white-background luminance DC coefficients, each equal to **339**. This is now an observed coefficient-to-output path, extending P28/review48's earlier scalar explanation. It does not establish absence of a payload elsewhere.

## Frozen procedure and validation

`S15-CARD.md` fixes default no-key extraction, two actual images, two controls, a separate source copy, and the white-block criterion: every decoded RGB pixel in the coefficient footprint must be at least 250 in every channel. No regions or thresholds were adjusted after results.

The separate source copy changes only observational logging in `outguess.c` and `jpeg-6b-steg/jdcoefct.c`. It records every retained coefficient's component, block coordinates, natural DCT frequency, value and sampling factors, plus every header/body iterator-selected index and bit. No iterator, PRNG, filter, coefficient, key, error handling or extraction repair was changed. Exact instrumentation diffs and hashes are retained. Source provenance checks every upstream C/header file against the pinned P28 archive, verifies the original files remain byte-identical, and confirms only those two copied files differ. The independent coefficient reader links the original unmodified library and uses `jpeg_read_coefficients` with random-access component arrays, avoiding the instrumented streaming traversal.

Before actual tracing, both the historical 4gq25 carrier and P28 plant-0 reproduced the original expected payload bytes exactly. All usable coefficient coordinates and values matched the independent reader, every selected bit matched its coefficient parity, and a separate scalar MD5/ARC stream reconstruction decrypted the complete raw traces to the exact payload. The same four checks passed on both actual images. The historical control contains 25,229 usable coefficients and 1,136 payload bytes; plant-0 contains 717,016 usable coefficients and **304** payload bytes. The latter matches P28's binary exactly; its report's 303-byte wording is a separate one-byte prose discrepancy notified to P.

The independent reader shares the original JPEG entropy decoder, so this is independent coordinate traversal and extraction reconstruction, not an independent JPEG codec implementation. RGB classification uses Pillow's decoded pixels without an explicit ICC color-management transform. Exact DC values and coordinates do not depend on that white-pixel classification.

## Actual traced results

Both images have 2400 × 3600 pixels. OutGuess retains 714,405 coefficients from page 0 and 692,534 from page 26. Each default extraction has 32 header bits plus 465,216 body bits, yielding 58,152 bytes. The observed header is all ones and decrypts to seed 41,408 and length 58,152.

| Selected range | Page 0 | Page 26 |
|---|---|---|
| Header, 32 bits | All Y DC = 339, all white footprints | All Y DC = 339, all white footprints |
| Shared first 1,417 bytes, 11,336 bits | All Y DC = 339, all white footprints | All Y DC = 339, all white footprints |
| Shared-prefix footprint bounding box | [0,0,2400,624) | [0,0,2400,480) |
| Complete initial all-one body run | 11,338 bits | 16,480 bits |
| First zero, zero-based body bit | 11,338 | 16,480 |
| First zero coefficient | Y block (142,77), natural index 4, value -2 | Y block (75,84), natural index 1, value 286 |
| First zero footprint | [1136,616,1144,624) | [600,672,608,680) |

Coordinates are zero-based; bounding boxes are half-open and enclose selected footprints, not claims that every pixel throughout the rectangle is blank. Header footprints on each image lie within [120,0,2104,16). Natural DCT indices use row-major frequency ordering, with index zero being DC. All common-prefix footprints are 8 × 8 luminance blocks.

The complete initial page-0 run includes 11,337 white DC selections plus one nonwhite AC selection. Page 26's longer run includes 16,479 white DC selections and one nonwhite DC selection. The first zero in each image lies in a block spanning RGB values 0–255, classified nonwhite by the frozen criterion. Thus the constant run stops upon selected content coefficients; neither the full run nor all later extraction bits are attributed indiscriminately to blank margins. Full-body DC/AC, component, frequency and white-footprint counts are retained in the JSON results.

The mechanism is explicit: white-background Y DC = 339 has low bit one; the unchanged OutGuess predicate retains it; the unchanged iterator selects those coefficients; raw all-one bytes XOR with the restarted default encryption stream to produce its complement. Both images supply that same raw bit pattern for all 1,417 shared bytes despite their different body trajectories and usable-coefficient counts. No assertion of intentional embedding, image-generation pipeline, universal no-stego result or readability follows. This test addresses only these default extractions and the measured shared prefix.

## Preservation and replay

`S15/summary.json` and `S15/{historical,plant0,actual0,actual26}.json` preserve results, commands, exits and input/output hashes. Each `.map.bin.gz` is the full usable stream: native little-endian int32 rows with nine documented columns; row index is bitmap index. Each `.selected.bin.gz` stores bitmap index and bit, header first then body. Independent random-access arrays are preserved separately as `.randomaccess.bin.gz`. Complete unchanged payloads, stderr, source copy, original-source hash manifest, instrumentation diffs and build commands remain local under `S15/`. This product includes software developed by Niels Provos.

Authored replay scripts are `s15_build.py`, `s15_trace.py` and `s15_finalize.py`. Invoke through the standard logger, for example:

```
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-s --label S15-replay0 --seconds 300 --input liber-primus/data/relikd/p0.jpg --input exploration/persistent-01/worker-s/S15/build.json -- .venv/bin/python exploration/persistent-01/worker-s/s15_trace.py 0
```

The trace modes are `controls`, `0` and `26`; actual modes require saved passing controls. STOP and the original 03:30:37 UTC deadline remain enforced. Recorded runs are `20260917T015532.081863Z-S15-build`, `20260917T015655.080459Z-S15-controls`, `20260917T015719.306267Z-S15-actual0`, `20260917T015740.932640Z-S15-actual26`, and `20260917T015850.771013Z-S15-finalize`. All exited zero, without timeout; trace/control jobs each took about 12 seconds. Original images, P28 artifacts, shared state and earlier S01–S14 artifacts were not changed.
