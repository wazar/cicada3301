# P21 — literal shedding as a complete deletion decoder
Removing exactly the first and last rune of each explicit unit does not reveal a readable complete output on originals0/17. The two-page maximum score has full-procedure cyclic-origin tail0.760. Four complete wrapping controls recover their original runes and boundaries exactly, each with tail0.005 against199 controls.

This tests one literal reading of the solved parable, not the meaning or intent of the passage in general.

## Operational readings and selected rule
The verified solved_p57_parable.txt reference tells the reader to shed their circumferences and find divinity within. Two precise operations were considered before scoring:
- A remove one outer rune at each end of every explicit unit and retain all strict interiors;
- B repeatedly remove outer pairs until only one odd-length or two even-length central runes remain.

Only A was tested. The source does not specify units, one versus repeated removals, or an encoded output register. Those are acknowledged choices, not inferred facts. B was not computed after the miss.

The complete decoder has no key, shift, reversal or additional stage. F06 explicit units retain their original order; units of length1/2 disappear. Each nonempty retained interior ends with a boundary token for the frozen rune/boundary LM. All retained and discarded runes map to original indices and source-character positions. This computational extraction leaves source files unchanged.

## Actual complete outputs
| Page | Original runes | Retained | Discarded | Empty-output units | Full-output score |
|---|---:|---:|---:|---:|---:|
|0|262|147|115|10|−4.97517695|
|17|273|140|133|19|−4.93765038|

Both complete transliterations are retained in full-output.txt and were inspected. They do not form coherent full plaintext. No isolated fragment was used as evidence. Source rune indices, unit bounds and every discarded short unit remain in actual.json.gz.

The fixed maximum over both pages is−4.93765038. Of999 null panel maxima,759 meet or exceed it, giving add-one tail760/1000=0.760. Each null chooses independent uniform cyclic origins inside the complete original units, then applies the exact same removal, boundary treatment, LM and two-page maximum. It preserves each unit's length, multiset and cyclic ordering. Uniform origin exchangeability is not established for the ciphertext, so this is a conditional positional comparison, not a universal cryptographic null.

## Controls and detector limits
The four held solved-source rune texts were wrapped word-by-word in two uniform random cover runes, with fixed seeds. The decoder recovered every original rune and every word boundary. There was no unknown key or adaptive extraction search.

| Source | Original runes | Wrapped runes | Words | Full-output score | Origin tail |
|---|---:|---:|---:|---:|---:|
|welcome|515|763|124|−2.26419149|0.005|
|jpg107-167|319|495|88|−2.06140241|0.005|
|p56_an_end|85|135|25|−2.47548447|0.005|
|p57_parable|95|135|20|−2.28792948|0.005|

Each uses199 own origin nulls. Natural source word lengths plus2 differ from actual unit lengths; the controls contain no wrapped length1/2 units, whereas actual extraction drops29 such units across the two pages. Thus exact control recovery does not establish coverage of a construction with missing letters in short actual units.

The frozen LM has five existing rune-English training groups; it was not refitted. This detector cannot exclude meaningful outputs in an unsupported language/register or encoded intermediate format. It also does not establish that literal shedding should yield unencrypted text. A fixed one-step direct decoder was tested because it is a simple operational reading, not because the instruction uniquely specifies it.

## Prior overlap, validation and retention
K04 tested categorical word-position predictions. P21 instead tests deletion as the complete output operation and inspects all resulting text, while sharing delimiter and English-register assumptions. H14 tested last-first equality closure, not shedding. An initially considered positional coincidence statistic was not run because it overlapped K04 more closely.

Independent p21_check.py imports no decoder/LM implementation. It rebuilds the training counters and conditional probabilities from the five pinned source texts, regenerates all cover and origin draws, reconstructs every retained/discarded position and independently scores all2,800 complete control/actual/null outputs. All checks pass, including exact source-coordinate coverage of every original0/17 rune.

Logged controls took0.68s, actual/nulls1.25s, replay0.71s; all exit0, one thread. Complete null outputs, phases, maps, source hashes, code and logs are retained. No reserve, original50, new image, alternate operation or post-result parameter change was introduced.

The experiment ends with no plaintext candidate and no extension to repeated center extraction. It is a bounded English-register test of one source-motivated direct operation.
