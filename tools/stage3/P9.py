"""P9-v1: bounded information-state reachability certificates.

The verifier requires a *single root action* across worlds sharing the same
FoW observation, then a universal check across adversary responses. "Win"
is a machine-checkable finite restricted-game certificate, NOT a global KQvK
theorem. Full 8x8 unbounded belief-game completeness is explicitly out of scope.
"""
from __future__ import annotations
from functools import lru_cache


def certify(nodes, start, horizon):
    """Finite known transition graph.

    node = {"view": str, "actions": {action: [("win" | "loss" |
             next-node-ID), ...]}}.
    A world may branch nondeterministically on an opponent move. A common
    action is selected once per identical observation/history prefix; all
    resulting next observations are solved separately and recursively.
    """
    if not start or horizon < 0:
        raise ValueError("nonempty starting infoset and nonnegative horizon")
    if any(s not in nodes for s in start):
        raise ValueError("unknown hidden world")
    visited = {"calls": 0, "edges": 0}
    @lru_cache(None)
    def solve(world_ids, remaining):
        visited["calls"] += 1
        if not world_ids or remaining <= 0:
            return None
        views = {nodes[s]["view"] for s in world_ids}
        if len(views) != 1:
            raise ValueError("a decision information set contains distinct observations")
        common = set.intersection(*(set(nodes[s]["actions"]) for s in world_ids))
        for action in sorted(common):
            next_groups = {}
            possible = True
            for state in world_ids:
                outcomes = nodes[state]["actions"][action]
                if not outcomes:
                    possible = False
                    break
                for successor in outcomes:
                    visited["edges"] += 1
                    if successor == "loss":
                        possible = False
                        break
                    if successor == "win":
                        continue
                    if successor not in nodes:
                        raise ValueError("missing adversary successor")
                    key = nodes[successor]["view"]
                    next_groups.setdefault(key, set()).add(successor)
                if not possible:
                    break
            if not possible:
                continue
            children = {}
            for obs, worlds in next_groups.items():
                child = solve(tuple(sorted(worlds)), remaining - 1)
                if child is None:
                    possible = False
                    break
                children[obs] = child
            if possible:
                return {"action": action, "children": children}
        return None
    result = solve(tuple(sorted(start)), horizon)
    return {"certified_winning": result is not None,
            "witness": result, "reachable_calls": visited["calls"],
            "adversary_edges_checked": visited["edges"],
            "horizon": horizon, "initial_worlds": len(start)}


def fow_endgame_sanity():
    """Use the real referee on KQ-v-K hidden-king worlds, never known-board
    lookahead to choose different moves when the white observations match.
    """
    import fow  # noqa: F401
    import chess
    import referee
    x = referee.FowBoard("1k6/8/8/8/8/8/8/K6Q w - - 0 1")
    y = referee.FowBoard("2k5/8/8/8/8/8/8/K6Q w - - 0 1")
    views = [referee.observation(board, chess.WHITE) for board in (x, y)]
    if views[0] != views[1]:
        raise AssertionError("intended hidden king states are distinguishable")
    legal = [set(referee.fow_moves(board)) for board in (x, y)]
    moves = sorted(m.uci() for m in legal[0] & legal[1])
    if "h1h4" not in moves:
        raise AssertionError("expected common KQ move absent")
    # Restrict toy horizon to a single *same* white action and the entire
    # black pseudo-legal reply set. No success guarantee is inferred here.
    reply_counts = []
    for board in (x, y):
        copied = board.copy(stack=False)
        copied.push_uci("h1h4")
        reply_counts.append(len(referee.fow_moves(copied)))
    return {"same_public_own_view": views[0] == views[1],
            "common_attempts": len(moves),
            "defender_reply_counts_after_h1h4": reply_counts,
            "h1h4_is_feasible_in_both_worlds": True,
            "not_exhaustive_8x8_endgame": True}



def certify_referee_one_turn(fens, side=True):
    """Exhaustive *one own move + one opponent reply* reachability check under
    actual starter FoW rules. This is a sound positive certificate for the
    supplied, nonterminal full-state support and this ONE-turn horizon only.

    Every candidate action must be legal in all possible worlds that yield
    the same current observation; every legal opponent reply is enumerated.
    Longer-game guarantees, repetition-history, and unreachable-state filters
    are expressly outside this bounded certificate's assumptions.
    """
    import fow  # noqa: F401
    import chess
    import referee
    from collections import Counter
    if not fens:
        raise ValueError("no initial hidden states")
    boards = [referee.FowBoard(fen) for fen in fens]
    if any(board.turn != side for board in boards):
        raise ValueError("not own turn in every hidden state")
    obs = {referee.observation(board, side) for board in boards}
    if len(obs) != 1:
        raise ValueError("starting states are not one information set")
    for board in boards:
        if referee.outcome(board, Counter({referee.position_key(board): 1})):
            raise ValueError("already terminal; no active one-turn certificate")
    common = set.intersection(*(set(referee.fow_moves(board)) for board in boards))
    wins = []
    replies_checked = 0
    for action in sorted(common, key=lambda move: move.uci()):
        works = True
        for board in boards:
            after_own = board.copy(stack=False)
            after_own.push(action)
            seen = Counter({referee.position_key(board): 1,
                            referee.position_key(after_own): 1})
            term = referee.outcome(after_own, seen)
            if term is not None:
                if term[0] != ("1-0" if side else "0-1"):
                    works = False
                    break
                continue
            for reply in referee.fow_moves(after_own):
                replies_checked += 1
                next_board = after_own.copy(stack=False)
                next_board.push(reply)
                future = seen.copy()
                future[referee.position_key(next_board)] += 1
                terminal = referee.outcome(next_board, future)
                if terminal is None or terminal[0] != ("1-0" if side else "0-1"):
                    works = False
                    break
            if not works:
                break
        if works:
            wins.append(action.uci())
    return {"real_referee": True, "worlds": len(boards),
            "common_legal_attempts_checked": len(common),
            "full_defender_replies_checked": replies_checked,
            "certified_one_turn_capture_actions": wins,
            "horizon_own_turns": 1,
            "no_broader_endgame_theorem": True}

def trial(seed=719):
    # Two hidden kings, one common probe; next observation disambiguates.
    states = {
        "h1": {"view": "same", "actions": {"probe": ["l"], "guess-left": ["win"],
                                          "guess-right": ["loss"]}},
        "h2": {"view": "same", "actions": {"probe": ["r"], "guess-left": ["loss"],
                                          "guess-right": ["win"]}},
        "l": {"view": "seen-left", "actions": {"capture-left": ["win"]}},
        "r": {"view": "seen-right", "actions": {"capture-right": ["win"]}},
    }
    win = certify(states, ["h1", "h2"], 2)
    no = certify(states, ["h1", "h2"], 1)
    assert win["certified_winning"] and win["witness"]["action"] == "probe"
    assert not no["certified_winning"]
    # An adversary counterexample invalidates a claimed forced win.
    attacked = {k: {"view": v["view"],
                    "actions": {a: list(x) for a, x in v["actions"].items()}}
                for k, v in states.items()}
    attacked["h2"]["actions"]["probe"].append("loss")
    assert not certify(attacked, ["h1", "h2"], 2)["certified_winning"]
    real = fow_endgame_sanity()
    bounded = certify_referee_one_turn(
        ["1k6/8/8/8/8/8/8/K6Q w - - 0 1",
         "2k5/8/8/8/8/8/8/K6Q w - - 0 1"], True)
    assert bounded["real_referee"] and bounded["worlds"] == 2
    assert bounded["common_legal_attempts_checked"] > 0
    return {"primary_metric": "zero false win certificates in complete finite adversarial toy graph",
            "exact_toy_depth2_winning": win,
            "exact_toy_depth1_winning": no,
            "adversary_counterexample_rejected": True,
            "actual_referee_hidden_king_sanity": real,
            "bounded_real_referee_certificate": bounded,
            "limitations": "Certificate applies only to supplied finite transitions; queen-vs-king 8x8 theorem NOT reproduced, defended, or extended."}
