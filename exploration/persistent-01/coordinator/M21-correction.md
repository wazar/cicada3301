# Historical OAEP compatibility correction

Fresh review06 reproduces worker M21 against pinned official Crypt::RSA1.99 and Convert::ASCII::Armour1.4 source. The routine named MGF1 in Crypt::RSA1.99 uses SHA1 counter values0,20,40,... . The inherited C1 and E01 implementation uses0,1,2,... . The first mask block agrees, later blocks do not.

Using the actual library convention recovers three strict historical message blocks and the already-public address recorded in M21/result.json. Exact cipher length is162 bytes, not the stale161-byte comment in C1. The container checksum, public puzzle factors, RSA re-encryption, source interoperability and malformed-padding controls independently pass. Historical PGP attribution was not reverified; no address was visited.

This does **not** invalidate the inherited E01 first20-byte header test: its seed and first mask block are mathematically identical under both conventions for every eligible input. A correct strict parser adds constraints, so it cannot rescue any old header miss. No LP2 payload reread, expanded key search or repeated negative sweep was needed. The result corrects full-body compatibility, not the old test's recorded scope.

Old code and results remain intact. See worker-m/M21/RESULTS.md for exact sources, independent implementations, missing historical files, licenses and reproduction commands; review-06/REPORT.md for independent source identity, six valid and seven invalid fixtures, and algebraic predicate review. A later narrowly scoped repair can adopt the correct counter convention if historical full-body decoding is needed. Do not silently change a standard MGF1 routine used for other protocols.
