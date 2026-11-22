"""Nine separate first-version algorithmic probes; explicit falsification tests.

Passing this suite shows mathematical and implementation sanity on toy data,
not game strength, inference validity against strong opponents, or FoW arena
compatibility. The unchanged frozen v4 reference is tested separately.
"""
from __future__ import annotations
import importlib
import json
import math
from pathlib import Path
import sys

import pytest

MODULES = [f"P{i}" for i in range(1, 10)]


@pytest.mark.parametrize("project", MODULES)
def test_each_first_version_is_executable_and_has_scientific_limitations(project):
    algorithm = importlib.import_module("tools.stage3." + project)
    result = algorithm.trial(7106)
    assert isinstance(result, dict)
    assert result.get("primary_metric")
    assert isinstance(result.get("limitations"), str) and len(result["limitations"]) > 50
    # A limitation is a substantive scope statement, not a required magic word.
    assert not result.get("claim_strength", False)


@pytest.mark.parametrize("project", MODULES)
def test_each_first_version_is_deterministic(project):
    algorithm = importlib.import_module("tools.stage3." + project)
    assert algorithm.trial(7106) == algorithm.trial(7106)


def test_p1_support_preserved_and_bad_weights_rejected():
    from tools.stage3 import P1
    p, q = P1.proposal([0.999, 0.001], [0, 1], 0.40)
    assert all(a > 0 and b > 0 for a, b in zip(p, q))
    assert math.isclose(sum(q), 1.0)
    with pytest.raises(ValueError):
        P1.proposal([1, -1], [0, 1])
    with pytest.raises(ValueError):
        P1.proposal([1, 0], [0, 1], 1)
    with pytest.raises(ValueError):
        P1.sample([1], [1], 0, 0.3, 7)


def test_p1_checks_prior_history_not_just_last_observation():
    import fow
    import chess
    import referee
    from tools.stage3 import P1
    board = referee.FowBoard()
    start = referee.observation(board, chess.WHITE)
    board.push_uci("e2e4")
    end = referee.observation(board, chess.WHITE)
    assert P1.history_consistent(referee.FowBoard().fen(), [start, end], ["e2e4"], chess.WHITE)
    assert not P1.history_consistent(referee.FowBoard().fen(), ["?" * 64, end],
                                     ["e2e4"], chess.WHITE)


def test_p2_hidden_action_cannot_replace_observable_event():
    from tools.stage3 import P2
    actions = [[{"capture": 1, "promotion": 0, "development": 0, "pressure": 0},
                {"capture": 0, "promotion": 0, "development": 0, "pressure": 1}]]
    # The event 'silent' merges *both* possible hidden actions.
    events = [["silent", "silent"]]
    names = ("capture", "quiet", "pressure")
    prior = [1 / 3] * 3
    post, likelihood, observed = P2.marginal_event_likelihood(
        names, actions, events, "silent", [1], prior)
    assert observed
    assert all(abs(p - 1 / 3) < 1e-10 for p in post.values())
    assert all(abs(x - 1.0) < 1e-10 for x in likelihood.values())


def test_p2_probabilities_have_positive_floor():
    from tools.stage3 import P2
    moves = [{"capture": 1, "promotion": 0, "development": 0, "pressure": 0},
             {"capture": 0, "promotion": 0, "development": 1, "pressure": 0}]
    model = {"capture": 1, "quiet": 0, "pressure": 0}
    odds = P2.predict(model, moves)
    assert min(odds) > 0 and sum(odds) == pytest.approx(1.0)


def test_p3_ambiguous_hidden_worlds_cannot_select_separate_actions():
    from tools.stage3 import P3
    cases = [(1, "view", "public", {"A": 1, "B": 0}),
             (1, "view", "public", {"A": 0, "B": 1})]
    out = P3.contingent(cases)
    assert out["clairvoyant_value"] == 1
    assert out["contingent_value"] == 0.5
    assert len(out["policy"]) == 1


def test_p3_disjoint_feasibility_rejected_and_budget_fallback():
    from tools.stage3 import P3
    bad = [(0.5, "same", "past", {"A": 1}),
           (0.5, "same", "past", {"B": 1})]
    with pytest.raises(ValueError, match="common feasible"):
        P3.contingent(bad)
    assert P3.choose_root({"base": [(1, "same", "past", {"A": 0})]},
                          fallback="base", max_cost=0)["timed_out"]


def test_p4_entropy_not_substitute_for_decision_value():
    from tools.stage3 import P4
    cases = [(0.5, "one", {"A": 1, "B": 0}),
             (0.5, "two", {"A": 1, "B": 0})]
    result = P4.value_of_information(cases)
    assert result["future_view_count"] == 2
    assert result["instrumental_voi"] == 0.0


def test_p4_rejects_different_direct_payoffs():
    from tools.stage3 import P4
    toy = [(1, "view", {"A": 1})]
    with pytest.raises(ValueError, match="differ tactically"):
        P4.evaluate_root_actions({"a": toy, "b": toy}, {"a": 0, "b": 0.1})


def test_p5_selective_capture_not_blanket_penalty():
    from tools.stage3 import P5
    model = P5.calibrate([("quiet-exposed", 1), ("quiet-sheltered", 0)])
    assert P5.calibrated_utility(0.4, 0, "capture", model) == 0.4
    assert P5.calibrated_utility(0.4, 0.1, "quiet-exposed", model) < (
        P5.calibrated_utility(0.4, 0.1, "quiet-sheltered", model))
    with pytest.raises(ValueError):
        P5.calibrate([("posthoc_hidden_king", 1)])


def test_p6_exploitability_certificate_rejects_pure_mixed_game():
    from tools.stage3 import P6
    matrix = [[1, -1], [-1, 1]]
    pure = P6.certificate(matrix, [1, 0], [1, 0])
    mixed = P6.certificate(matrix, [0.5, 0.5], [0.5, 0.5])
    assert pure["exploitability_gap"] == 2
    assert mixed["exploitability_gap"] == 0
    assert mixed["row_security_value"] == 0


def test_p7_no_retrospective_target_or_policy_allowed_in_model_features():
    from tools.stage3 import P7
    good = {"side": "white", "view": "?" * 64,
            "own_history_sha256": "0" * 64, "legal_attempts": ["e2e4"],
            "visible_enemy_count": 0, "visible_square_count": 0}
    assert len(P7.featurize(good)) == 4
    with pytest.raises(ValueError, match="predecision"):
        P7.featurize({**good, "selected_action": "e2e4"})
    with pytest.raises(ValueError, match="predecision"):
        P7.featurize({**good, "truth_board_fen": "forbidden"})
    with pytest.raises(ValueError, match="predecision"):
        P7.featurize({**good, "opponent_policy": "capture"})


def test_p8_requires_bayesian_mean_consistency_and_reserve():
    from tools.stage3 import P8
    with pytest.raises(ValueError, match="martingale"):
        P8.value_of_computation({"a": 0.5, "b": 0.5},
                                [(1, {"a": 0.6, "b": 0.5})], 0.1, 0)
    tie = [(0.5, {"a": 0.8, "b": 0.2}), (0.5, {"a": 0.2, "b": 0.8})]
    assert P8.select({"a": 0.5, "b": 0.5},
                     {"one": {"duration": 0.5, "outcomes": tie}},
                     0.55, 0.1)["decision"] == "stop"


def test_p9_rejects_one_action_per_hidden_state_and_adversary_escape():
    from tools.stage3 import P9
    nodes = {
        "h1": {"view": "?", "actions": {"A": ["win"], "B": ["loss"]}},
        "h2": {"view": "?", "actions": {"A": ["loss"], "B": ["win"]}},
    }
    assert not P9.certify(nodes, ["h1", "h2"], 1)["certified_winning"]
    with pytest.raises(ValueError, match="distinct observations"):
        P9.certify({**nodes, "h2": {"view": "different", "actions": nodes["h2"]["actions"]}},
                   ["h1", "h2"], 1)


def test_stage3_tracked_job_runner_preserves_independent_evidence(tmp_path):
    from tools.offline_jobs.stage3 import run_job
    run = tmp_path / "actions-150-1"
    run.mkdir()
    (run / "manifest.json").write_text(json.dumps({
        "project_id": "P3", "variant": "v1", "purpose": "research",
        "seed": 719, "run_id": run.name,
    }))
    run_job(run, 719)
    metrics = json.loads((run / "metrics.json").read_text())
    index = json.loads((run / "results/algorithm_metadata.json").read_text())
    assert metrics["status"] == "complete" and not metrics["claim_strength"]
    assert index["project_id"] == "P3"
    assert "module_sha256" in index
    assert (run / "data_split.json").is_file()
    assert (run / "notes.md").is_file()
