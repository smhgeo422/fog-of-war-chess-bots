"""P1-v1: support-preserving threat-stratified importance sampling.

This module changes only WHICH legal posterior states get leaf evaluations.
It does not create/reconstruct histories or alter the original posterior.
Any history-consistency failure must be rejected upstream. The returned weights
correct proposal bias; ESS is an explicit diagnostic, not a success metric.
"""
from __future__ import annotations
import bisect
import math
import random


def normalize(weights):
    if not weights or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError("finite nonnegative posterior weights required")
    total = sum(weights)
    if not total > 0:
        raise ValueError("posterior must have positive mass")
    return [float(w) / total for w in weights]


def proposal(posterior, danger, alpha=0.3, floor=1e-3):
    p = normalize(posterior)
    if len(p) != len(danger) or not 0 <= alpha < 1 or floor <= 0:
        raise ValueError("bad threat proposal configuration")
    if any(not math.isfinite(d) or d < 0 for d in danger):
        raise ValueError("danger must be finite and nonnegative")
    # The threat proposal deliberately puts extra mass on rare dangerous worlds.
    # The EPS floor is only a proposal device, not a posterior mutation.
    r = normalize([min(10.0, d) + floor for d in danger])
    q = [(1 - alpha) * a + alpha * b for a, b in zip(p, r)]
    if any(a > 0 and b <= 0 for a, b in zip(p, q)):
        raise ValueError("proposal lost posterior support")
    return p, q


def sample(posterior, danger, draws, alpha, seed):
    if type(draws) is not int or draws <= 0:
        raise ValueError("positive integral root count required")
    p, q = proposal(posterior, danger, alpha)
    cdf = []
    for v in q:
        cdf.append((cdf[-1] if cdf else 0.0) + v)
    rng = random.Random(seed)
    indices = [min(len(q) - 1, bisect.bisect_right(cdf, rng.random()))
               for _ in range(draws)]
    importance = [p[i] / q[i] for i in indices]
    total = sum(importance)
    ess = (total * total / sum(w * w for w in importance)) if total else 0.0
    return {"indices": indices, "importance": importance, "ess": ess,
            "posterior": p, "proposal": q, "alpha": alpha}


def expected_event(events, sampled):
    if len(events) != len(sampled["posterior"]):
        raise ValueError("event array must match posterior support")
    if not events or any(not 0 <= e <= 1 for e in events):
        raise ValueError("bounded event indicator required")
    numer = sum(events[i] * w for i, w in zip(sampled["indices"], sampled["importance"]))
    denom = sum(sampled["importance"])
    if denom <= 0:
        raise ValueError("no effective posterior samples")
    return numer / denom


def history_consistent(initial_fen, observed_views, own_actions, side):
    """Existential single legal history: rule-out a complete-board path conflicting
    with an earlier observation. This does NOT generate additional belief worlds.
    """
    import fow  # noqa: F401, load repo referee
    import chess
    import referee
    if len(observed_views) != len(own_actions) + 1:
        raise ValueError("need one initial observation and one per own move")
    board = referee.FowBoard(initial_fen)
    for view, action in zip(observed_views, own_actions):
        if referee.observation(board, side) != view:
            return False
        move = chess.Move.from_uci(action)
        if move not in referee.fow_moves(board):
            return False
        board.push(move)
    return referee.observation(board, side) == observed_views[-1]


def trial(seed=719):
    # This toy has known truth: one rare hidden-king-attack state.
    p = [0.749, 0.24, 0.01, 0.001]
    event = [0, 0, 1, 1]
    danger = [0, 0.1, 1, 1]
    true_risk = sum(a * e for a, e in zip(p, event))
    estimates = {}
    for alpha in (0.0, 0.30):
        vals, ess = [], []
        for i in range(250):
            s = sample(p, danger, 64, alpha, seed + i)
            vals.append(expected_event(event, s))
            ess.append(s["ess"])
        estimates[str(alpha)] = {
            "mse": sum((x - true_risk) ** 2 for x in vals) / len(vals),
            "mean": sum(vals) / len(vals),
            "mean_ess": sum(ess) / len(ess),
            "sample_count": len(vals),
        }
    p0, q0 = proposal(p, danger, 0.30)
    assert abs(sum(q0) - 1.0) < 1e-10
    assert min(q0) > 0
    assert len(set(sample(p, danger, 32, 0.3, seed)["indices"])) >= 1
    return {"primary_metric": "MSE against exact rare-event posterior",
            "exact_risk": true_risk, "proposal_results": estimates,
            "importance_weights_checked": True,
            "not_full_history_reconstruction": True,
            "limitations": "Toy four-state support only; no held-out chess posterior, no playing-strength inference."}
