# N19 — zlib metadata-selector gate failed

**Stop this selector: none of the four controls uniquely selects the true source. No actual or null output was compressed/scored.** The gate was frozen before the first compression result; no parameter, tie rule or statistic was changed after failure.

| Control | Admitted outputs | True competition rank | Equal-size truth ties | Unique shortest true? |
|---|---:|---:|---:|---|
|welcome|15|8|3|No; wrong insertion150 is uniquely shortest|
|jpg107-167|7|1|4|No|
|p56|6|1|3|No|
|p57|4|1|4|No|

The one measure was `len(zlib.compress(bytes(runeindices), level=9))`, default zlib header/window. Build and runtime library are both1.2.12; API signature/doc are saved. Rune indices were compressed directly, without transliteration, dictionary, language model, added boundaries or normalization. Within each packet, all inputs have equal length. Full size vectors, compressed bytes, output/source hashes and exact metadata IDs are retained in result.json and individual zlib files. Ranking counts strictly smaller compressed sizes; ties are explicitly retained rather than resolved favorably.

Tiny512rune controls behave as expected: repeated0123 compresses to17bytes, a fixed seeded aperiodic stream to342bytes. That generic sanity check does not establish ability to distinguish the source from BWT metadata alternatives. Deterministic replay verifies all32control outputs and both tiny outputs, decompression identities, source/output hashes, ranks and gate. One-shot and two-chunk streaming compression produce identical bytes under the same frozen setting. Both logged runs exit0; the scientific failure is the capability gate, not an execution error.

This was not blind: the worker had previously encountered the actual N18 output. The coordinator specified the sole compression statistic before this card, and no actual score was used to select it. Because the source gate failed, the experiment supplies no compression-based inference about actual plaintext or any other selector. It does not impose a new gate on unrelated lanes or change N18's exact format compatibility.

All work completed before03:25UTC under the existing window; no deadline extension, new source/library download, image, key, alphabet, serialization, shared-state edit or Git action occurred. Freeze and stop; no replacement compressor or trained scorer follows this failure.
