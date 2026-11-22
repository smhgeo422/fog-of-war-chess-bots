"""P3-v1: exact contingent two-step policy over future observation histories.

Clairvoyant search selects a different action in each true world. This planner
chooses only one action per indistinguishable information set. The transition
rows and leaf values are externally supplied, so this kernel neither assumes
true hidden state is known at play-time nor computes new Stockfish values.
"""
from __future__ import annotations
from collections import defaultdict
from math import isfinite


def contingent(transitions):
    """Row: (mass, observation, public_history, {action: utility}).

    World-specific action sets are intersected within each information set;
    otherwise an impossible move in one world would falsely count as a legal
    contingent plan. The game model may deliberately include actual FoW
    "attempt" actions that can fail, as permitted by the referee.
    """
    if not transitions:
        raise ValueError("nonempty future world outcomes required")
    groups = defaultdict(list)
    mass_total = 0.0
    for weight, view, history, utilities in transitions:
        if not isfinite(weight) or weight <= 0 or not utilities:
            raise ValueError("positive finite mass and legal actions required")
        if any(not isfinite(v) for v in utilities.values()):
            raise ValueError("finite continuation utilities required")
        if not isinstance(view, str) or not isinstance(history, str):
            raise ValueError("observation/history key must be explicit strings")
        groups[(view, history)].append((weight, utilities))
        mass_total += weight
    total_contingent = total_clairvoyant = 0.0
    policy = {}
    for key, rows in groups.items():
        candidate = set.intersection(*(set(u) for _, u in rows))
        if not candidate:
            raise ValueError("no common feasible FoW attempt in information set")
        best = max(candidate, key=lambda action:
                   (sum(w * u[action] for w, u in rows), action))
        policy["|".join(key)] = best
        total_contingent += sum(w * u[best] for w, u in rows)
        total_clairvoyant += sum(w * max(u.values()) for w, u in rows)
    q = total_contingent / mass_total
    q_clair = total_clairvoyant / mass_total
    if q > q_clair + 1e-10:
        raise AssertionError("strategy-fusion upper bound violated")
    return {"contingent_value": q, "clairvoyant_value": q_clair,
            "fusion_gap": q_clair - q, "policy": policy,
            "information_sets": len(groups), "worlds": len(transitions)}


def choose_root(root_transitions, fallback=None, max_cost=None):
    """Root move tables are precomputed by the unchanged leaf evaluator.

    An exhausted research budget returns the baseline's root move; zero/negative
    budget cannot secretly buy extra Stockfish calls.
    """
    if not root_transitions:
        raise ValueError("empty root table")
    if max_cost is not None and max_cost <= 0:
        if fallback not in root_transitions:
            raise ValueError("baseline fallback unavailable")
        return {"root_move": fallback, "timed_out": True}
    estimates = {move: contingent(rows) for move, rows in root_transitions.items()}
    best = max(sorted(estimates), key=lambda move: estimates[move]["contingent_value"])
    return {"root_move": best, "timed_out": False,
            "by_move": estimates, "baseline": fallback}


def trial(seed=719):
    import random
    rng = random.Random(seed)
    # Same future observation, opposite perfect-information best responses.
    ambiguous = [(0.5, "same-view", "public-prefix", {"a": 1.0, "b": 0.0}),
                 (0.5, "same-view", "public-prefix", {"a": 0.0, "b": 1.0})]
    now_distinct = [(0.5, "view-left", "public-prefix", {"a": 1.0, "b": 0.0}),
                    (0.5, "view-right", "public-prefix", {"a": 0.0, "b": 1.0})]
    a = contingent(ambiguous)
    b = contingent(now_distinct)
    assert abs(a["contingent_value"] - 0.5) < 1e-12
    assert abs(a["fusion_gap"] - 0.5) < 1e-12
    assert abs(b["fusion_gap"]) < 1e-12
    # A competing root has lower clairvoyant score but higher realizable value.
    other = [(0.5, "common", "public-prefix", {"a": 0.7, "b": 0.6}),
             (0.5, "common", "public-prefix", {"a": 0.7, "b": 0.6})]
    root = choose_root({"optimistic": ambiguous, "robust": other}, fallback="optimistic")
    assert root["root_move"] == "robust"
    # Changed public-history information can forbid an invalid alias merge.
    differ = [(0.5, "same-view", "past-A", {"a": 1, "b": 0}),
              (0.5, "same-view", "past-B", {"a": 0, "b": 1})]
    assert contingent(differ)["fusion_gap"] == 0
    timeout = choose_root({"optimistic": ambiguous, "robust": other},
                          fallback="optimistic", max_cost=0)
    assert timeout["root_move"] == "optimistic" and timeout["timed_out"]
    return {"primary_metric": "reduction in strategy-fusion optimism on exact toy worlds",
            "ambiguous_clairvoyant": a["clairvoyant_value"],
            "ambiguous_feasible": a["contingent_value"],
            "ambiguous_fusion_gap": a["fusion_gap"],
            "distinct_observation_fusion_gap": b["fusion_gap"],
            "root_changed": root["root_move"] != "optimistic",
            "test_repetitions": 1,
            "rng_seed": rng.randint(0, 1_000_000),
            "limitations": "Leaf tables are synthetic and no Stockfish/equal-CPU FoW game result is claimed."}
