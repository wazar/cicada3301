# N18 — omitted-sentinel BWT serialization

**Original0 is format-compatible at sentinel insertion239; originals17/55 are not.** This separate standard metadata convention changes one P31 format result without changing any rune values/order. It is not a decoded-message candidate. Three of the19paired page0inventory permutations also admit reconstructions, and the source controls demonstrate that missing metadata can leave several complete outputs.

The frozen convention appends a unique lexicographically smallest sentinel to source text, applies cyclic last-column BWT, then omits the sentinel and its primary-row metadata. Internal sentinel0/runes1–29 preserve the canonical GP order exactly. Every one of n+1insertion positions was tested, including before/after the complete rune column. No alphabet search, word segmentation, extra stage, damaged-input repair or English scoring occurred.

| Input | Admitted main insertion positions | Compatible inventory permutations |
|---|---:|---:|
|welcome control|15, including exact true source position|2/19|
|jpg107-167 control|7, including exact true source position|3/19|
|p56 control|6, including exact true source position|7/19|
|p57 control|4, including exact true source position|6/19|
|original0|1 (index239)|3/19|
|original17|0|1/19|
|original55|0|3/19|

All140complete inputs and32,640sentinel insertion positions are retained, with125admitted full outputs overall. Every position has a complete inverse candidate, LF map, sentinel-cycle length, forward column and equality flag; valid outputs include complete rune arrays and insertion indexes. Actual0's full unspaced rune/transliteration output is also in actual-0-output.txt, without correction or fragment selection. Format membership alone does not select a language interpretation or establish relevance to the puzzle.

## Controls, exact logic and verification

All1,314tiny augmented columns (binary source lengths1–6, ternary lengths1–4, every insertion) agree with exhaustive forward-image membership. Rune-periodic sources are included; adding a unique sentinel makes their full source primitive. A valid unique-sentinel cyclic BWT must have one LF cycle, and a one-cycle LF reconstructs the complete source with sentinel last. Nevertheless the implementation does not depend solely on that shortcut: it forward-transforms EVERY reconstructed candidate and checks equality against the ENTIRE augmented input column.

All four complete existing source texts were transformed under this exact sentinel convention and their original full text/metadata pair is among admitted outputs. The15/7/6/4ambiguities are preserved; control acceptance is not unique plaintext recovery without metadata. Actual arrays and19inventory comparisons are byte-identical to P31's corresponding inputs. Control carriers differ because the sentinel changes the transform; index-shuffle seeds intentionally match P31. These comparisons are paired descriptive format frequencies, not independent new evidence or pvalues. They preserve inventory only, not adjacent-equality masks or word boundaries.

An independent no-production-import checker constructs Psi by queues of matching-symbol source indexes, traverses forward from sentinel's first-column row, and uses fixed-width base32 integer rotation sorting for forward checks. It verifies all32,640LF maps/candidates/cycle flags/full columns, all125admitted outputs, source/metadata controls, all133shuffle RNG streams and actual/P31 array equality. All pass. The same independent packed transform rebuilds exhaustive tiny image sets.

The20input pilot took2.24seconds (1.47MB), forecasting15.7seconds for all140. Remaining controls and actual batches completed within seconds, with no code repair, numerical failure or timeout. Full source packet maps and scientific inputs are retained. No P31/N17 result or source was modified.

Decision: P31 remains an exact cyclic-no-sentinel miss; N18 demonstrates why omitted metadata must be stated separately. Freeze N18 with one format-compatible actual page and common comparison acceptance, without a candidate claim or further alphabet/serialization expansion.
