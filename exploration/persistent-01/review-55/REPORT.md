# Review 55 — N13 and S16

Scoped PASS. Independently authored `audit.py` imports neither production algorithm. Logged execution `20260917T021627.736929Z-review55-format-certificates` exited 0 in 0.205 seconds. All snapshotted scientific inputs remained unchanged.

N13: verified 65,535 positive-integer Elias-delta round trips, 640 length endpoints, all 870 repaired controls and their 5,109 proposal traces. The initial control failure is real and preserved: its alphabet excluded the mandatory pattern 30. All 10,000 retained failed proposals have the relevant mandatory header; 360 earlier completed controls remain recorded, but their complete old RNG stream was not replayed. Exit chronology is failure, diagnostic failure, repaired success, independent check success. The declared pre-actual repair derives its 24 mandatory patterns from minimum integers and excludes 5, 7, 19; it does not change the actual format hypothesis.

For integer bit length L, delta length is L+2 floor(log2 L): lengths 39 and 42 straddle 40. Thus the four eight-rune units on original 0 (word indices 0,20,36,46) and two on original 1 (1,2) cannot each represent one unpadded delta codeword in five-bit chunks, irrespective of the rune-to-bit assignment. All six source maps and all unit classifications were rebuilt. Padding, multiple integers, other codes and altered boundaries are outside this statement.

S16: replayed all 40 planted panels including random orders, circles, selected rotations, all inequalities and the recovered orders. Exhaustive independent small-alphabet order checks covered 7,260 two-word panels over three labels and 84 words over four labels. Contradiction controls pass. Rebuilt all 406 actual directed inequalities and mapped both two-edge certificates: original 0 requires 0<18 and 18<0; original 1 requires 0<4 and 4<0. Each page separately therefore fails the proposed common within-page strict order making every explicit word its least cyclic rotation. Reversing the order also covers greatest rotations. This excludes neither arbitrary rotations nor per-word orders.

Provenance clarification: S16-result.json contains complete rune arrays and inequalities, but full original word maps only for the four certificate words. Other maps are in hash-referenced F06. The author acknowledged this in S16-REVIEW-CLARIFICATION.md; scientific outputs were not changed.

No scientific search was rerun. These are finite necessary-condition checks, not cipher-family or language exclusions. No failed review attempt occurred.
