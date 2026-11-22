"""P5-v1: independently calibrated selective hidden-material hazard.

Risk estimation is a probability model, not a global "avoid fog" coefficient.
Training labels are retrospective; at decision-time the key is constructed from
observation-derived action type and geometry only. The Bayesian estimate has
an explicit Beta prior and reports held-out Brier loss by move class.
"""
from __future__ import annotations
import math
import random


CATEGORIES = ("quiet-exposed", "quiet-sheltered", "capture", "king-exposed")


def calibrate(rows, prior_strength=6.0, prior_rate=0.25):
    """Rows: (online-category, retrospective-event-label); labels are never features."""
    if prior_strength <= 0 or not 0 < prior_rate < 1:
        raise ValueError("invalid shrinkage prior")
    count = {name: 0 for name in CATEGORIES}
    events = {name: 0 for name in CATEGORIES}
    for category, label in rows:
        if category not in count or label not in (0, 1):
            raise ValueError("unapproved category or nonbinary event")
        count[category] += 1
        events[category] += label
    prior_a = prior_strength * prior_rate
    return {name: (prior_a + events[name]) / (prior_strength + count[name])
            for name in CATEGORIES}


def predict(calibration, category):
    if category not in CATEGORIES or category not in calibration:
        raise ValueError("missing category probability")
    p = calibration[category]
    if not 0 <= p <= 1 or not math.isfinite(p):
        raise ValueError("invalid risk probability")
    return p


def brier(rows, predictor):
    if not rows:
        raise ValueError("no evaluation rows")
    grouped = {name: [] for name in CATEGORIES}
    for category, label in rows:
        p = predictor(category)
        grouped[category].append((p - label) ** 2)
    total = sum(sum(x) for x in grouped.values())
    return {"overall": total / len(rows),
            "by_class": {cat: sum(loss) / len(loss) if loss else None
                         for cat, loss in grouped.items()},
            "counts": {cat: len(loss) for cat, loss in grouped.items()}}


def calibrated_utility(base_nonterminal, king_capture_p, category, risk_model,
                       loss_scale=0.22):
    """King loss is terminal; hidden material hazard is separate conditional risk.

    The calibrator is an *incremental* quiet-move diagnostic. Captures are not
    penalized by a generic visibility coefficient: fog captures can profit.
    """
    if not -1 <= base_nonterminal <= 1 or not 0 <= king_capture_p <= 1:
        raise ValueError("bad expected utility")
    if loss_scale < 0:
        raise ValueError("negative penalty")
    material_hazard = predict(risk_model, category) if category != "capture" else 0.0
    return -king_capture_p + (1.0 - king_capture_p) * (
        base_nonterminal - loss_scale * material_hazard)


def trial(seed=719):
    rng = random.Random(seed)
    truth = {
        "quiet-exposed": 0.62, "quiet-sheltered": 0.07,
        "capture": 0.14, "king-exposed": 0.78,
    }
    train, holdout = [], []
    for name in CATEGORIES:
        for i in range(150):
            label = int(rng.random() < truth[name])
            (train if i < 100 else holdout).append((name, label))
    rng.shuffle(train)
    model = calibrate(train)
    model_loss = brier(holdout, lambda name: predict(model, name))
    constant = sum(y for _, y in train) / len(train)
    null_loss = brier(holdout, lambda name: constant)
    assert all(0 < p < 1 for p in model.values())
    assert predict(model, "quiet-exposed") > predict(model, "quiet-sheltered")
    assert model_loss["overall"] < null_loss["overall"]
    assert calibrated_utility(0.8, 0.03, "quiet-exposed", model) < (
        calibrated_utility(0.8, 0.03, "quiet-sheltered", model))
    # No indiscriminate anti-capture penalty.
    assert abs(calibrated_utility(0.8, 0.0, "capture", model) - 0.8) < 1e-12
    return {"primary_metric": "held-out Brier of selective hidden-material-loss event",
            "calibrated_brier": model_loss,
            "constant_brier": null_loss["overall"],
            "model": model,
            "n_train": len(train), "n_holdout": len(holdout),
            "no_capture_penalty": True,
            "limitations": "Synthetic label mechanism is known and may favor this model; no referee-derived held-out hazard labels or game result yet."}
