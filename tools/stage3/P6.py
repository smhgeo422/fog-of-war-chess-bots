"""P6-v1: independent restricted zero-sum regret-matching+ oracle.

This is a finite normal-form local game for solver correctness; it does NOT
implement a full extensive-form FoW CFR resolver or certify global safety.
Deep cached leaf values and infoset feasibility belong in later variants.
"""
from __future__ import annotations
import math


def strategy(regrets):
    positive = [max(0.0, r) for r in regrets]
    z = sum(positive)
    return [r / z for r in positive] if z > 1e-14 else [1 / len(regrets)] * len(regrets)


def payoff(matrix, row, col):
    return sum(row[i] * col[j] * matrix[i][j]
               for i in range(len(row)) for j in range(len(col)))


def certificate(matrix, row, col):
    value = payoff(matrix, row, col)
    best_row = max(sum(matrix[i][j] * col[j] for j in range(len(col)))
                   for i in range(len(row)))
    worst_col = min(sum(row[i] * matrix[i][j] for i in range(len(row)))
                    for j in range(len(col)))
    gap = best_row - worst_col
    if gap < -1e-9:
        raise AssertionError("zero-sum duality contradiction")
    return {"value": value, "max_row_deviation": best_row - value,
            "max_col_deviation": value - worst_col, "exploitability_gap": max(0, gap),
            "row_security_value": worst_col}


def solve(matrix, iterations=5000):
    if not matrix or not matrix[0] or type(iterations) is not int or iterations < 1:
        raise ValueError("invalid local game")
    m, n = len(matrix), len(matrix[0])
    if any(len(row) != n or any(not math.isfinite(x) for x in row) for row in matrix):
        raise ValueError("finite rectangular zero-sum matrix required")
    row_regrets, col_regrets = [0.0] * m, [0.0] * n
    row_sum, col_sum = [0.0] * m, [0.0] * n
    trace = []
    for t in range(1, iterations + 1):
        x, y = strategy(row_regrets), strategy(col_regrets)
        for i in range(m):
            row_sum[i] += t * x[i]
        for j in range(n):
            col_sum[j] += t * y[j]
        row_pay = [sum(matrix[i][j] * y[j] for j in range(n)) for i in range(m)]
        col_pay = [sum(x[i] * matrix[i][j] for i in range(m)) for j in range(n)]
        value = sum(x[i] * row_pay[i] for i in range(m))
        row_regrets = [max(0.0, r + a - value)
                       for r, a in zip(row_regrets, row_pay)]
        col_regrets = [max(0.0, r + value - a)
                       for r, a in zip(col_regrets, col_pay)]
        if t in (10, 100, 500, 1000, iterations):
            total = t * (t + 1) / 2
            c = certificate(matrix, [v / total for v in row_sum],
                            [v / total for v in col_sum])
            trace.append({"iteration": t, "gap": c["exploitability_gap"]})
    total = iterations * (iterations + 1) / 2
    x = [v / total for v in row_sum]
    y = [v / total for v in col_sum]
    return {"row_policy": x, "col_policy": y,
            "certificate": certificate(matrix, x, y),
            "gap_trace": trace, "iterations": iterations}


def trial(seed=719):
    matching = [[1.0, -1.0], [-1.0, 1.0]]
    rps = [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]]
    one = solve(matching, 6000)
    two = solve(rps, 6000)
    # Pure deterministic strategy has security value -1; equilibrium mixes.
    assert one["certificate"]["exploitability_gap"] < 0.08, one
    assert two["certificate"]["exploitability_gap"] < 0.10, two
    assert abs(one["certificate"]["value"]) < 0.08
    assert abs(one["row_policy"][0] - 0.5) < 0.08
    assert one["certificate"]["row_security_value"] > -0.2
    assert certificate(matching, [1, 0], [1, 0])["row_security_value"] == -1
    return {"primary_metric": "exact best-response exploitability gap, zero-sum toy games",
            "matching_pennies": one, "rock_paper_scissors": two,
            "pure_policy_worst_case": -1.0,
            "limitations": "Correct normal-form local solver only; no FoW infosets, blueprint safety guarantees, or Stockfish leaf cost yet."}
