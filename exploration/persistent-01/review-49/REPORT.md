# Review49 — P28 extraction evidence and bounded crash diagnosis

Independent replay passes for saved input/output hashes, all historical/planted payloads, actual/surrogate counts, prefix comparisons and source-derived iterator behavior. No extractor binary was rerun, patched or rebuilt in this review.

The experiment has16 actual queries (pages0/26, each default plus7named keys), one historical carrier,8own planted keyed carriers and2synthetic surrogates. The historical extraction equals the independently pinned1,136-byte payload from review48, seed230. Every own control equals the complete checksum-framed256-byte body, and each saved embed/extract status is successful. These qualify the0.4 build for the tested operations and this historical carrier; they do not prove universal0.2 compatibility or correctness on every noncarrier. Input originals and binary hashes agree with the records. Complete zlib/gzip parsing, PGP-start and checksum-frame checks find no structured actual output among successful cases; those finite validators do not cover arbitrary encrypted formats.

Of16actuals,12 finish with binary output;4 terminate with−10/SIGBUS and zero output. The latter are UNKNOWN, not negative. Blank surrogate rejects its claimed58,152-byte header against16,875-byte capacity; line-art produces58,152bytes. Surrogates are generatedJPEGs, not asserted historical-render pipeline replicas.

## Prefix and header mechanism

Independent scalar MD5/ARC4 code reproduces every actual/surrogate header from raw all-one bits under its specified key. Default header gives seed41408 and length58152. Complementing the independently generated default stream matches exactly the first1417bytes of page0,2060bytes of page26 and1087bytes of the line-art output. The page0/page26 shared prefix is1417bytes; both share1087with line-art. All saved pairwise prefix lengths and positional matches agree.

This demonstrates that the matching output prefix is the deterministic default decryption of extracted all-one bits; it is not necessary to posit shared meaningful plaintext. Source inspection from review48 explains why dimensions do not determine length and why zero/+1 exclusion and retainedDC/negative coefficients matter. It does not yet identify the precise image-space blocks responsible; no coefficient-to-pixel trace was performed. Nor does a mundane explanation of a prefix prove that arbitrary later bytes contain nothing.

## Four source-predicted failures

An independent source-faithful iterator simulation, including actual ARC4 reseeding and float32 skip adaptation, reaches zero skipmod on exactly the four crashed cases. It completes all12 successful actuals and line-art without this violation, and independently predicts the blank capacity rejection.

| Input/key | Body byte before failure | Bit offset | Remaining usable bits | Remaining payload bytes |
|---|---:|---:|---:|---:|
|0/circumference|62165|714262|143|18|
|0/pilgrim|64790|714262|143|18|
|26/circumference|62151|692281|253|32|
|26/pilgrim|64776|692281|253|32|

`iterator_adapt` truncates a value below1 to unsigned zero. `iterator_next` then computes random_word modulo zero, undefined in C, and `steg_retrbyte` has no usable-bit bounds guard. Static disassembly of the preserved actual binary shows ARM64 UDIV/MSUB implementing remainder followed by unchecked byte access. A64 integer division by zero returns zero without exception, as documented in the [Arm ISA overview](https://developer.arm.com/-/media/Files/pdf/graphics-and-multimedia/ARMv8_InstructionSetOverview.pdf). Therefore this binary's remainder becomes the raw PRNG word, producing predicted next byte offsets265341744,168771461,102405627 and116140085, versus actual bitmap byte capacities89301/86567. Disassembly and exact next words are retained.

This is a concrete deterministic invalid-read mechanism consistent with the observed SIGBUS. It is **not a captured faulting-PC trace**. No core, debugger execution, sanitizer run or extractor rerun was performed. Successful controls do not remove this noncarrier input-safety defect; historical0.2 behavior remains unmeasured.

## Next bounded experiment

A separately named guard-only diagnostic on exactly the four failed inputs plus the historical control could stop and log before zero-modulus or out-of-range access, comparing the table above while preserving ordinary successful output. It must not clamp the modulus, invent remaining bits or treat interrupted extraction as recovered plaintext. The coordinator may instead prioritize the historical-version comparison; neither was executed in this review.

All three logged scientific/static review jobs passed. An availability probe found otool but no llvm-objdump (shell status1 from the absent optional command); no experiment failed. Full producer files were hashed, scripts/results/disassembly and source inputs retained. No shared edits, new keys, reserve images, Git operations or broad tool audit occurred.
