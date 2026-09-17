# Q07-edformat — two complete record-array formats fail

The cached corrected256-byte object is not either of the two frozen rawpackings: eight normalgenerated Ed25519publickeys, or four normalgenerated Ed25519signatures. Nooffset/reversal/curve/search variants were tried. The input SHA256 remains3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290; no newimage50inspection occurred.

At fixed32-byte boundaries, only offsets0and128 canonically decode to curvepoints; onlyoffset0 lies in the prime-order subgroup. The other six blocks have nonsquare reconstructed x². At allfour64-byte signature boundaries, S is outside the canonical scalar range, independently sufficient to reject each standardgenerated signature. Completecoordinates, subgroup multiples and integer scalars are retained in actual.json.

The first32-byte block passing a point/subgroup check is not a candidate: the complete prescribedformat fails, and a randomblock can pass that necessary check. No message/signature/publickey relationship was verified. No arbitrary prefix/header format was introduced after observing this partialacceptance. Encryptedobjects, privatekeybytes, othercurves/packings and unrelatedcryptographicmaterial remain outside these narrow results.

Controls: the firsttwo public RFC8032 Ed25519vectors match installedcryptography keygeneration/signing/verification; eightadditional explicitlypublic deterministic testseeds generate valid points/signatures. Separate scalar affineEdwards arithmetic checks allsubgroup conditions. Noncanonical y, noncanonical zero-x sign, order2torsion and S=grouporder are correctly rejected. Tenpositive/fournegative cases pass beforeactual. CompleteRFCsource/retrievalhash/UTC, generatedfixtures, libraryversion and rawlogs retained. RFC2017 supplies format definitions and postdates thepuzzle; it is not historicaltoolchain evidence.

Run controls-and-actual PASS.668s. This is necessaryformatverification, not an attack on keys or a signature-verification result for thepuzzle. Narrowpriorinspection distinguished R08compression/JSON/AES/RC4, P16GF256code andR06bitmap tests; no universal novelty claim. Existingdeadline unchanged.
