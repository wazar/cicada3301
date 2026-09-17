# P23 — exact greedy Gematria Primus rendering feasibility
Six explicit units on originals0/1 cannot be outputs of the frozen Latin-to-rune renderer. This is an exact finite incompatibility, independent of English scoring, keys or statistical thresholds.

The simplest witness is original0, unit0: separate rune IDs18(E) and3(O) at rune positions2/3 and source-character positions2/3. Their only accepted spellings are E and O. Within one parser call, EO must become the single rune12. No supported alias avoids that merge.

## Exact format being tested
The hypothesis is that an intermediate A–Z Latin-character output was then greedily rendered independently within each F06 explicit unit by lp.gematria.keyword_to_indices. The inspected implementation uppercases, removes ASCII spaces, prefers its seven two-letter spellings TH,EO,NG,OE,AE,IA,EA, and supports V→U, K/Q→C and Z→S aliases. All29 canonical spellings plus four aliases participate in the test.

This bounds one implementation/domain/segmentation convention. It does not exclude direct rune emission, hidden parser resets inside a unit, nongreedy rendering, other aliases such as ING/IO, punctuation handling, transcription changes or all Latin-first mechanisms. ASCII spaces inside this function are deleted, so they are not reset boundaries; separate parser calls are.

## Complete membership method
A finite dynamic program considers every allowed spelling of each desired rune. It retains all reachable last-spelling states, exact spelling-path counts and one complete Latin witness when feasible. Two adjacent spellings are compatible only when the greedy first token of their concatenation consumes exactly the preceding spelling and emits its desired rune. Since all tokens have length at most2, no later character can change that decision. This makes local compatibility sufficient as well as necessary.

Every successful witness is reparsed through the exact repository renderer. Every failure retains its first unreachable position and every incoming spelling/transition obstruction, rather than relying on a failed canonical expansion.

A separate checker derives14 forbidden rune-pair types and proves that, for this particular spelling inventory, all spelling alternatives have the same compatibility. The supported aliases do not occur in the relevant digraph joins. Thus canonical reparse happens to give the same feasibility here, but that fact was established by checking all aliases rather than assumed.

## Actual source-mapped witnesses
| Page | Explicit units | Feasible | Infeasible |
|---|---:|---:|---:|
|0|59|55|4|
|1|63|61|2|

The first obstruction in each failing unit is:

| Page/unit (zero-based) | Rune IDs | Spellings | Page rune positions | Source-character positions |
|---|---|---|---|---|
|0/0|18,3|E + O|2,3|2,3|
|0/18|10,25|I + AE|83,84|107,110|
|0/22|16,8|T + H|105,106|135,136|
|0/55|3,18|O + E|246,247|323,324|
|1/12|9,6|N + G|60,61|422,423|
|1/26|3,18|O + E|105,106|485,486|

The I+AE example would greedily consume IA first, so the obstruction also covers a single-letter rune followed by a digraph rune. No cross-unit or cross-page merge is asserted. Source-character positions preserve F06's coordinate convention, including non-rune gaps; they are not image pixel coordinates.

All122 units retain complete rune lists, bounds, source positions, DP states and witnesses or obstructions in actual.json. The six first-obstruction witnesses suffice; this is not advertised as an exhaustive count of every forbidden adjacency within each failed unit.

## Controls and independent proof
All33 accepted single-token spellings pass. Exhaustive testing covers:
- 841 rune pairs:827 feasible,14 infeasible, with1,075 valid spelling paths;
- 24,389 rune triples:23,594 feasible,795 infeasible, with35,030 valid spelling paths.

Each is compared with brute enumeration of every spelling combination followed by the actual renderer. Four hundred fixed random A–Z Latin strings, including empty input, render forward and pass membership. Lowercase/space behavior, all aliases, all digraphs and boundary resets are explicitly tested. Together TH yields rune2; separately rendered T and H yield runes16 and8, which cannot form one word under this parser.

Four complete held solved-source rune texts supply257 words. Their canonical Latin expansions render forward, all generated outputs pass membership, and none of those257 source words changes segmentation. Original source spans and character-to-rune expansion maps remain available; these are capability controls, not an assumption that all solved texts establish a universal rendering rule.

The no-import p23_check.py reads the declared table through AST, implements an independent two-character lookahead parser, proves alias-invariant pair compatibility, rechecks every rune triple, all forward controls, every actual source map and all six obstructions. independent-certificate.json contains the14 complete forbidden-pair certificates and actual source witnesses.

Controls took0.30s, actual0.05s and independent replay0.09s; all logged exit0, one thread. Source/code hashes, exact command snapshots and all raw outputs are retained. No reserved page, original50, new image, installation or Git mutation was used.

P17 used the same forward renderer for a source search; the narrow prior check found no equivalent inverse-membership test. This is a specific input-format contradiction, not evidence selecting a different cipher or a broad rejection of Latin-character intermediates.

Review39 independently passed alias-complete maximal-munch trie reconstruction, every pair/triple, all122 actual DP histories/maps, all400 random controls and257 solved-source words. See exploration/persistent-01/review-39/REPORT.md. No production defect or scientific change was required.
