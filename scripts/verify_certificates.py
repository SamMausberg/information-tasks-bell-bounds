#!/usr/bin/env python3
"""Exact finite checks for 'From information tasks to exclusivity and Bell bounds'.

Run with Python 3.10+ and SymPy. No network, floating-point optimization, or
external data is used. These checks supplement, not formalize, the task proofs.
An AssertionError identifies a failed certificate and gives a nonzero exit code.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product

try:
    import sympy as sp
except ImportError as exc:
    raise SystemExit("SymPy is required: install the dependency in requirements.txt") from exc

BITS = (0, 1)
Event = tuple[tuple[int, ...], tuple[int, ...]]  # (outputs, settings)


def orthogonal_witnesses(first: Event, second: Event) -> list[int]:
    """Return 1-based parties with the same setting and opposite outcomes."""
    o, x = first
    p, y = second
    return [i + 1 for i in range(4) if x[i] == y[i] and o[i] != p[i]]


def check_event_certificates() -> None:
    counts: Counter[Event] = Counter()
    parity_counts: Counter[tuple[int, int, int]] = Counter()
    for t, c, d, k in product(BITS, repeat=4):
        events: list[Event] = []
        parity_counts[t, c, d] += 1
        for x, a, b in product(BITS, repeat=3):
            xp, y, yp = x ^ t, k, k ^ 1 ^ c ^ d
            gamma = (c, d)[x]
            ap = a ^ 1 ^ gamma
            bp = b ^ 1 ^ gamma ^ (x * y) ^ (xp * yp)
            event = ((a, b, ap, bp), (x, y, xp, yp))
            events.append(event)
            counts[event] += 1
            assert (a ^ b ^ (x * y)) == (ap ^ bp ^ (xp * yp))
            assert a ^ ap == 1 ^ gamma  # Opposite to the added parity record.
            # Invert the generator, including the component not indexed by x.
            recovered_t, recovered_k = x ^ xp, y
            recovered_gamma = 1 ^ a ^ ap
            gamma_other = recovered_gamma ^ 1 ^ y ^ yp
            recovered_cd = (recovered_gamma, gamma_other) if x == 0 else (gamma_other, recovered_gamma)
            assert (recovered_t, *recovered_cd, recovered_k) == (t, c, d, k)
        assert len(events) == len(set(events)) == 8
        assert all(orthogonal_witnesses(e, f) for e, f in combinations(events, 2))
    target = {
        ((a, b, ap, bp), (x, y, xp, yp))
        for a, b, ap, bp, x, y, xp, yp in product(BITS, repeat=8)
        if a ^ b ^ (x * y) == ap ^ bp ^ (xp * yp)
    }
    assert set(counts) == target and set(counts.values()) == {1}
    assert len(counts) == 128 and set(parity_counts.values()) == {2}
    assert len(parity_counts) == 8
    print("PASS: 16 contexts; 448 fine-event pairs locally exclusive; 128 pairs covered once; 8 parity records counted twice.")

    strings = [("0000", "0000"), ("0011", "0100"), ("0111", "1101"), ("1100", "1010"), ("1110", "0011")]
    five = [(tuple(map(int, o)), tuple(map(int, x))) for o, x in strings]
    claimed = [3, 3, 2, 1, 2, 4, 1, 1, 4, 3]
    for (e, f), witness in zip(combinations(five, 2), claimed):
        assert witness in orthogonal_witnesses(e, f)
    for (a, b, ap, bp), (x, y, xp, yp) in five:
        assert a ^ b == x * y and ap ^ bp == xp * yp

    weights = {(a, b, x, y): (1 + (-1) ** (a + b + x * y) * Fraction(81, 100)) / 4
               for a, b, x, y in product(BITS, repeat=4)}
    for x, y in product(BITS, repeat=2):
        assert sum(weights[a, b, x, y] for a, b in product(BITS, repeat=2)) == 1
        for a in BITS:
            assert sum(weights[a, b, x, y] for b in BITS) == Fraction(1, 2)
        for b in BITS:
            assert sum(weights[a, b, x, y] for a in BITS) == Fraction(1, 2)
    chsh = sum((-1) ** (a + b + x * y) * w for (a, b, x, y), w in weights.items())
    excess = sum(weights[a, b, x, y] * weights[ap, bp, xp, yp]
                 for (a, b, ap, bp), (x, y, xp, yp) in five) - 1
    assert chsh == Fraction(81, 25) and excess == Fraction(761, 32000)
    assert excess / 5 == Fraction(761, 160000)
    assert excess / 10 == Fraction(761, 320000)
    assert (chsh**2 - 8) / 4 == Fraction(1561, 2500)
    assert (chsh**2 - 8) / 288 == Fraction(1561, 180000)
    print("PASS: five-event excess 761/32000; CHSH 81/25; all associated rational thresholds.")

    b, e, kappa, h, delta = sp.symbols("B e kappa h delta")
    lhs = (2 + b / 2)**2 + (2 - b / 2)**2 + 4 - 2 * e - 16 - 144 * kappa
    assert sp.expand(lhs - (b**2 - 8 - 4 * e - 288 * kappa) / 2) == 0
    assert sp.expand((288 * kappa).subs(kappa, 2 * h + 2 * delta)) == 576 * (h + delta)
    print("PASS: residual polynomial; coefficients 4, 288, and finite-frequency coefficient 576.")


def check_frequency_certificates() -> None:
    copies = sp.symbols("L", positive=True, integer=True)
    center = (copies + 1) / (4 * copies)
    left = center**2
    right = (sp.Rational(1, 2) - center)**2 + 1 / (4 * copies)
    assert sp.simplify(left - right) == 0
    assert sp.limit(left, copies, sp.oo) == sp.Rational(1, 16)
    q, f = sp.symbols("q f", real=True)
    expression = (q - f)**2 + q * (1 - q) / copies
    assert sp.simplify(sp.diff(expression, q, 2) - 2 * (1 - 1 / copies)) == 0
    for count in range(1, 6):
        probs = sp.symbols(f"p0:{count}")
        direct = 0
        for bits in product(BITS, repeat=count):
            weight = sp.prod(p if bit else 1 - p for p, bit in zip(probs, bits))
            direct += weight * (sp.Rational(sum(bits), count) - f)**2
        mean = sum(probs) / count
        formula = (mean - f)**2 + sum(p * (1 - p) for p in probs) / count**2
        assert sp.expand(direct - formula) == 0
    print("PASS: symbolic minimax equalizer ((L+1)/(4L))^2, limit 1/16, endpoint convexity, variance expansion for L=1,...,5.")


def check_quantum_certificates() -> None:
    eye = sp.eye(2)
    x = sp.Matrix([[0, 1], [1, 0]])
    y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    z = sp.diag(1, -1)
    kron = sp.kronecker_product
    hadamard = (x + z) / sp.sqrt(2)
    assert sp.simplify(hadamard * z * hadamard) == x
    assert sp.simplify(hadamard * x * hadamard) == z
    for c0, c1 in [(kron(z, z), kron(x, x)), (kron(z, x), kron(x, z))]:
        projectors = [(sp.eye(4) + (-1)**c * c0) * (sp.eye(4) + (-1)**d * c1) / 4
                      for c, d in product(BITS, repeat=2)]
        assert sum(projectors, sp.zeros(4)) == sp.eye(4)
        assert all(p.trace() == 1 and p * p == p for p in projectors)
        assert all(p * q == sp.zeros(4) for p, q in combinations(projectors, 2))
    cnot = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    decoder = kron(hadamard, eye) * cnot
    assert sp.simplify(decoder.T * kron(z, eye) * decoder) == kron(x, x)
    assert sp.simplify(decoder.T * kron(eye, z) * decoder) == kron(z, z)
    phi = sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)
    correlations = [sp.simplify((phi.T * kron(a, b) * phi)[0])
                    for a, b in product([z, x], [(z + x) / sp.sqrt(2), (z - x) / sp.sqrt(2)])]
    assert correlations == [sp.sqrt(2) / 2] * 3 + [-sp.sqrt(2) / 2]
    tilted = (3 * z + 4 * x) / 5
    commutator = kron(z, z) * kron(tilted, tilted) - kron(tilted, tilted) * kron(z, z)
    assert commutator == 24 * sp.I * (kron(eye, y) + kron(y, eye)) / 25
    assert max((commutator.conjugate().T * commutator).eigenvals()) == sp.Rational(48, 25)**2
    print("PASS: aligned/crossed qubit projectors, CHSH 2 sqrt(2), Bell decoder, tilted commutator norm 48/25.")

    plus = sp.Matrix([1, 1]) / sp.sqrt(2)
    support = kron(eye, plus)
    p_support = support * support.T
    sum_projs = [sp.diag(1, 0, 0, 0), sp.diag(0, 1, 1, 0), sp.diag(0, 0, 0, 1)]
    r = sp.symbols("r", real=True)
    rho = kron(sp.diag(r, 1 - r), plus * plus.T)
    assert [(rho * p).trace() for p in sum_projs] == [r / 2, sp.Rational(1, 2), (1 - r) / 2]
    for p in sum_projs:
        # Dimension of the intersection = rank(S)+rank(P)-rank([S P]).
        assert support.rank() + p.rank() - support.row_join(p).rank() == 0
        assert (p_support * p).rank() > 0
    kraus = []
    for a, b in product(BITS, repeat=2):
        matrix = sp.zeros(4)
        matrix[2 * a, 2 * a + b] = 1
        kraus.append(matrix)
    assert sum((k.T * k for k in kraus), sp.zeros(4)) == sp.eye(4)
    before = sp.diag(0, 1, 0, 0)
    after = sum((k * before * k.T for k in kraus), sp.zeros(4))
    compatible_effect = kron(eye, sp.diag(0, 1))
    assert (before * compatible_effect).trace() == 1
    assert (after * compatible_effect).trace() == 0
    print("PASS: Z+ frequency vector and support conditions; reset instrument trace preservation and disturbance one.")

    # New scope example: a two-level T2 sector in a three-level carrier.
    embedding = sp.Matrix([[1, 0], [0, 1], [0, 0]])
    spare = sp.Matrix([0, 0, 1])
    tx = embedding * x * embedding.T + spare * spare.T
    ty = embedding * z * embedding.T + spare * spare.T
    g = embedding * hadamard * embedding.T + spare * spare.T
    basis = [sp.Matrix([1, 0, 0]), sp.Matrix([0, 1, 0])]
    signs = [(basis[0] + basis[1]) / sp.sqrt(2), (basis[0] - basis[1]) / sp.sqrt(2)]
    project = lambda v: sp.simplify(v * v.conjugate().T)
    for a in BITS:
        assert project(tx * basis[a]) == project(basis[1 - a])
        assert project(tx * signs[a]) == project(signs[a])
        assert project(ty * signs[a]) == project(signs[1 - a])
        assert project(ty * basis[a]) == project(basis[a])
        assert project(g * basis[a]) == project(signs[a])
        assert project(g * signs[a]) == project(basis[a])
    qutrit_phi = kron(embedding, embedding) * phi
    assert project(kron(tx, tx) * qutrit_phi) == project(qutrit_phi)
    assert project(kron(ty, ty) * qutrit_phi) == project(qutrit_phi)
    local_intrinsic = embedding * eye * embedding.T / 2
    assert tx * local_intrinsic * tx.T == local_intrinsic
    bells = [kron(sp.eye(3), sp.eye(3)) * qutrit_phi,
             kron(tx, sp.eye(3)) * qutrit_phi,
             kron(ty, sp.eye(3)) * qutrit_phi,
             kron(tx * ty, sp.eye(3)) * qutrit_phi]
    frame = sum((project(v) for v in bells), sp.zeros(9))
    assert frame.rank() == 4 and frame * frame == frame
    assert frame == kron(embedding * embedding.T, embedding * embedding.T)
    residual = sp.eye(9) - frame
    assert residual.rank() == 5 and residual * kron(spare, spare) == kron(spare, spare)
    print("PASS: qutrit T2-sector embedding; R2 calibrations, R3 invariant reduced state, R4 symmetries, rank-four frame and rank-five residual.")


def check_hypersignaling() -> None:
    v = [sp.Matrix(p) for p in [(1, 0, 1), (0, 1, 1), (-1, 0, 1), (0, -1, 1)]]
    e = [sp.Matrix(p) for p in [(1, 1, 1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1)]]
    center = sp.Matrix([0, 0, 1])
    assert all(2 * center - a in v for a in v)
    for a, b in combinations(v, 2):
        assert any({(effect.T * a)[0] / 2, (effect.T * b)[0] / 2} == {0, 1} for effect in e)
    for a, b in product(v, repeat=2):
        assert 4 * center * center.T - a * b.T == (2 * center - a) * (2 * center).T + a * (2 * center - b).T
    states = [a * b.T for a, b in product(v, repeat=2)]
    effects = [a * b.T for a, b in product(e, repeat=2)]
    e23 = sp.Matrix([[-1, -1, 0], [1, -1, 0], [0, 0, 1]])
    measurement = [effects[i] / 8 for i in [0, 1, 6, 8, 10, 15]] + [e23 / 4]
    assert sum(measurement, sp.zeros(3)) == center * center.T
    assert {(state.T * e23).trace() for state in states} == {0, 2}
    assert all((state.T * effect).trace() >= 0 for state, effect in product(states, measurement))
    channel = sp.Matrix([[(states[i].T * effect).trace() for effect in measurement]
                         for i in [0, 2, 6, 7, 12, 13, 15]])
    supports = [tuple(j + 1 for j in range(7) if channel[i, j]) for i in range(7)]
    assert supports == [(1, 6), (2, 7), (2, 3), (3, 7), (4, 6), (4, 7), (5, 6)]
    assert all(channel[i, j] == sp.Rational(1, 2) for i in range(7) for j in range(7) if channel[i, j])
    payoff_matrix = sp.Matrix([
        [2, 0, 0, 0, 0, 1, 0], [0, 2, 0, 0, 0, 0, 2],
        [0, 2, 2, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0, 2],
        [0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 2, 1, 0],
    ]) / 21
    payoff = sum(payoff_matrix[i, j] * channel[i, j] for i, j in product(range(7), repeat=2))
    scores = []
    for columns in combinations(range(7), 4):
        score = sum(max(payoff_matrix[i, j] for j in columns) for i in range(7))
        scores.append(score)
        k = len(set(columns) & {1, 2, 6})
        ell = len(set(columns) & {0, 3, 4})
        b = int(5 in columns)
        assert 21 * score == [0, 4, 6, 6][k] + 2 * ell + b * (3 - ell)
    assert len(scores) == 35
    assert payoff == sp.Rational(1, 2) and max(scores) == sp.Rational(10, 21)
    assert payoff - max(scores) == sp.Rational(1, 42)
    print("PASS: HS effects, 16 product vertices, seven-input channel, all 35 classical column sets; payoff gap 1/42.")


def main() -> None:
    check_event_certificates()
    check_frequency_certificates()
    check_quantum_certificates()
    check_hypersignaling()
    print("ALL EXACT FINITE CHECKS PASSED.")
    print("The universal closure, completion, capacity, and approximation claims require the written proofs and their stated premises.")


if __name__ == "__main__":
    main()
