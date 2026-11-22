from copy import deepcopy

import chess

from tools.stage2_corpus import play
from tools.stage4.compute import _continuation, _exact_histories, _marginal_voc, _p8
from bots.eBotI.eBotI.belief import state_key


def test_own_belief_history_ignores_hidden_opponent_action():
    replay, _, _ = play("fixture", 7106, 1, 0, "train", "uniform", "visible_capture")
    frames = replay["frames"][:3]
    corrupted = deepcopy(frames)
    corrupted[2]["move"] = "hidden, not a usable UCI"
    signature = lambda source: [(ply, [state_key(s) for s in states]) for ply, states
                               in _exact_histories(source, chess.WHITE, "fixture", 2)]
    assert signature(frames) == signature(corrupted)
    assert len(signature(frames)) == 1


def test_p7_retrospective_truth_is_neither_feature_nor_baseline():
    replay, observations, labels = play("fixture", 7106, 1, 0, "train", "uniform", "visible_capture")
    _, states = next(_exact_histories(replay["frames"][:3], chess.WHITE, "fixture", 2))
    row = observations[2]
    label = labels[2]
    score = lambda board, move: (0.125, 17)
    record = _continuation(replay, row, label, states, 1, score)
    assert record is not None
    assert _continuation(replay, row, label | {"truth_board_fen": "tampered"}, states,
                         1, score) == record
    assert record.baseline == 0.125
    assert record.nodes == 17 * record.roots


def test_p8_empirical_voc_can_use_extra_root_for_ambiguous_decision():
    spend, tied_gain = _marginal_voc([(0.8, 0.0), (0.0, 0.8)] * 2)
    skip, clear_gain = _marginal_voc([(0.8, 0.0), (0.7, 0.1)] * 2)
    assert spend and tied_gain > 0.001
    assert not skip and clear_gain == 0


def test_p8_random_control_matches_root_evaluations_and_reports_engine_nodes():
    rows = [
        {"pair": i + 1, "adapt": i == 0, "regret_initial": float(i),
         "regret_extra": 0.0, "initial_nodes": 1000, "extra_nodes": 256 + i}
        for i in range(6)
    ]
    audit = _p8({"holdout": rows})["split_results"]["holdout"]
    assert audit["n"] == 6
    assert audit["extra_slots_each"] == 1
    assert audit["root_evaluations_each"] == 25
    assert audit["actual_reported_engine_nodes"]["adaptive"] == 6256
    assert sum(r["fixed_extra"] for r in audit["decisions"]) == 1
