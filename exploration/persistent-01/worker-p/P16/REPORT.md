# P16 — fixed full-field GF(256) evaluation format

The corrected256-byte artifact is **not a codeword in the frozen format**: polynomial0x11d, points0..255 in unchanged order, maximum message-polynomial degree223. Its full interpolant has degree255. All32 parity checks are nonzero. No224-byte message was extracted and no input byte was changed.

Input SHA256: 3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290. Bytes were reconstructed solely from cached audit/alphanumeric-01/v1/transcription.json using the inspected R08 base60 mapping; transcription SHA256 d2a8cd1bf7cb20b0802c5262d752908d6036bd27a25730dd6a60fe2b8bfdfd7f. No image50 or new source was read. input.bin is a retained byte-identical copy, not an edited transcription.

The32 checks S0..S31 are:

    148 24 246 215 62 123 4 161
    69 184 205 252 60 94 89 122
    82 81 183 250 228 255 155 115
    58 116 44 234 93 156 38 38

actual.json and interpolant-coefficients.bin retain all256 coefficients in ascending degree order. This full interpolant is not a decoded message: every256-byte vector has one. Independent Newton interpolation with carryless polynomial arithmetic equals the moment-derived interpolant exactly; re-evaluation reproduces all256 original bytes.

## Exact format and checks

This is a nonsystematic evaluation code: the hypothetical224-byte message would be coefficients a0..a223, not the first224 input bytes. Multiplication uses the fixed polynomial basis modulo0x11d; x is the unchanged byte index. No route, basis, primitive polynomial, dimension, length, offset or point-order alternative was tested. No error-location/correction attempt was included.

For the unique degree<=255 interpolant f, set S_k=Σ over all256 field elements of f(x)x^k, k0..31, with x^0=1 also at zero. Characteristic2 makes the constant power sum256=0; positive power sums vanish unless the exponent is a multiple of255, when they equal1. Since the maximum relevant exponent is286, S_k=a_(255−k). Thus the32 checks are exactly the32 forbidden high coefficients, not heuristic redundancy scores. The actual degree255 already fails the first check; all remaining checks were nevertheless calculated and retained.

## Controls and implementation checks

All65,536 products from the log/antilog arithmetic agree with independently written carryless product plus explicit polynomial division. Generator2 visits all255 nonzero bytes before returning to1; all255 inverses multiply to1. Gaussian elimination confirms the32×256 parity matrix has rank32.

Seven frozen224-byte messages (zero, constant1, monomial degree223 and four seeded random vectors) encode correctly. For each, moment interpolation and separate Newton divided differences both recover the exact224 coefficients plus32 zeros, and all256 independent evaluations match. All256 single-byte xor1 corruptions and256 cyclic-adjacent double-byte xor1/xor2 corruptions of the first random codeword fail the complete32-check test. Exact detection also follows from the root bound: a nonzero degree<=223 polynomial cannot vanish at more than223 of256 distinct points, so this code's minimum distance is33.

Controls and every corrupted codeword/check vector are preserved in controls.json; no favorable fixtures were selected after the actual result. Standard logger records controls0.797s and actual0.136s, both exit0, one thread. No external field package, install, English scorer or key search was used.

## Interpretation and scope

The proposed error-corrected output role was speculative, motivated by the exact256-byte length. R08's inspected binary.py covered cipher/decompression/JSON formats; a narrow ledger/source check found no equivalent full-field evaluation test. This is not an exhaustive assertion about all historical work.

The miss excludes only this exact undamaged basis/order/degree format. It says nothing decisive about other Reed–Solomon conventions, shorter codes, field representations, permutations, messages or damaged codewords. The high interpolant degree does not establish encryption or randomness. No second variant was attempted after the miss.
