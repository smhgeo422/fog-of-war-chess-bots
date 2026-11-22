"""P3 v2 fixed-slot ablation on bounded, independent local referee fixtures."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from time import perf_counter_ns

import chess
import fow  # noqa: F401 - exposes the starter referee
import referee
from bots.eBotI.eBotI import infoset
from bots.eBotI.eBotI.evaluation import evaluate
from tools.stage4.tactics import add_move, board_with_pieces, color_uci, history_result, value


REPLY_SLOTS = 3
REPLY_RETREAT_WEIGHT = 0.08


@dataclass(frozen=True)
class Fixture:
    name: str
    extra_pieces: tuple[tuple[str, str], ...]
    attacker: str
    possible_squares: tuple[str, str]
    roots: tuple[str, str]


# The case identities, moves, equal world prior and scripted reply policy are
# fixed in source. Mirror each complete case; its colors are one paired unit.
FIXTURES = (
    Fixture("knight-fork", (("g1", "N"),), "n", ("d4", "d2"), ("h1h2", "h1h3")),
    Fixture("bishop-diagonal", (("g1", "N"),), "b", ("e1", "d2"), ("h1h2", "h1h3")),
    Fixture("rook-file", (), "r", ("d4", "e4"), ("h1h2", "h1h4")),
    Fixture("remote-knight-control", (), "n", ("f6", "g6"), ("h1h2", "h1h3")),
)


@dataclass(frozen=True)
class Continuation:
    view: str | None
    utilities: dict[str, float]
    terminal_value: float | None


def payoff(board: referee.FowBoard, side: chess.Color) -> float:
    result = history_result(board)
    return evaluate(board, side) if result is None else float(value(result, side))


def continuation(board: referee.FowBoard, side: chess.Color) -> Continuation:
    result = history_result(board)
    if result is not None:
        return Continuation(None, {}, float(value(result, side)))
    return Continuation(
        referee.observation(board, side),
        {move.uci(): payoff(add_move(board, move.uci()), side)
         for move in sorted(referee.fow_moves(board), key=chess.Move.uci)},
        None,
    )


def reply_values(child: referee.FowBoard, side: chess.Color) -> dict[str, float]:
    """Scripted quiet/retreat-biased scores, identical for all selector arms.

    The stockfish-free fixture supplies an opponent table, not an estimate
    of how a trained player would choose from the offered replies.
    """
    opponent = not side
    result = {}
    for move in sorted(referee.fow_moves(child), key=chess.Move.uci):
        rank = chess.square_rank(move.to_square)
        closeness_to_home = (7 - rank) if opponent == chess.WHITE else rank
        result[move.uci()] = (payoff(add_move(child, move.uci()), opponent)
                              + REPLY_RETREAT_WEIGHT * closeness_to_home)
    return result


def contingent_value(rows: list[tuple[float, Continuation]], *, reference: bool) -> tuple[float, float]:
    """FoW-observational and clairvoyant values on one shared payoff scale.

    The experiment retains legacy union/missing-as-loss in both ablation
    arms. The independent oracle only admits common referee-legal actions.
    This is a conservative legal policy in ambiguous worlds.
    """
    groups = defaultdict(list)
    total_contingent = total_clairvoyant = 0.0
    total_mass = 0.0
    for weight, row in rows:
        total_mass += weight
        if row.terminal_value is not None:
            total_contingent += weight * row.terminal_value
            total_clairvoyant += weight * row.terminal_value
            continue
        groups[row.view].append((weight, row.utilities))
        total_clairvoyant += weight * max(row.utilities.values())
    if total_mass <= 0:
        raise ValueError("the payoff table has no positive support")
    for members in groups.values():
        actions = [set(utilities) for _, utilities in members]
        feasible = set.intersection(*actions) if reference else set.union(*actions)
        if not feasible:
            raise ValueError("the reference observation has no common legal action")
        total_contingent += max(sum(weight * utilities.get(action, infoset.LOSS)
                                    for weight, utilities in members)
                                for action in sorted(feasible))
    return total_contingent / total_mass, total_clairvoyant / total_mass


def world_reply_rows(child: referee.FowBoard, side: chess.Color) -> dict:
    """One complete referee table, shared by oracle, legacy and v2 arms."""
    scores = reply_values(child, side)
    odds = infoset._reply_odds(scores)
    table = {reply: continuation(add_move(child, reply), side) for reply in odds}
    picks, select_ns = {}, {}
    for name, enabled in (("legacy", False), ("hidden_slot", True)):
        started = perf_counter_ns()
        picks[name] = infoset.select_replies(child, odds, REPLY_SLOTS, side, reserve_hidden=enabled)
        select_ns[name] = perf_counter_ns() - started
    assert len(picks["legacy"]) == len(picks["hidden_slot"]) == min(REPLY_SLOTS, len(odds))
    hidden = {reply for reply in odds if infoset.unseen_king_reply(child, reply, side)}
    return {"child_fen": child.fen(), "scores": scores, "odds": odds, "rows": table,
            "picks": picks, "hidden": hidden, "selection_ns": select_ns}


def aggregate(worlds: list[dict], arm: str) -> tuple[float, float]:
    rows = []
    for world in worlds:
        odds = world["odds"]
        selected = list(odds) if arm == "oracle" else world["picks"][arm]
        denominator = sum(odds[reply] for reply in selected) * len(worlds)
        rows.extend((odds[reply] / denominator, world["rows"][reply]) for reply in selected)
    return contingent_value(rows, reference=(arm == "oracle"))


def leaf_count(world, arm):
    return sum(world["rows"][reply].terminal_value is None for reply in world["picks"][arm])


def fixture_case(fixture: Fixture, side: chess.Color) -> dict:
    pieces = {"a1": "K", "h1": "R", "f8": "k", **dict(fixture.extra_pieces)}
    boards = [board_with_pieces({**pieces, square: fixture.attacker})
              for square in fixture.possible_squares]
    if side == chess.BLACK:
        boards = [board.mirror() for board in boards]
    views = {referee.observation(board, side) for board in boards}
    if len(views) != 1 or any(history_result(board) for board in boards):
        raise ValueError(f"{fixture.name} must have one active initial observation")

    by_action = {}
    for raw_action in fixture.roots:
        action = color_uci(raw_action, side)
        children = [add_move(board, action) for board in boards]
        if any(history_result(child) for child in children):
            raise ValueError(f"{fixture.name} must have active reply positions")
        worlds = [world_reply_rows(child, side) for child in children]
        initial = mean(evaluate(child, side) for child in children)
        exact, clairvoyant = aggregate(worlds, "oracle")
        arms = {}
        for arm in ("legacy", "hidden_slot"):
            feasible, optimistic = aggregate(worlds, arm)
            reply_slots = sum(len(world["picks"][arm]) for world in worlds)
            arms[arm] = {
                "root_score": initial + (feasible - optimistic),
                "observational_value_on_selected_rows": feasible,
                "clairvoyant_value_on_selected_rows": optimistic,
                "selected_reply_slots": reply_slots,
                "nonterminal_leaf_slots": sum(leaf_count(world, arm) for world in worlds),
                "unseen_threat_probability_mass_retained": mean(
                    sum(world["odds"][reply] for reply in world["picks"][arm]
                        if reply in world["hidden"]) for world in worlds
                ),
            }
        by_action[action] = {
            "base_one_ply_value": initial,
            "oracle_observation_consistent_value": exact,
            "oracle_clairvoyant_value": clairvoyant,
            "arbiter_arms": arms,
            "nonterminal_leaf_slots_matched": all(
                leaf_count(world, "legacy") == leaf_count(world, "hidden_slot") for world in worlds
            ),
            "worlds": [{
                "after_root_fen": world["child_fen"],
                "fixed_reply_scores": world["scores"],
                "fixed_reply_probabilities": world["odds"],
                "unseen_king_attack_replies": sorted(world["hidden"]),
                "selected": world["picks"],
                "selection_ns": world["selection_ns"],
                "continuations": {reply: {"view": row.view, "utilities": row.utilities,
                                           "terminal_value": row.terminal_value}
                                  for reply, row in world["rows"].items()},
            } for world in worlds],
        }

    selected = {arm: max(by_action, key=lambda action: by_action[action]["arbiter_arms"][arm]["root_score"])
                for arm in ("legacy", "hidden_slot")}
    best = max(row["oracle_observation_consistent_value"] for row in by_action.values())
    regret = {arm: best - by_action[action]["oracle_observation_consistent_value"]
              for arm, action in selected.items()}
    matched = all(row["nonterminal_leaf_slots_matched"] for row in by_action.values())
    return {"family": fixture.name, "side": chess.COLOR_NAMES[side],
            "initial_fens": [board.fen() for board in boards], "by_action": by_action,
            "selected_root": selected, "regret": regret, "nonterminal_leaf_slots_matched": matched}


def run() -> dict:
    cases = [fixture_case(fixture, side) for fixture in FIXTURES for side in chess.COLORS]
    # Two mirrors of the same board family form one analysis block.
    matched_families = {
        fixture.name for fixture in FIXTURES
        if all(case["nonterminal_leaf_slots_matched"] for case in cases
               if case["family"] == fixture.name)
    }
    deltas = [
        mean(case["regret"]["hidden_slot"] - case["regret"]["legacy"]
             for case in cases if case["family"] == fixture.name)
        for fixture in FIXTURES if fixture.name in matched_families
    ]
    def changed(case):
        return case["selected_root"]["legacy"] != case["selected_root"]["hidden_slot"]

    return {
        "primary_metric": {
            "name": "hidden-slot minus legacy observation-consistent root regret",
            "value": mean(deltas), "n": len(deltas), "unit": "bounded referee utility",
        } if deltas else None,
        "fixtures": cases,
        "families_with_matched_nonterminal_leaf_slots": sorted(matched_families),
        "root_reversals": sum(changed(case) for case in cases),
        "improved_reversals": sum(changed(case) and case["regret"]["hidden_slot"] < case["regret"]["legacy"]
                                  for case in cases),
        "worsened_reversals": sum(changed(case) and case["regret"]["hidden_slot"] > case["regret"]["legacy"]
                                  for case in cases),
        "limitations": [
            "Fixed two-world support and scripted opponent scores, using the local referee.",
            "One full table of referee continuations is scored once for both selectors; the primary metric only includes families with equal reply and nonterminal leaf slots.",
            "Both selectors re-normalize the same fixed reply probabilities over the slots they retain, as the legacy planner does.",
            "Legacy union/missing-as-loss and Jensen gap are retained in both arms; the oracle uses all scripted probability mass and legal common FoW continuations.",
            "Single-call local selector timings are diagnostics. No live engine calls, clock equivalence, competitive outcomes, or unseen-threat rate estimate.",
        ],
    }
