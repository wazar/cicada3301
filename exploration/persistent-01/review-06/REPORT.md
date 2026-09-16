# Review 06 — M21 accepted within its stated scope

The historical interoperability correction is reproduced. This is a correction to the repository's decoder description and historical plaintext recovery, not an LP2 solution or a reason to repeat the LP2 search.

## Source identity and execution boundary

I independently fetched both exact official CPAN URLs, compared bytes with the saved archives, and compared every manifest-listed extracted file with its archive member and saved hash (49 RSA files, 10 Armour files). No source patches were found.

- https://www.cpan.org/modules/by-module/Crypt/Crypt-RSA-1.99.tar.gz — SHA256 `4706fd6605c920cd1c79f4afc0036b14e233620162b3957abe9b5f1be50b24be`.
- https://www.cpan.org/modules/by-module/Convert/Convert-ASCII-Armour-1.4.tar.gz — SHA256 `97e8acb6eb2a2a91af7d6cf0d2dff6fa42aaf939fc7d6d1c6057a4f0df52c904`.

`DataFormat.pm::mgf1` starts at zero, serializes its counter as four big-endian bytes, and increments by hLen=20. Its `while ($i <= $l)` can compute one unused digest at exact length multiples; truncation means this does not change returned bytes. OAEP uses an empty label by default, EM length k−1, zero PS, and byte 0x01 delimiter. The inspected wrapper uses k−42 plaintext and k-byte ciphertext blocks. These are actual source properties, not inferred from readable output.

The harness extracts the named function bodies verbatim; I inspected the extraction regex and its boundaries. Digest::SHA substitutes SHA1, synthetic randomness is fixed, debug/error are adapters, and PARI is identity only for tiny counters and base256 arithmetic. All tested values are exactly representable by native Perl arithmetic. This is valid for this padding test, but is not a full installed-library RSA/dependency test. Large RSA integers are independently handled in Python. Armour itself runs unmodified. The source harness's hash at review is `6c3f6788b276440c03c85a8a2118a43bfcf322552e3ad687fd2ae34feb32e443`.

## Independent reproduction

`check.py` imports no worker algorithms. It independently parses the stored carrier, validates compressed-container MD5, checks exact single-field lengths, and obtains all 162 ciphertext bytes. The carrier SHA256 is `65ff60bfa019e424ce2ae23994f19af5692f7e12e6bc177830b42a154985defd`. Published n equals the supplied public puzzle factors' product, e=65537, k=54. All three ciphertext values are below n. Lambda-based modular decryption and a separate CRT reconstruction agree, and each resulting 53-byte EM re-encrypts exactly.

Independent strict Python and extracted-source Perl recover all three blocks, lengths 12/12/1. Standard counter-step-one decoding fails the delimiter on all three. The exact concatenation is `\ncu343l33nqaekrnw.onion\n\n` (25 bytes). It was recorded only; no navigation occurred. No PGP signature was checked in this review; historical authorship remains inherited attribution, not newly established here. Both old cited external factor-script locations are absent in this checkout; the constants remain available in C1 and are arithmetically checked against the carrier.

Six independent known-message vectors match the source harness byte-for-byte at EM lengths 41,42,53,53,255,511, including empty and maximum-capacity messages. Seven invalid cases are rejected by both decoders: absent delimiter, nonzero PS, wrong first tail byte, wrong hash, too-short EM, reversed EM, and an added leading zero. Thus agreement is not just a roundtrip through two mutually permissive decoders.

## Why the prior header negative survives

For every eligible EM (length at least41, hLen20), seedMask has length20, so only SHA1(maskedDB || BE32(0)) contributes. Both conventions recover the same seed. DB's first20 bytes likewise use only SHA1(seed || BE32(0)). Therefore old and corrected DB[0:20] are identically equal for every input. Equality to SHA1(empty), the actual old acceptance predicate, is unchanged. A strict corrected parser adds constraints and cannot convert a header miss into a hit. This proof is independent of plaintext, byte order, length choice, key, and how the EM was generated, provided the same eligible EM is supplied.

I additionally AST-extracted only the actual old `mgf1`, `oaep_unmask`, and `match_cryptrsa_oaep` definitions, without executing imports/mains or reading any payload. Their header results agree with my independent implementation on 600 deterministic inputs over six lengths and on the positive/malformed panels. This validates the predicate targeted by the proof, rather than merely comparing two new implementations. No LP2 data or reserved-page inputs were read.

## Report assessment and decision

Worker M21 `RESULTS.md` was read after completion. Its main claims, explicit dependency limits, compatible-parser-versus-proven-sender-version distinction, and qualified signature attribution are supported. No material correction to that report is required. The old C1 `cryptrsa.py` also retains a stale comment alleging 161 rather than162 bytes; documentation correction should identify it along with the counter error, while preserving historical outputs. The old MGF description should not be advertised as full-source-compatible. The old first20-only negative remains bounded by its original tested paths, not enlarged by this review.

Logged execution: `runs/20260916T213432.503918Z-independent-m21-review/command.json`, exit0, 1.811s. Exact command, input hashes, script snapshot, stdout/stderr are retained there; Perl command and outputs are separately retained in this review directory. No installations, Git mutations, source/output changes outside review-06, or unrelated keys. Read-only CPAN downloads only.

Next decisions: (1) coordinator may publish a scoped historical decoder/documentation correction; (2) checkpoint this RSA lane and allocate further work to another mechanism unless new artifact evidence changes its search premise. No extra RSA key/offset sweep or LP2 rerun is justified by this finding.
