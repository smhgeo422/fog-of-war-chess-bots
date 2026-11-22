"""P4-v1: decision-focused value of information under action-matched conditions.

Unlike the P3 policy correction, this measures what a ROOT intervention on
information flow buys when its immediate tactical payoff is held fixed. It
does not use entropy or square count as a proxy for instrumental utility.
"""
from __future__ import annotations
from collections import defaultdict
from math import isfinite


def value_of_information(worlds):
    """Worlds (mass, observed_next_view, {future_action: continuation_utility}).

    All future actions must be legal in all unresolved hidden worlds for the
    uninformed comparator. The informed policy uses one feasible action per
    future observation group; its advantage is the instrumental benefit.
    """
    if not worlds:
        raise ValueError("no possible continuation worlds")
    denom = 0.0
    groups = defaultdict(list)
    all_actions = None
    for p, obs, values in worlds:
        if p <= 0 or not isfinite(p) or not values or any(
                not isfinite(v) for v in values.values()):
            raise ValueError("invalid outcome probability or utility")
        actions = set(values)
        all_actions = actions if all_actions is None else all_actions & actions
        groups[obs].append((p, values))
        denom += p
    if not all_actions:
        raise ValueError("need legal common actions to compare equal feasible decisions")
    # Baseline: commit to one continuation without receiving further information.
    base = max(sum(p * values[action] for p, _, values in worlds)
               for action in sorted(all_actions)) / denom
    informed = 0.0
    policies = {}
    for obs, rows in groups.items():
        valid = set.intersection(*(set(v) for _, v in rows))
        best = max(sorted(valid),
                   key=lambda action: sum(p * values[action] for p, values in rows))
        policies[obs] = best
        informed += sum(p * values[best] for p, values in rows)
    informed /= denom
    return {"uninformed_value": base, "informed_value": informed,
            "instrumental_voi": max(0.0, informed - base),
            "future_view_count": len(groups), "future_policy": policies}


def evaluate_root_actions(roots, direct, beta=1.0):
    """Matched-root study: compare only roots sharing a direct payoff, avoiding
    material/king-risk double-counting. P3 Q must NOT also contain VOI here."""
    if not roots or set(roots) != set(direct) or not 0 <= beta <= 1:
        raise ValueError("invalid matched root actions")
    if max(direct.values()) - min(direct.values()) > 1e-9:
        raise ValueError("root actions differ tactically: VOI not identifiable")
    detail = {a: value_of_information(worlds) for a, worlds in roots.items()}
    selection = max(sorted(detail), key=lambda a:
                    direct[a] + beta * detail[a]["instrumental_voi"])
    return {"selected": selection, "direct": direct,
            "information_only": detail, "beta": beta}


def trial(seed=719):
    # Two root moves reveal the SAME number of squares; only one changes
    # which future defensive action should be taken. All immediate payoffs 0.
    informative = [(0.5, "enemy-fork-left", {"defend-L": 1.0, "defend-R": 0.0}),
                   (0.5, "enemy-fork-right", {"defend-L": 0.0, "defend-R": 1.0})]
    irrelevant = [(0.5, "empty-a", {"defend-L": 0.5, "defend-R": 0.4}),
                  (0.5, "empty-b", {"defend-L": 0.5, "defend-R": 0.4})]
    noinfo = [(0.5, "unknown", {"defend-L": 1.0, "defend-R": 0.0}),
              (0.5, "unknown", {"defend-L": 0.0, "defend-R": 1.0})]
    direct = {"reveals-relevant": 0.0, "reveals-empty": 0.0}
    root = evaluate_root_actions(
        {"reveals-relevant": informative, "reveals-empty": irrelevant}, direct)
    yes = value_of_information(informative)
    no = value_of_information(irrelevant)
    blind = value_of_information(noinfo)
    assert abs(yes["instrumental_voi"] - 0.5) < 1e-12
    assert no["instrumental_voi"] == 0.0
    assert blind["instrumental_voi"] == 0.0
    assert root["selected"] == "reveals-relevant"
    return {"primary_metric": "decision-focused VOI on matched immediate-tactic toy actions",
            "relevant_voi": yes["instrumental_voi"],
            "irrelevant_voi": no["instrumental_voi"],
            "unobservable_voi": blind["instrumental_voi"],
            "same_square_count_not_a_proxy": yes["instrumental_voi"] > no["instrumental_voi"],
            "avoids_p3_double_counting": True,
            "limitations": "Exact toy continuation tables only; opponent information denial requires later independent experiment."}
