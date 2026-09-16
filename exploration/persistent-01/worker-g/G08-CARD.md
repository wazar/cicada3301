# G08 — red fields as integer metadata for delimited body

Changed role: a red heading/footer could be an integer length/check value rather than encrypted text. Exact image-backed field pairs frozen: p3 heading[0,16) with body[16,119); p3 heading[119,122) with remaining visible body[122,217); p7 footer[194,208) with preceding body[0,194). Second p3 body may continue on another page, so no whole-section exclusion follows.

Interpret entire red field as base29 zero-based rune digits, forward/reverse only. Compare exactly (no truncation/modulus/tuning) to body rune count, index sum, first29-prime sum, and number of distinct rune types. Twelve target comparisons per pair? Four targets times2 directions =8 perpair,24 total. Explicit lengths make many checks simple size mismatches; count those honestly. The purpose is reject a small concrete field-role claim, not search arbitrary checksums.

Control encodes each computed target in exactly red-field length when representable and recovers it. 1000 within-field rune shuffles per pair with same eight tests; store full values/counts. No English detector or additive cipher. Next two actions: compile source-bounded G findings for review; then implement a genuinely different non-language finite-state constraint only after comparing existing C transition coverage, rather than expanding numeric metadata variants.
