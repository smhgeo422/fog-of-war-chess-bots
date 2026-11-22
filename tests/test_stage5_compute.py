from unittest.mock import patch

import chess
import fow  # noqa: F401 (puts starter on sys.path)
import pytest
import referee
from tools.stage4.compute import _marginal_voc
from tools.stage5.compute import _allocate, _interval, _scores, _trace
from uniform_random import ObservationTracker


def test_v2_retains_stage4_raw_voc_and_penalizes_leave_one_variability():
    initial = [(0.6, 0.4)] * 3 + [(0.25, 0.75)]
    decisions = _scores(initial)
    _, stage4_gain = _marginal_voc(initial)
    assert decisions["voc_raw"] == pytest.approx(stage4_gain)
    assert 0 < decisions["voc_v2"] < decisions["voc_raw"]
    assert decisions["voc_jackknife_se"] > 0


def test_all_arms_use_same_fixed_quota_and_v2_ranks_shrunk_values():
    rows = [{"voc_raw": i, "voc_v2": 8 - i, "initial_margin": i, "v1_eligible": i > 4}
            for i in range(8)]
    arms = _allocate(rows, 75101, "holdout")
    assert all(len(slots) == 2 for slots in arms.values())
    assert arms["v2_shrunk_voc"] == {0, 1}
    assert arms["raw_voc_rank"] == {6, 7}
    assert arms["v1_threshold_matched"] <= {5, 6, 7}
    assert arms == _allocate(rows, 75101, "holdout")


def test_engine_reference_disjoint_and_selection_does_not_read_later_scores():
    start = referee.FowBoard()
    states = []
    for move in referee.fow_moves(start):
        board = start.copy(stack=False)
        board.push(move)
        states.append(board)
    view = referee.observation(states[0], chess.BLACK)
    assert all(referee.observation(state, chess.BLACK) == view for state in states)
    tracker = ObservationTracker(chess.BLACK)
    tracker.observe(referee.observation(start, chess.BLACK))
    tracker.observe(view)
    row = {"sample_id": "controlled-001", "ply": 1, "online_inputs": {
        "side": "black", "view": view, "own_history_sha256": "0" * 64,
        "legal_attempts": sorted(move.uci() for move in tracker.legal_moves()),
    }}
    obtained = []

    def capture(initial):
        obtained.extend(initial)
        return {"voc_raw": 0, "voc_v2": 0, "initial_margin": 0, "v1_eligible": False}

    with patch("tools.stage5.compute._scores", capture):
        trace, reason = _trace(row, states, 75101, 1, lambda board, move: (0.1, 256))
    assert reason is None
    assert obtained == [root["values"] for root in trace["initial_roots"]]
    tested = {root["root_sha256"] for root in trace["initial_roots"]}
    tested.add(trace["extra_root"]["root_sha256"])
    reference = {root["root_sha256"] for root in trace["reference_roots"]}
    assert len(tested) == 5 and len(reference) >= 6 and tested.isdisjoint(reference)
    assert trace["initial_nodes"] == 4 * 4 * 256
    assert trace["extra_nodes"] == 4 * 256


def test_regret_uncertainty_keeps_pair_numbers_separate_across_seeds():
    rows = [{"corpus_seed": 75101, "pair": 1}, {"corpus_seed": 75102, "pair": 1}]
    contrast = _interval(rows, [-0.25, 0.5])
    assert contrast["pairs"] == 2
    assert contrast["better_pairs"] == contrast["worse_pairs"] == 1
    assert contrast["delta"] == pytest.approx(0.125)
