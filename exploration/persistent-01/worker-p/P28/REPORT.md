# P28 — controlled OutGuess extraction and constant-prefix mechanism

The fixed default-plus-seven-passphrase experiment on original images0/26 produced12 complete binary outputs and4 tool crashes. None of the completed outputs passes the predeclared complete-format checks. The default outputs reproduce the previously reported1,417-byte common prefix. That entire prefix equals bitwise-NOT the independently derived default encryption keystream, establishing a constant-one extracted-bit mechanism for the shared bytes. It is not evidence of a hidden readable message.

The broad prior claim that no recoverable steganography exists is not established by this result. Four crashing settings are unresolved, the remaining binary outputs are unverified, and other formats/keys/channels are outside scope.

## Prior coverage and actual implementation

`analysis/armada20/stego_sweep.py` performs byte/pixel-LSB analysis, not OutGuess. `extract21.sh` contains a wider partially overlapping key sweep, but no retained outputs or command logs were found beside it; script-only evidence neither proves completion nor proves historical nonexecution. The old STEGO-VERDICT relies on third-party pre-extractions and explicitly parks the blank/passphrase control; LEDGER B-10 records that gap. Metadata/authenticity alone cannot establish absence of stego. Earlier P12 implements a different JSteg channel.

No installed OutGuess executable was found. Upstream0.4 tag source was retrieved from https://api.github.com/repos/resurrecting-open-source-projects/outguess/tarball/0.4 (repository commit prefix24810e1). Archive SHA256 `51763b460839175256623b17682b08eae855c29ab89f66bcaccb4e140b55ca4c`. README/ChangeLog and build/source paths were inspected. With no autoconf/automake, p28_build.py supplies explicit standard macOS feature configurations and compiles the unchanged C files with their bundled modified JPEG6b library. No installation or extraction-algorithm patch occurred. Binary SHA256 `1ad05d1cea85667b567cb790e7fb144f64150b866dcb1c3217194680615bed44`. The native binary, third-party source and archive stay local in private-P28; exact commands/configs/source hashes make the build reproducible. This is a0.4 macOS source build, not an unmodified historical0.2 Linux executable.

This product includes software developed by Niels Provos. The upstream README's broad statistical-undetectability claims are not adopted.

## Controls before actual

The exact pinned2016 historical carrier4gq25.jpg (SHA256 `a8340ad04b83fb3130e7ed9172867a440812e87089d6aa2b932d97c6ae38aebe`,26,342bytes) reproduces its existing1,136-byte expected payload byte-for-byte with no key, seed230. Expected payload SHA256 `fe89e77519dfaca998a257ed39c2861303029de2a49183db00eea0fda3a28010`. This measures compatibility for that carrier and command, not every historical version or negative extraction.

For each fixed setting, a copied authorized original0 carrier embeds and recovers a304-byte binary frame containing every byte value, explicit length and SHA256. All8 recover exactly and independently pass frame validation. Damaged/truncated-frame and complete gzip/zlib/trailing-data validation controls pass. No ECC, second-message, seed or key-derivation variants are tried. These positive controls prevent treating a dead tool as absence evidence.

## Fixed actual results

| Setting | Original0 output | Original26 output | Process disposition |
|---|---:|---:|---|
| Default, no-k |58,152|58,152|Both exit0, unverified binary|
|3301|54,051|54,051|Both exit0, unverified binary|
|33011033|24,438|24,438|Both exit0, unverified binary|
|circumference|0|0|Both SIGBUS, return−10; UNKNOWN|
|firfumferenfe|53,874|53,874|Both exit0, unverified binary|
|welcome|53,479|53,479|Both exit0, unverified binary|
|instar|36,324|36,324|Both exit0, unverified binary|
|pilgrim|0|0|Both SIGBUS, return−10; UNKNOWN|

The completed outputs are preserved in full with command/stdout/stderr/exit/hash records. Their whole byte strings are neither the known checksum frame, complete checksum-valid gzip/zlib without trailing bytes, nor complete PGP armor. There is no general-purpose authentication test for arbitrary binary plaintext; failed checks do not establish absence of a payload. Empty crash outputs are not valid empty extractions. The outer logger reports PASS because the experiment driver completed recording all statuses; that must not obscure the four child failures.

Original0 supplies714,405 usable bits; original26 supplies692,534. The source skips exactly0/+1 coefficients while retaining−1, and includes DC coefficients. Its decrypted header holds a16-bit seed and16-bit byte length. A capacity check compares this requested length with the usable bitmap byte count. Therefore the old statement that58,152bytes is simply the capacity determined by image dimensions is false.

## Controlled prefix explanation

Independent scalar review48 derives default initial encryption bytes3f5ed71c. An all-one raw header ffffffff decrypts to c0a128e3: seed41,408 and length58,152. Actual0,actual26 and the line-art surrogate show exactly those header values.

The independently derived4,096-byte stream, restarted as the source does for body decryption, predicts the complete observed constant-bit prefixes. Actual0 matches its complement for1,417bytes; actual26 for2,060bytes; the fixed line-art surrogate for1,087bytes. This accounts for the full1,417bytes shared by the two actual outputs. It establishes all-one selected input bits under this implementation, without asserting which spatial margins produce them or what the remaining bytes mean.

Two fixed Pillow surrogates are RGB2400×3600, quality92, optimized4:2:0,400DPI, carrying source0's exact2,576-byte ICC. They are not faithful Ghostscript/ImageMagick reconstructions. Pure white yields135,000 usable bits (16,875 bitmap bytes), the same header, and exit1 because58,152 exceeds capacity; no payload was produced. The central deterministic line-art grid yields948,360 usable bits and58,152 output bytes, sharing the predicted1,087-byte prefix. No geometry or JPEG-setting variant was selected after seeing results. Blank capacity failure alone does not confirm the full shared-margin hypothesis.

## Limits, preservation and next discriminating step

Source images remain hash-identical and are never edited; embedding used an explicit copy. No reserved4, original50, additional image, key dictionary or stego format was accessed. Build took3.40seconds, positive controls2.43seconds and actual/surrogate batch0.97seconds, single thread and under the15minute setup cap. Every input/output byte and subprocess status is retained; build and source files are locally reproducible from hashes.

Independent review48 supplied the historic carrier and scalar mechanism before interpretation; targeted review of the complete outputs and four crashes is ongoing. The four failures need an explicitly bounded safe source-level diagnosis before their extraction status can change. No silent tool repair, reclassification or broader key search is justified. The concrete new result is a measured tool/constant-bit explanation for the old prefix and a precisely limited fixed-key extraction record, not a blanket no-stego verdict.

Prose correction after S15 cross-check: the control frame is304 bytes (12-byte magic +4-byte length +256 data +32 digest); the earlier report said303. Actual payloads, hashes and exact-equality checks were always304 bytes and remain unchanged.
