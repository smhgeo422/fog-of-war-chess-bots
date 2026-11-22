"""P2-v1: online opponent style inference from observable EVENT equivalence classes.

The unknown opponent action is a retrospective label only; updates marginalize
it over all compatible actions and worlds, rather than training on hidden action
as if observed online. The style experts are explicit feature policies.
"""
from __future__ import annotations
import math
import random


def probs(scores, temperature=1):
    if not scores or temperature <= 0:
        raise ValueError("need nonempty scores and positive temperature")
    m = max(scores)
    e = [math.exp((v - m) / temperature) for v in scores]
    z = sum(e)
    return [v / z for v in e]


def expert(action_features, style):
    """Observation-computable features for candidate legal actions."""
    if style not in ("capture", "quiet", "pressure"):
        raise ValueError("unknown style")
    if style == "capture":
        return probs([2.5 * a["capture"] + 0.4 * a["promotion"]
                      for a in action_features])
    if style == "quiet":
        return probs([-2.0 * a["capture"] + 0.4 * a["development"]
                      for a in action_features])
    return probs([1.5 * a["pressure"] + 0.5 * a["capture"]
                  for a in action_features])


def marginal_event_likelihood(styles, actions, events, observed, belief, rho,
                              epsilon=0.04):
    """Each world admits its own action set / observation equivalence classes."""
    if not 0 < epsilon < 1 or len(actions) != len(events) or len(actions) != len(belief):
        raise ValueError("invalid belief/event table")
    if any(len(a) != len(e) or not a for a, e in zip(actions, events)):
        raise ValueError("each world needs one event per legal action")
    z = sum(belief)
    if z <= 0 or any(w < 0 for w in belief):
        raise ValueError("invalid belief weights")
    likelihoods = {style: 0.0 for style in styles}
    for world_actions, world_events, w in zip(actions, events, belief):
        for style in styles:
            policy = expert(world_actions, style)
            n = len(policy)
            likelihoods[style] += w / z * sum(
                (epsilon / n + (1 - epsilon) * probability)
                for event, probability in zip(world_events, policy)
                if event == observed
            )
    # When every style says an observation is impossible, do not claim the
    # hidden move was revealed or fabricate a posterior change.
    if all(l == 0 for l in likelihoods.values()):
        return dict(zip(styles, rho)), likelihoods, False
    weights = [p * max(1e-12, likelihoods[name]) for name, p in zip(styles, rho)]
    norm = sum(weights)
    return dict(zip(styles, (w / norm for w in weights))), likelihoods, True


def adapt(prior, posterior, shrink=0.02):
    if not 0 <= shrink < 1:
        raise ValueError("invalid shrink factor")
    return {k: (1 - shrink) * posterior[k] + shrink * prior[k] for k in prior}


def predict(style_weights, candidates, epsilon=0.04):
    styles = tuple(style_weights)
    n = len(candidates)
    if not n or abs(sum(style_weights.values()) - 1) > 1e-8:
        raise ValueError("invalid mixture")
    mixed = [epsilon / n] * n
    for name in styles:
        p = expert(candidates, name)
        for j in range(n):
            mixed[j] += (1 - epsilon) * style_weights[name] * p[j]
    if abs(sum(mixed) - 1) > 1e-9 or min(mixed) <= 0:
        raise ValueError("non-normalized, collapsed opponent policy")
    return mixed


def trial(seed=719):
    rng = random.Random(seed)
    actions = [
        {"capture": 1.0, "promotion": 0.0, "development": 0.0, "pressure": 1.0},
        {"capture": 0.0, "promotion": 0.0, "development": 1.0, "pressure": 0.0},
        {"capture": 0.0, "promotion": 0.0, "development": 0.0, "pressure": 1.0},
    ]
    names = ("capture", "quiet", "pressure")
    prior = {k: 1.0 / len(names) for k in names}
    # Synthetic opponent is capture-biased on the first game and quiet-biased
    # on the second. Only the event, never its action index, updates the style.
    expected, uniform_nll, online_nll = [], [], []
    unchanged_marginal = True
    events = ["captured", "unseen", "unseen"]
    for truth in ("capture", "quiet"):
        rho = prior.copy()
        actual = expert(actions, truth)
        for _ in range(90):
            j = rng.choices(range(3), actual, k=1)[0]
            # Offline action NLL is a retrospective scoring label, NOT update data.
            online_nll.append(-math.log(predict(rho, actions)[j]))
            uniform_nll.append(math.log(3))
            posterior, _, updated = marginal_event_likelihood(
                names, [actions], [events], events[j], [1.0],
                [rho[k] for k in names],
            )
            if not updated:
                raise ValueError("observable event incorrectly impossible")
            rho = adapt(prior, posterior)
        expected.append({"true_style": truth, "posterior": rho})
    # Two invisible moves may have different hidden meanings but SAME event.
    ep1, _, _ = marginal_event_likelihood(
        names, [actions], [events], "unseen", [1], list(prior.values()))
    ep2, _, _ = marginal_event_likelihood(
        names, [actions], [events], "unseen", [1], list(prior.values()))
    unchanged_marginal = ep1 == ep2
    return {"primary_metric": "retrospective action NLL, toy observation-only event updates",
            "online_mean_nll": sum(online_nll) / len(online_nll),
            "uniform_mean_nll": sum(uniform_nll) / len(uniform_nll),
            "n_actions_retrospectively_scored": len(online_nll),
            "event_alias_invariance": unchanged_marginal,
            "posterior_by_true_style": expected,
            "limitations": "Toy features/styles; actual opponent legal actions and opponent view uncertain in live FoW. No public protocol reveals these hidden actions."}
