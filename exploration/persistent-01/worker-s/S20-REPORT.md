# S20 — exact source-support obstruction

None of the **224,473** admitted 2,355-rune source windows can equal S19's complete word-length payload under a bijection. The actual payload uses exactly **14 distinct labels**. Every source window uses at least **23** distinct runes. A bijection preserves support size, so this is an exact necessary-condition obstruction independent of optimizer quality or language scores.

| Existing source stream | Normalized runes | Windows | Minimum support | Maximum support | Support14 windows |
|---|---:|---:|---:|---:|---:|
| Clean Caesar |120,854|118,500|23|26|0|
| Virgil I |27,183|24,829|25|27|0|
| Virgil IV |25,577|23,223|24|27|0|
| Virgil VII |29,555|27,201|24|27|0|
| Virgil X |33,074|30,720|25|27|0|

This only excludes exact equality to a contiguous window in these five fixed normalized streams under the shared bijection. It does not exclude Latin generally, other sources, paraphrase, abbreviations, text assembled from multiple windows, a nonbijective map, or another role for word length. It supplies no evidence for any such alternative. S19's scorer-based result and its imperfect/support-mismatched controls are unchanged.

The source interpretation was chosen adaptively because S19 exposed the 14-versus27 support mismatch. All corpus bytes and normalization were already pinned. Caesar is the existing clean Q05 training word stream with its original exclusions; Virgil books I/IV/VII/X are the same books used for S19's fixed prefixes, now read to each next book heading. Windows may begin/end inside a normalized word. No windows cross distinct books/works, although Caesar's cleaned concatenation crosses its already omitted heading gaps. Every raw word and every normalized rune's half-open decoded-character span are retained, preserving UTF-8-sig decoding and CRLF positions. No actual image or text was repaired.

## Controls and checks

The pilot verified all five fixed-source prefix supports under seeded random29-bijections, plus synthetic14/15-symbol classifications. It exhaustively compared every positive window length for all binary and ternary strings of lengths1–7: **22,862 tiny panels**. The production sliding histogram and an independently structured last-occurrence presence algorithm agree at **every** actual source window. Direct set counting additionally confirms deterministic first/last and all minimizing/passing offsets. All source hashes, clean Caesar word maps, S19 Virgil prefix runes/spans, F06 length units and the actual support were checked. These are two implementations within this experiment, not a fresh external reviewer.

The source/control pilot passed in1.485seconds; full enumeration passed in.536seconds including logging overhead. No scientific failure, timeout, repair, parameter change or search expansion occurred. One numerical thread and existing STOP/deadline guards were used.

## Prior scope and reproduction

P04 addresses a shared vowel-deleted rune-to-consonant codebook over five page-specific source-window sets. Its support/count reasoning overlaps conceptually; its units, normalization, source selection and equations differ. S20 uses S19's 2,355 word-length symbols and the fixed complete Latin source windows. This is a narrow exact source bound, not broad novelty or independent language evidence.

`S20/result.json` stores full counts/histograms. Each `S20/*-windows.json.gz` retains every support count, every minimizing offset/raw span and all support14 offsets (empty). `S20/sources.json.gz` retains complete normalized source arrays, words and rune-character maps; `actual.json.gz` retains all F06 source pages and actual length-symbol sequence; `controls.json.gz` retains controls, maps and seed632020. `inputs.json` pins all sources and code. `S20-CARD.md` was written before executable code and actual window enumeration.

Reproduce through the shared logger with `.venv/bin/python exploration/persistent-01/worker-s/s20.py pilot`, then `full`; the exact invocations, stdout, exits and code snapshots are retained in `worker-s/runs/20260917T031311.749239Z-S20-source-support-pilot` and `20260917T031332.472939Z-S20-source-support-full`. The fixed local completion guard is03:25UTC2026-09-17; later reproduction requires an explicitly documented deadline-only update or an independent checker, not silent changes to frozen artifacts.
