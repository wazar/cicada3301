# Post-run seed discrepancy disclosed during independent review14

The pre-execution card states real-null seed330901. The executed `calibration` function instead initializes with `330901 + sum(name.encode())`, giving **331321** for `real`. This is an implementation deviation from the card, not a post-result change or a chosen favorable seed. The original card, executed source, outputs and draws remain unchanged; no rerun will replace them.

The same naming formula supplies the control-null seeds, while control-generation seeds330902+i remain as stated. Review14 checks the exact streams and name-seed uniqueness within this finite run. The general byte-sum naming method can collide and should not be treated as a general unique-seed scheme. This note records the error; it does not repair research code or reinterpret the result as preregistration-perfect.
