# S21 — unavoidable error mass from the14-type payload

S20's support mismatch cannot be confined to one or two rare runes in these fixed sources. For every one of the224,473 source windows, any2355-rune output using at most14 rune types must disagree on at least119 positions (**5.053%**). The per-source best lower bounds are:

| Source | Minimum unavoidable errors | Fraction | Windows attaining minimum |
|---|---:|---:|---:|
| Clean Caesar |119/2355|5.053%|7|
| Virgil I |163/2355|6.921%|45|
| Virgil IV |149/2355|6.327%|3|
| Virgil VII |152/2355|6.454%|4|
| Virgil X |149/2355|6.327%|43|

For source counts n_r, any output type set T with at most14 symbols can agree with at most sum(r in T)n_r source positions. Maximizing that quantity gives the mass of the14most frequent source types. Therefore2355 minus that mass is an unavoidable Hamming error count. Arbitrarily reordering output positions cannot remove the type limitation. The bound grants more freedom than S19's substitution, since it ignores output frequencies and all ciphertext equality constraints. It does **not** show a S19 mapping attains the bound or resembles any source window; actual errors can be much larger. This is not an approximate-text acceptance threshold.

The same five frozen streams and all2355-rune windows from S20 were used, with no new normalization or source. The bound concerns those exact windows, not arbitrary Latin or another payload model. In particular, S19's high recovery on27-symbol controls cannot be transferred to its14-symbol actual payload as evidence of source compatibility.

Before source enumeration,768 exhaustive small histogram/cap controls compare sorted largest counts against every allowed subset; explicit projections attain the bound in the relaxed arbitrary-output problem. For every source window, production sliding counts match independently constructed per-symbol prefix differences for all29 symbols:6,509,717 count comparisons. Window totals and all support sizes also match frozen S20. This is internal independent arithmetic, not a fresh external review. All controls and actual calculations passed without failures, timeouts, code repair or parameter changes.

`S21/*.npz` retains every29-count vector, error bound and support. Per-source JSON retains every minimum-achieving offset, its support, complete count vector and raw source span. `S20/sources.json.gz` supplies the pinned full rune/raw-character maps; `S21/inputs.json` pins that file, S20 support arrays, the card and implementation. `S21/result.json` contains the aggregate. The single logged job completed in.538seconds, one numerical thread, before the03:24UTC completion guard. Exact command/source snapshot is in `worker-s/runs/20260917T031720.232654Z-S21-top14-error-bound`; executable is `worker-s/s21.py` under the standard logger.

This is a quantitative follow-up to S20's exact support obstruction and overlaps that same source-bound logic. No assignment solver, stronger relaxation, optimizer, larger key family, image, reserve, shared-state or Git operation was used.

Fresh review71 independently verified all count arrays, bounds, extrema/source maps and768 subset controls. It initially detected that publication had normalized the checkout prefix in S20/inputs.json after S21 pinned its original hash. The exact original remains in `private-originals/worker-s/S20/inputs.json`; `publication-redactions.json` records the original-to-published hashes. Review71 verified both hashes and that replacing only the checkout prefix with `<REPO_ROOT>` produces the published bytes. No scientific value changed and S21's original pin was not rewritten. The failed initial provenance check and its explicit resolution are retained in `review-71/REPORT.md`.
