# M21 — concrete historical compatibility correction; LP2 predicate unchanged

**FOUND ERROR in the historical OAEP body decoder, with no change to the existing LP2 first-20-byte predicate.** Crypt::RSA1.99's function named `mgf1` advances its SHA1 counter by20: 0,20,40,… . Repository C1/cryptrsa.py and e01_cryptrsa.py advance by1. Both produce identical first digest blocks, explaining why the repository saw valid SHA1(empty) headers but invalid message tails.

Using the actual upstream routine source strictly recovers all three 2014 ciphertext blocks. The exact concatenated historical plaintext is `\ncu343l33nqaekrnw.onion\n\n` (25 bytes). This is an already-public historical puzzle carrier, not an LP2 solve. The address was retained only; no request was made to it.

## Pinned primary sources

- [CPAN Crypt-RSA1.99](https://www.cpan.org/modules/by-module/Crypt/Crypt-RSA-1.99.tar.gz), 52,393 bytes, SHA256 `4706fd6605c920cd1c79f4afc0036b14e233620162b3957abe9b5f1be50b24be`. `lib/Crypt/RSA/DataFormat.pm` supplies counter semantics and big-endian conversion; `lib/Crypt/RSA/ES/OAEP.pm` supplies empty label, EM k−1, strict delimiter; `lib/Crypt/RSA.pm` supplies plaintext k−42/ciphertext k blocks and armour invocation.
- [CPAN Convert-ASCII-Armour1.4](https://www.cpan.org/modules/by-module/Convert/Convert-ASCII-Armour-1.4.tar.gz), 6,002 bytes, SHA256 `97e8acb6eb2a2a91af7d6cf0d2dff6fa42aaf939fc7d6d1c6057a4f0df52c904`. This exact public source parses/re-emits the carrier. Its version is our verified compatible parser, not a proven version fingerprint of the original sender.
- The code headers permit redistribution under the same terms as Perl; RSA archive includes COPYING(GPLv2), Armour archive ARTISTIC. Archives and original license files retained unchanged; complete per-file hashes in sources/manifest.json and sources/armour-manifest.json.
- Local primary signed-artifact path `corpus/A-primary-artifacts/pgp/messages/2014-01-rsa-oaep-challenge.asc`, SHA256 `65ff60bfa019e424ce2ae23994f19af5692f7e12e6bc177830b42a154985defd`. This experiment did not independently reverify its PGP signature; the exact bytes and literal n/e were checked. Factors taken from scoped public puzzle script `liber-primus/analysis/round19/C1/cryptrsa.py`; their product exactly equals the artifact's 432-bit n, e65537.
- Legacy file `corpus/A-primary-artifacts/cijhho123/2014/additional docs/scripts/Program to decrypt RSA message in perl.txt` is missing. No claim of reading it.

## Executed compatibility experiment

The isolated Perl harness extracts **verbatim** upstream `i2osp`, `octet_xor`, `mgf1`, `encode`, `decode`, `hash`, and `mgf` bodies from pinned files. It uses installed core Digest::SHA's SHA1, a deterministic 20-byte synthetic seed, no-op debugging/error adapter, and identity PARI only for small MGF counters/base256. No large integer RSA uses that stub. It does not pretend to run a fully installed Crypt::RSA dependency stack.

Four synthetic messages at encoded lengths53,53,255,511 roundtrip through the actual padding functions and match independently written Python encodings byte-for-byte. These include maximum-size12-byte message at53, zero/high-byte contents, and all256 byte values. Exact upstream Convert::ASCII::Armour runs unmodified, validates MD5, returns the same162 bytes as Python's strict single-field parser, and completes re-armour/unarmour roundtrip.

Independent Python modular arithmetic uses the public factors and compares n to the signed text. All three54-byte ciphertext integers are below n; decrypted EMs are53 bytes, and each re-encrypts exactly to its original ciphertext. Both Perl and Python strict decoders recover identical blocks (12,12,1 message bytes). Old standard-counter decoding fails delimiter on all three; new source-counter decoding passes all three. Old/new seeds, complete DBs, EM/cipher bytes and exact output are in result.json. The first DB divergence is byte20 (zero-based) for every block.

This resolves the nonsensical39-byte concatenated tail observation: each old tail was13 bytes, but those bytes were generated using the wrong second mask digest. It does not require repairing, dropping or adding a cipher byte. The serialized field is decimal length(name), NUL, decimal length(value), NUL, name, value; its leading cipher byte0x2c is data. Cipher length162 exactly equals3×54. MD5 covers the compressed container, not just cipher bytes.

## LP2 impact is bounded

For **every** EM in the old matcher's domain with hLen20, seedMask is20 bytes and therefore uses only counter0 under either implementation. Consequently recovered seed is identical. The first20 bytes of dbMask likewise use counter0; therefore DB[0:20] and the SHA1(empty) predicate are identical for every input. Counter differences affect only later DB bytes. A deterministic panel of1,000 inputs at each EM length53/255/256/511 confirms seed, first20-byte DB and predicate equality (4,000/4,000).

The existing E01 recognizer tests only that first20-byte equality. Its negative result is **not invalidated by this counter error**; its description of the full MGF/body layout is wrong. A source-correct strict parser adds constraints to the same necessary header predicate; it cannot turn a previous header miss into a hit. No corrected LP2 payload read or rerun is justified, so none occurred. The historical base60 interpretation is not established by this experiment. The 256-byte field cannot be an integral number of54-byte ciphertext blocks under this exact432-bit key, which remains only a bounded whole-ciphertext observation, not an exclusion of other keys or encodings.

## Reproduction and next decision

`compat.py` executes the bounded experiment; `source_harness.pl` is its actual-source cross-language oracle. Logger command records, source snapshots, outputs, exit codes, and explicit Perl subprocess command are retained under runs/ and perl-command.json. The first fetch failed an overstrict archive-root check before extraction; the corrected check allowed only the expected root directory and safe child files, then succeeded. Source fetching performed no installs. Main compatibility run completed PASS in0.324s. No old analysis output modified, no reserved pages or unrelated secret keys read, no Git changes.

Checkpoint for fresh review: inspect verbatim source extraction and dependency boundaries; replay the exact public cipher arithmetic; verify the counter/header-invariance proof. After review, correct repository descriptions through the coordinator; do not expand RSA keys/offsets or claim an LP2 discovery. This task resolved its source-level ambiguity and offers no new LP2 search convention.
