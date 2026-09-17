# S16 provenance wording clarification

Review55 correctly distinguishes copied and referenced maps. S16-result.json stores every word's rune array and every rotation inequality, but full word_map objects (raw positions, source-character positions and lines) only for the four cycle-witness words. Other complete maps remain in the hash-pinned F06-maps.json input. The report's sentence about full original word maps refers to the four certificate words, not all words. This clarification changes no computation, result, certificate or input.
