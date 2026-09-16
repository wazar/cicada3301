# Blinded search protocol and disclosure

Coordinator independently wrote an additive mod29 encryptor with repeat rejection
and new ordinary-English prose. It imported no inherited plant or decoder. Two
hand checks verified mapping and rejection advancing the key without consuming a
plaintext symbol. Eight independently drawn key arrays were shuffled by choosing
a hidden correct index; key arrays have equal length. The supplied challenge states
the model, page lengths and candidate arrays but omits text, seed and correct label.

The answer JSON was saved outside the worker's supplied directory. Its SHA256 and
the challenge SHA256 were published in `blind-commitment.json` before ranking.
C froze ranking by the weaker of the two selected page scores, using both signs,
rigid and legacy beam, offset0. Its ranking hash was received and verified before
copying `blind-answer.json` and generator source into this directory. See
`blind-reveal.json`. No parameters were tuned using the revealed label.

This is **procedural blinding**, not filesystem access isolation: all agents share
a checkout and machine. The worker states it did not access the answer. This one
8-candidate search is a control, not an estimate of recovery probability across
messages or proof of safety at billions of trials.

Original generator source is retained unchanged. For exact reconstruction, replace
`secret=secrets.randbits(128)` with the recorded `seed` in a temporary copy and run
from a temporary directory containing `audit/parallel-01/coordination`; do not
rerun it over preserved outputs. Fresh invocation without that substitution creates
a different challenge. The generator's fixed temporary answer path was used only
for withholding the answer, not as a data dependency of C's ranking.
