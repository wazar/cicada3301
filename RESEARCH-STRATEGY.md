# Research strategy: question the model, not only the key

**Version:** `outside-box-v1`  
**Applies to:** the continuous research mission in `CICADA-CONTINUOUS-RESEARCH.md`  
**Owner direction:** think beyond the current approach; it is not established as the best route.

## 1. What we do and do not know

The audit gives us useful input checks and reference arithmetic. It does not establish the method used by the remaining puzzle. Read the scoped findings in [PARALLEL-01](audit/reports/PARALLEL-01.md), [NEXT-01](audit/reports/NEXT-01.md), and [OVERNIGHT-01](audit/reports/OVERNIGHT-01.md). Their measurements are evidence. Their method choices are not instructions to assume the same mechanism forever.

In particular, a correct transcription hash does not make a flattened rune sequence the complete problem. Correct handling of literal F on solved groups does not prove that unsolved pages use that rule. A language score is a detector, not a specification of the hidden message. A large number of failed candidate tests does not establish an optimal research strategy.

There is no established guarantee that our current approach is the best way to solve this puzzle. Do not claim one. Also, do not wait for such a guarantee before acting. Compare approaches through concrete predictions and measured outcomes.

**Core rule: do not mistake the tool we have for the problem we need to solve.**

## 2. Research allocation

Initially use one worker for a justified extension of existing methods and two for different problem models. Aim for at least half of substantive effort on alternative-model tests until an independently checked predictive result justifies concentration. This is a flexible resource rule, not a claim about probabilities of success.

Keep one lane outside the legacy English quadgram ranking and one outside the additive mod-29 candidate-keystream model. These can be the same lane, but the other alternative lane must still challenge a materially different assumption.

Varying a seed, key word, offset, sign, beam width, or CPU budget within the same model is an extension. It does not count as a new explanation merely because a different agent does it.

Review allocation at each substantive checkpoint. Evidence that a frozen rule predicts unused text or structure can justify concentrating workers. More attractive training text, exhausted sunk cost, or an impressive attempt count cannot. Keep a challenge task available so early preference does not become dogma.

## 3. Start each cycle with an assumption test

Spend a short reasoning pass on these questions, then execute work:

- What must be true for our current method to succeed?
- Which of those conditions were observed, and which did we choose for convenience?
- What simple alternative could explain the same observations?
- What measurement or decoding attempt would make the two explanations behave differently?

Use an experiment card, not a long essay:

```text
Assumption challenged:
Alternative mechanism or representation:
Observed feature or simplicity argument motivating it:
Prediction different from the current model:
Exact transformation, input, and output type:
Small control and real discovery-input test:
What would count against it:
Search/tuning choices and evidence limits:
First executable step:
```

A speculative idea may receive a cheap test without an explicit prior clue. The idea must still be precise enough to fail. Do not require a solved passage to name every allowable mathematical operation.

Do not ask the owner to choose between every new hypothesis. Generating, implementing, and testing them is part of the assigned work.

## 4. Directions that genuinely change the question

These are examples, not a mandatory finite queue. Choose or invent tests from the actual source and observations. Do not assume any example is the solution.

### A. We may be using the wrong units

Perhaps a rune is not always one encrypted letter. Separators, word-sized groups, paired symbols, line positions, prime values, or a mixed rune/alphanumeric field may carry part of the rule.

A useful first test compares a small number of explicit representations on discovery input. Preserve the map back to every original symbol. Ask whether one representation exposes a repeatable dependency, constraint, or decoding relationship that another erases.

Do not call a tuned relabelling of every symbol a discovery. Report discarded information. A mapping chosen after seeing a desirable output needs a fresh test.

### B. We may be looking for the wrong kind of answer

A region might contain an instruction, address, number table, coordinate list, key, compressed object, or another intermediate stage rather than ordinary English prose. Different regions may have different roles.

Define the proposed output format before searching and test its actual constraints. For structured data, require meaningful lengths, complete parsing, internal relationships, checksums where applicable, or a rule that predicts additional content. A few printable bytes, a short file signature, or a permissive parser accepting random input is not enough.

Do not assume that ciphertext which looks random is specifically compressed data or an external pad. These are competing hypotheses, not deductions from appearance.

### C. The operation itself may be different

Challenge additive keystream arithmetic. Consider a simple finite-state transform, position-dependent substitution, fractionation, a short composition of operations, or a constrained generative program. Select explicit small families; do not launch an unbounded search over all programmes.

One approach is inverse construction: write several simple encoders that can generate the observed kinds of structure. Compare what else each predicts. Matching the repeated-rune deficit alone cannot identify an encoder. Seek a second independent prediction.

A bounded search over short recipes is allowed when the operations, complexity limit, and tests are explicit. Record the cost of keys, exceptions, and parameter choices as part of model complexity. A custom rule as long as its output is not an explanation. Re-encryption alone cannot distinguish a genuine construction from one fitted to arbitrary plaintext.

### D. Pages may play different roles

A page could help interpret another page. Section boundaries might change the rule. A continuous mixed-format field might need to be treated as one object despite image cuts.

Test a specific relationship using a documented boundary or a prior prediction. Examples include a proposed index relationship, a repeated state, or an output from one region that becomes a justified input to another. Do not force one cipher or one language across the book.

The absence of evidence for a universal reset rule does not establish its opposite. Distinguish what is fit within a page from what is predicted across pages.

### E. The useful information may be outside the flattened stream

Inspect a defined region's line lengths, delimiters, initials, terminal marks, colouring, number placement, or relation between text and artwork. Byte identity with an archive does not logically prove that no deliberate information was present in the original object.

Start with actual discovery-page images and exact coordinates. Test one or a few justified extraction rules, not thousands of adjustable acrostics until a word appears. Control for image processing, typography, transcription ancestry, and the choices made while looking at the data.

This is not permission for a complete visual audit before any search. Inspect what a specific hypothesis needs. Do not invent glyphs, erased text, or image content.

### F. The clue may specify a procedure rather than a password

Treat a solved instruction as a possible operation, order, relation, or data-selection rule. Compare that interpretation with using its words as a key. Require an executable reading of the clue and account for ambiguous wording.

Do not extend this into free association about authors, secret organisations, numerology, or private individuals. Focus on public puzzle artifacts and reproducible operations.

## 5. Use fresh agents to challenge shared assumptions

At least once in the first substantive cycle, give a fresh worker a small neutral brief: the relevant artifact, verified measurements, and the known limitations. Do not lead with the repository's OTP-class headline or insist on the current decoder.

Have that worker propose two materially different explanations, implement the most discriminating cheap test, and compare the result with prior work afterwards. Do not call this strongly blinded research if the same files or conversation context are accessible. Document what context was actually withheld.

A different model name or agent identity does not create independence. Inspect shared data, scorer, parser, transform, and expected outputs.

Fresh review should ask: could the result arise from the fitting freedom, score selection, or a shared input error? It must also identify the next useful test when it rejects a candidate. Review is part of continuing research, not a reason to shut down all lanes.

## 6. Be imaginative about mechanisms and strict about evidence

Encourage unusual proposals, including proposals not on this list. Do not promote them because they sound clever. Prefer simple mechanisms with consequences we can test.

Do not require every useful clue to immediately produce plaintext. A cross-region prediction, a constraint that removes a large class of models, or a new reproducible structural relationship may be progress. Confirm the claim's scope and selection history.

Do not promote every new statistic into meaning. Comparisons must reflect the choices that produced the reported maximum. Adaptive discovery is permitted, but untouched validation must remain untouched until the rule is frozen.

For negative results, say what was tested and how the detector could fail. Do not conclude that a whole approach is impossible because one implementation or scoring rule missed its planted example.

After two unproductive extensions inside one model, redirect at least one lane to a different assumption. Do not change parameters forever merely because it is easy to automate. Conversely, do not abandon a simple useful method just to appear creative.

Keep the existing holdout rules. Reading a reserved page's image, layout, or alphanumeric content for a new theory also uses that holdout. Record every authorised reveal. Do not borrow its clues and later call its decoded text an untouched validation.

## 7. Report decisions, not novelty theatre

At checkpoints, record briefly:

```text
Current competing explanations:
Assumptions changed or retained:
Alternative-model tests actually executed:
New evidence and limitations:
Why the next resource allocation changed or stayed the same:
Next two executable tests:
Strategy version: outside-box-v1
```

Use the existing state, queue, and experiment files. Do not build a new management framework. A list of novel-sounding ideas with no executed test does not satisfy this strategy.

Do not claim that this allocation is optimal, that creativity guarantees success, or that continued work proves progress. This strategy is intended to reduce the risk of spending the entire session searching inside the wrong model.

**Continue until the mission's real stop condition. A failed hypothesis changes the next experiment; it does not complete the research assignment.**
