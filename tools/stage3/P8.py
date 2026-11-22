"""P8-v1: one-step rational metareasoning for root-evaluation computation.

This allocates *compute*, not board observations (P4), and keeps the chess
evaluator fixed. VOC is an expectation over hypothetical computation results.
Every computation has explicit wall cost, conservative safety reserve, and
shadow price for future clock opportunity.
"""
from __future__ import annotations
import math


def value_of_computation(current, outcomes, duration, price):
    """outcomes: [(probability, {action: posterior_mean_after_call}), ...].

    Bayesian consistency matters: expected updated action values must equal
    current estimates; otherwise VOI is being spuriously manufactured.
    """
    if not current or duration <= 0 or price < 0 or not outcomes:
        raise ValueError("invalid computation or budget")
    if any(not math.isfinite(v) for v in current.values()):
        raise ValueError("nonfinite current score")
    z = sum(p for p, _ in outcomes)
    if abs(z - 1) > 1e-10:
        raise ValueError("outcome probabilities must sum to one")
    for p, means in outcomes:
        if p < 0 or set(means) != set(current):
            raise ValueError("invalid posterior action set")
    for a, old in current.items():
        if abs(sum(p * v[a] for p, v in outcomes) - old) > 1e-9:
            raise ValueError("violated posterior mean martingale")
    before = max(current.values())
    after = sum(p * max(means.values()) for p, means in outcomes)
    gain = after - before
    if gain < -1e-9:
        raise AssertionError("nonnegative expected value of information violated")
    return {"expected_decision_gain": max(0.0, gain),
            "duration": duration, "clock_shadow_cost": price * duration,
            "net_voc": gain - price * duration}


def select(current, computations, remaining_seconds, reserve_seconds,
           price=0.03, overhead=0.0):
    """One-step controller: choose best positive-VOC next computation, or stop.

    All candidate computations are explicit and have stated real wall cost.
    No extra compute is allowed when it would violate the hard safety reserve.
    """
    if reserve_seconds < 0 or remaining_seconds < reserve_seconds or overhead < 0:
        raise ValueError("invalid clock state")
    if overhead > 0.05 * max(1e-12, remaining_seconds - reserve_seconds):
        return {"decision": "stop", "reason": "controller-overhead-budget", "budget_left": remaining_seconds}
    best = None
    for name, proposal in computations.items():
        duration = proposal["duration"]
        if duration + overhead + reserve_seconds > remaining_seconds:
            continue
        detail = value_of_computation(current, proposal["outcomes"], duration, price)
        if best is None or detail["net_voc"] > best[1]["net_voc"]:
            best = (name, detail)
    if best is None or best[1]["net_voc"] <= 0:
        return {"decision": "stop", "reason": "not-worth-future-clock-cost",
                "budget_left": remaining_seconds}
    return {"decision": "compute", "computation": best[0],
            "detail": best[1], "budget_left": remaining_seconds -
            best[1]["duration"] - overhead}


def trial(seed=719):
    clear = {"safe": 0.8, "risky": 0.1}
    tie = {"left": 0.5, "right": 0.5}
    # Observing symmetric noisy estimates on an already decisive position
    # cannot reverse the root decision, hence no decision value.
    clear_out = [(0.5, {"safe": 0.82, "risky": 0.08}),
                 (0.5, {"safe": 0.78, "risky": 0.12})]
    tie_out = [(0.5, {"left": 0.65, "right": 0.35}),
               (0.5, {"left": 0.35, "right": 0.65})]
    a = value_of_computation(clear, clear_out, 0.5, 0.03)
    b = value_of_computation(tie, tie_out, 0.5, 0.03)
    assert a["expected_decision_gain"] < 1e-10
    assert b["expected_decision_gain"] > 0.14
    skip = select(clear, {"sample": {"duration": 0.5, "outcomes": clear_out}}, 2, 0.6)
    more = select(tie, {"sample": {"duration": 0.5, "outcomes": tie_out}}, 2, 0.6)
    blocked = select(tie, {"sample": {"duration": 0.5, "outcomes": tie_out}}, 0.9, 0.6)
    assert skip["decision"] == "stop"
    assert more["decision"] == "compute" and more["budget_left"] >= 0.6
    assert blocked["decision"] == "stop"
    return {"primary_metric": "exact toy marginal decision VOC under a fixed shadow price",
            "decisive_gain": a["expected_decision_gain"],
            "near_tie_gain": b["expected_decision_gain"],
            "decisive_stops": skip["decision"] == "stop",
            "near_tie_computes": more["decision"] == "compute",
            "hard_reserve_respected": blocked["decision"] == "stop",
            "limitations": "Analytic computation-outcome model, not calibrated Stockfish node/wall-time benefit or full game clock."}
