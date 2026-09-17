#!/usr/bin/env python3
"""Exact best-score literal-F decoding for a FIXED key and a local score.

This is an independent research prototype, not a Liber Primus solution.
It makes no file or network requests. Run:
    python3 literal_f_exact_dp.py --selftest

Model:
* An ordinary rune emits (cipher + sign * key[position]) mod 29.
* An observed ciphertext F (index 0) may instead emit F without consuming key.
* The score is additive and depends only on the previous two emitted tokens.
* Optional boundary tokens (29) occur at fixed, supplied positions.
* The key is either periodic or a fixed, finite sequence.
* There is NO key-skip rejection filter and NO plaintext-feedback key generation.

It returns one maximum-scoring plaintext and one associated path. Equal-score
alternatives are NOT all retained, and no uniqueness claim follows. Exactness is
for this supplied scoring objective, not for the intended plaintext. A production
n-best implementation needs additional backpointer/tie handling.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import itertools
import math
import random
from typing import Callable, Iterable, Sequence

ALPHABET_SIZE = 29
BOUNDARY = 29
ScoreStep = Callable[[tuple[int, int], int], float]


@dataclass(frozen=True)
class DecodeResult:
    score: float
    plaintext: tuple[int, ...]
    literal_positions: tuple[int, ...]
    consumed: int
    max_live_states: int
    expansions: int


def _validate_runes(values: Sequence[int], label: str) -> tuple[int, ...]:
    vals = tuple(values)
    if any(type(x) is not int or not 0 <= x < ALPHABET_SIZE for x in vals):
        raise ValueError(f"{label} must contain integers in 0..28")
    return vals


def decode_exact(
    ciphertext: Sequence[int],
    key: Sequence[int],
    score_step: ScoreStep,
    *,
    sign: int = -1,
    periodic: bool = True,
    start: int = 0,
    ends: Iterable[int] = (),
) -> DecodeResult:
    """Find the exact optimum over legal literal-F decisions.

    At fixed input position, future scores depend only on the key phase/position
    and two-token score context. Paths with identical states can therefore merge.
    This property does NOT hold for an arbitrary whole-text neural score.
    """
    c = _validate_runes(ciphertext, "ciphertext")
    k = _validate_runes(key, "key")
    if not k:
        raise ValueError("key must not be empty")
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError("sign must be -1 or 1")
    if type(start) is not int or start < 0:
        raise ValueError("start must be a nonnegative integer")
    if not periodic and start > len(k):
        raise ValueError("finite key start is past its end")
    boundaries = frozenset(ends)
    if any(type(i) is not int or not 0 <= i < len(c) for i in boundaries):
        raise ValueError("boundary positions must refer to input runes")

    # state -> (score, plaintext, literal positions, number of consumed key values)
    # Tuples keep this demonstration clear; scalable code should use backpointers.
    initial_pos = start % len(k) if periodic else start
    states = {(initial_pos, (BOUNDARY, BOUNDARY)): (0.0, (), (), 0)}
    peak = 1
    expansions = 0
    for i, observed in enumerate(c):
        new = {}
        for (pos, context), (score, plain, path, used) in states.items():
            alternatives = []
            if periodic or pos < len(k):
                emitted = (observed + sign * k[pos]) % ALPHABET_SIZE
                next_pos = (pos + 1) % len(k) if periodic else pos + 1
                alternatives.append((emitted, next_pos, False))
            if observed == 0:
                alternatives.append((0, pos, True))
            for emitted, next_pos, literal in alternatives:
                expansions += 1
                increment = float(score_step(context, emitted))
                if not math.isfinite(increment):
                    raise ValueError("score_step must return finite numeric scores")
                value = score + increment
                new_context = (context[1], emitted)
                if i in boundaries:
                    increment = float(score_step(new_context, BOUNDARY))
                    if not math.isfinite(increment):
                        raise ValueError("score_step must return finite numeric scores")
                    value += increment
                    new_context = (new_context[1], BOUNDARY)
                state = (next_pos, new_context)
                candidate = (
                    value, plain + (emitted,),
                    path + (i,) if literal else path,
                    used + (not literal),
                )
                # Equal-score ties retain one representative, not proof of uniqueness.
                if state not in new or value > new[state][0]:
                    new[state] = candidate
        if not new:
            raise ValueError(f"no legal path survives at rune {i}; key may be exhausted")
        states = new
        peak = max(peak, len(states))
    best = max(states.values(), key=lambda item: item[0])
    return DecodeResult(best[0], best[1], best[2], best[3], peak, expansions)


def _exhaustive(c, key, step, sign, periodic, start, ends):
    # Deliberately retains every path and uses absolute key consumption.
    states = [(0.0, (), (), 0)]
    for i, observed in enumerate(c):
        next_states = []
        for score, plain, path, used in states:
            pos = start + used
            choices = []
            if periodic or pos < len(key):
                choices.append(((observed + sign * key[pos % len(key)]) % 29, False))
            if observed == 0:
                choices.append((0, True))
            for emitted, literal in choices:
                # Reconstruct context from the full retained history.
                tokens = [BOUNDARY, BOUNDARY]
                for j, rune in enumerate(plain):
                    tokens.append(rune)
                    if j in ends:
                        tokens.append(BOUNDARY)
                context = tuple(tokens[-2:])
                value = score + step(context, emitted)
                if i in ends:
                    value += step((context[1], emitted), BOUNDARY)
                next_states.append((
                    value, plain + (emitted,), path + (i,) if literal else path,
                    used + (not literal),
                ))
        states = next_states
    return states


def selftest() -> dict:
    rng = random.Random(9172026)
    weights = {t: -rng.random() * 9 for t in itertools.product(range(30), repeat=3)}
    step = lambda context, emitted: weights[context + (emitted,)]
    checked = 0
    total_paths = 0
    peak = 0
    for case in range(300):
        length = rng.randrange(1, 13)
        periodic = bool(case % 2)
        key_length = rng.randrange(1, 7) if periodic else length + 3
        key = [rng.randrange(29) for _ in range(key_length)]
        start = rng.randrange(3)
        c = [0 if rng.random() < .6 else rng.randrange(1, 29) for _ in range(length)]
        ends = {i for i in range(length) if rng.random() < .2}
        sign = (-1, 1)[(case // 2) % 2]
        exhaustive = _exhaustive(c, key, step, sign, periodic, start, ends)
        got = decode_exact(c, key, step, sign=sign, periodic=periodic, start=start, ends=ends)
        best_score = max(row[0] for row in exhaustive)
        assert math.isclose(got.score, best_score, rel_tol=0, abs_tol=1e-10)
        assert any(
            row[1] == got.plaintext and row[2] == got.literal_positions
            and row[3] == got.consumed for row in exhaustive
        )
        checked += 1
        total_paths += len(exhaustive)
        peak = max(peak, got.max_live_states)
    # This exact known rule retains an F without consuming the first key value.
    fixture = decode_exact([0, 4, 8], [1, 2], lambda ctx, x: 1.0 if x == 0 else 0.0,
                           periodic=False)
    assert fixture.plaintext == (0, 3, 6) and fixture.literal_positions == (0,)
    assert fixture.consumed == 2
    return {
        "random_cases_passed": checked,
        "exhaustive_paths_checked": total_paths,
        "maximum_live_dp_states_in_test": peak,
        "finite_key_fixture_passed": True,
        "scope": "Synthetic exact-objective checks; no puzzle or language-model validation.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if not args.selftest:
        parser.error("Use --selftest, or import decode_exact from your audit code.")
    import json
    print(json.dumps(selftest(), indent=2))
