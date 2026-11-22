import math

from tools import stage2_corpus
from tools.stage4 import replay

import chess
import referee


def test_replay_policy_forecasts_do_not_depend_on_later_observation():
    board = referee.FowBoard("4k3/8/8/8/3p4/2P5/8/K7 w - - 0 1")
    support = [replay.World(board, 1.0)]
    visible_events = []
    for action in ("c3d4", "c3c4"):
        board.push_uci(action)
        visible_events.append(referee.observation(board, chess.BLACK))
        board.pop()
    assert visible_events[0] != visible_events[1]
    first, first_support, _, confirmed = replay.opponent_forecast(
        support, chess.BLACK, replay.STYLE_PRIOR, visible_events[0],
    )
    second, second_support, _, second_confirmed = replay.opponent_forecast(
        support, chess.BLACK, replay.STYLE_PRIOR, visible_events[1],
    )
    assert confirmed and second_confirmed
    assert first == second
    assert all(first["action"]["online"][move] > 0 for move in ("c3d4", "c3c4"))
    assert all(math.isclose(sum(distribution.values()), 1)
               for methods in first.values() for distribution in methods.values())
    assert {world.board.fen() for world in first_support}.isdisjoint(
        world.board.fen() for world in second_support
    )


def test_material_label_needs_real_hidden_undefended_capture():
    board = referee.FowBoard("3r3k/8/8/8/3B4/8/8/K7 b - - 0 1")
    move = chess.Move.from_uci("d8d4")
    view = referee.observation(board, chess.WHITE)
    assert view[move.from_square] == "?"
    assert replay.retrospective_material_loss(board, move, view)
    assert not replay.retrospective_material_loss(board, chess.Move.from_uci("d8d5"), view)
    visible = view[:move.from_square] + "r" + view[move.from_square + 1:]
    assert not replay.retrospective_material_loss(board, move, visible)
    board.set_piece_at(chess.D1, chess.Piece(chess.ROOK, chess.WHITE))
    assert not replay.retrospective_material_loss(board, move, view)


def test_material_classifier_uses_only_view_including_en_passant_attempt():
    board = referee.FowBoard("7k/8/8/3pP3/8/8/8/K7 w - d6 0 1")
    view = referee.observation(board, chess.WHITE)
    move = chess.Move.from_uci("e5d6")
    assert view[move.to_square] == "-"
    assert replay.move_category(view, chess.WHITE, move) == "capture"


def test_screen_forecasts_on_referee_generated_game_and_censors_last_move():
    game = {"game_id": "s2-025-ab", "split": "holdout", "pair_block": 25}
    fixture, rows, labels = stage2_corpus.play(
        game["game_id"], 7106, game["pair_block"], 0, game["split"], "uniform", "visible_capture",
    )
    belief, style, _ = replay.early_replay(game, fixture, rows, labels)
    assert belief and all(row["truth_supported"] for row in belief)
    assert style and all(row["online_action_nll"] > 0 for row in style)
    material, censored = replay.material_rows(game, fixture, rows, labels)
    assert len(material) == len(rows) - 1
    assert sum(censored.values()) == 1
    assert set(material[-1]).isdisjoint({"truth_board_fen", "selected_action", "view"})
    score = replay.cluster_summary(belief, "threat_proposal", "posterior_draw")
    assert score["complete_pairs"] == 0
    assert score["delta_95_paired_block_bootstrap"] is None
