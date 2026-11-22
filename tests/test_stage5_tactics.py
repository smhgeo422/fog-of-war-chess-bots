"""P3 v2 selector, production wiring and fixed-fixture guards."""

from types import SimpleNamespace

import chess
import numpy as np
import pytest

from tools.stage5 import tactics
from tools.stage4.tactics import board_with_pieces
from bots.eBotI.eBotI import infoset
from bots.eBotI.eBotI.engine import JobResult
import referee


REPLY_ODDS = {"f8e8": 0.40, "f8e7": 0.24, "d4e6": 0.20, "d4b3": 0.10, "d4c2": 0.06}
LEGACY = ["f8e8", "f8e7", "d4e6"]


def position(rook="h1"):
    board = board_with_pieces({"a1": "K", rook: "R", "f8": "k", "d4": "n"})
    board.turn = chess.BLACK
    return board


def test_selector_compares_real_referee_visibility_with_same_reply_slots():
    child = position()
    fen = child.fen()
    assert infoset.select_replies(child, REPLY_ODDS, 3, chess.WHITE) == LEGACY
    assert infoset.select_replies(child, REPLY_ODDS, 3, chess.WHITE, reserve_hidden=True) == [
        "f8e8", "f8e7", "d4b3"
    ]
    assert child.fen() == fen and not child.move_stack
    covered = REPLY_ODDS | {"d4b3": 0.30}
    assert infoset.select_replies(child, covered, 3, chess.WHITE, reserve_hidden=True) == [
        "f8e8", "d4b3", "f8e7"
    ]


def test_visible_threat_and_expired_budget_preserve_legacy(monkeypatch):
    board = position("h3")
    visible_reply = {move: odds for move, odds in REPLY_ODDS.items() if move != "d4c2"}
    assert not infoset.unseen_king_reply(board, "d4b3", chess.WHITE)
    assert infoset.select_replies(board, visible_reply, 3, chess.WHITE, reserve_hidden=True) == LEGACY
    clock = iter([0, 0, 0, 0, 2])  # Deadline expires just after finding the omitted threat.
    monkeypatch.setattr(infoset, "time", SimpleNamespace(monotonic=lambda: next(clock)))
    assert infoset.select_replies(position(), REPLY_ODDS, 3, chess.WHITE,
                                  reserve_hidden=True, deadline=1) == LEGACY


class CompletePool:
    """Full deterministic tables using only legal referee moves."""

    def __init__(self):
        self.batches = []

    def ready_count(self):
        return 1

    def run(self, jobs, *_deadlines):
        self.batches.append(tuple(jobs))
        out = []
        for job in jobs:
            board = referee.FowBoard(job.fen)
            moves = referee.fow_moves(board)
            if len(self.batches) == 1:
                scores = tactics.reply_values(board, chess.WHITE)
            else:
                scores = {
                    move.uci(): tactics.payoff(tactics.add_move(board, move.uci()), chess.WHITE)
                    for move in moves
                }
            out.append(JobResult({move: {job.depth: score} for move, score in scores.items()},
                                 not moves, False))
        return out


def test_refine_flag_off_reproduces_legacy_calls_and_flag_on_wires_deadline(monkeypatch):
    own = board_with_pieces({"a1": "K", "h1": "R", "f8": "k", "d4": "n"})
    other = board_with_pieces({"a1": "K", "h1": "R", "f8": "k", "d2": "n"})
    roots = [chess.Move.from_uci("h1h2"), chess.Move.from_uci("h1h3")]
    monkeypatch.setattr(infoset, "CANDIDATES", 2)
    monkeypatch.setattr(infoset, "STATES", 2)
    monkeypatch.setattr(infoset, "REPLIES", 3)
    monkeypatch.setattr(infoset, "time", SimpleNamespace(monotonic=lambda: 0.0))

    def refine():
        pool = CompletePool()
        result = infoset.refine(pool, [own, other], [0.5, 0.5], roots, np.array([0.1, 0.2]),
                                chess.WHITE, 1.0)
        return result, pool.batches

    production = infoset.select_replies
    monkeypatch.setattr(infoset, "HIDDEN_REPLY", False)
    monkeypatch.setattr(infoset, "select_replies",
                        lambda board, odds, limit, side, **kwargs: sorted(
                            odds, key=lambda move: -odds[move])[:limit])
    expected, expected_calls = refine()
    observed = []

    def recording_selector(*args, **kwargs):
        observed.append(kwargs)
        return production(*args, **kwargs)

    monkeypatch.setattr(infoset, "select_replies", recording_selector)
    baseline, baseline_calls = refine()
    assert len(baseline_calls) == 2 and observed
    np.testing.assert_array_equal(baseline, expected)
    assert baseline_calls == expected_calls
    assert all(not call["reserve_hidden"] and call["deadline"] is None for call in observed)

    observed.clear()
    monkeypatch.setattr(infoset, "HIDDEN_REPLY", True)
    enabled, enabled_calls = refine()
    assert enabled is not None
    assert len(enabled_calls) == 2 and observed
    assert enabled_calls[0] == baseline_calls[0]
    assert len(enabled_calls[1]) == len(baseline_calls[1])
    assert all(call["reserve_hidden"] and call["deadline"] == pytest.approx(0.1)
               for call in observed)


@pytest.mark.parametrize("fixture", tactics.FIXTURES, ids=lambda fixture: fixture.name)
def test_declared_color_pair_and_shared_reply_table(fixture):
    white = tactics.fixture_case(fixture, chess.WHITE)
    black = tactics.fixture_case(fixture, chess.BLACK)
    for case in (white, black):
        assert len(case["initial_fens"]) == 2
        assert len(case["by_action"]) == 2
        for root in case["by_action"].values():
            for world in root["worlds"]:
                assert world["continuations"].keys() == world["fixed_reply_probabilities"].keys()
                assert len(world["selected"]["legacy"]) == len(world["selected"]["hidden_slot"])
    assert white["regret"] == pytest.approx(black["regret"])
    if fixture.name == "remote-knight-control":
        assert all(world["selected"]["legacy"] == world["selected"]["hidden_slot"]
                   for case in (white, black) for root in case["by_action"].values()
                   for world in root["worlds"])
