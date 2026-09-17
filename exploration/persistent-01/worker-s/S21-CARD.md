# S21 frozen top14 source-mass error bound

Follow-up to S20, using exactly its five pinned normalized source streams, every2355-rune contiguous window and raw maps. A S19 output under any bijection uses exactly14 rune types. Even granting arbitrary choice of at most14 types and arbitrary ordering, no more than the total count of a source window's14most frequent types can agree. Thus errors≥2355−top14mass. This necessary Hamming error bound also survives unrestricted permutation of output positions, but does not establish any alignment, mapping or approximate solution. Actual output frequency restrictions and cipher equality structure are deliberately relaxed.

Compute this quantity for every unchanged S20 window. Preserve all29 counts/window, all error bounds, full per-source minimum and its error fraction, every achieving offset and its support/raw-span. No assignment solver or stronger bound; no source, normalization, mapping, key or optimizer expansion.

Controls before source results: exhaust all four-symbol histograms with counts0..3, for allowed-type caps1/2/3. Enumerate every permitted subset and verify maximum covered mass equals sorted top-cap mass. Direct small source sequences confirm that projecting excluded symbols to a retained symbol attains that lower bound in the relaxed arbitrary-output problem. Verify production sliding histograms against independent symbol-prefix differences for every source/window/count and support against frozen S20 arrays.

One numerical thread; logger≤900seconds, STOP check, finish before03:24UTC2026-09-17. Controls and actual may run sequentially in one bounded job with controls recorded before enumeration. No random search, image, reserved data, Git, shared state or edits to S19/S20.
