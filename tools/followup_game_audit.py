"""Observe fresh baseline histories and audit the opt-in P3 reply selector."""

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
from functools import lru_cache
from hashlib import file_digest
import json
from pathlib import Path
import random
from statistics import mean
import subprocess
import tarfile
import time

import chess
import chess.engine
import fow  # exposes the course referee
import referee
from bots.eBotI.eBotI import infoset
from bots.eBotI.eBotI.engine import cp_value, mate_value
from bots.eBotI.eBotI.position_set import PositionSet
from bots.eBotI.eBotI.stockfish_search import engine_accepts, engine_fen, LOSS
from tools.stage3 import P1
from tools.stage4.replay import move_category, retrospective_material_loss, unseen_king_attack

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "bots/obscuro_v4/stockfish/src/stockfish"
HELPER = REPO / "bots/eBotI/positions"


def terminal(board, actor):
    result = referee.outcome(board, Counter())
    if result is None:
        return None
    if result[0] == "1/2-1/2":
        return 0.0
    return 1.0 if result[0] == ("1-0" if actor else "0-1") else -1.0


def child(board, uci):
    after = board.copy(stack=False)
    after.push_uci(uci)
    return after


def board_table(engine):
    @lru_cache(maxsize=15000)
    def score(fen, depth, cap):
        board = chess.Board(fen)
        if not board.is_valid() or not board.legal_moves:
            return {}, 0
        result = engine.analyse(board, chess.engine.Limit(depth=depth),
                                multipv=min(cap, board.legal_moves.count()), game=object())
        values = {}
        for row in result:
            pv = row.get("pv")
            if not pv:
                continue
            pov = row["score"].pov(board.turn)
            values[pv[0].uci()] = mate_value(pov.mate()) if pov.is_mate() else cp_value(pov.score())
        # MultiPV lines share the same search; count the engine node counter once.
        return values, max((x.get("nodes", 0) for x in result), default=0)
    return score


def lookup(score, board, depth, cap):
    if not engine_accepts(board):
        return {}, 0
    moves = {m.uci() for m in referee.fow_moves(board)}
    values, nodes = score(engine_fen(board), depth, cap)
    return {m: v for m, v in values.items() if m in moves}, nodes


def make_probe(score, states, weights, side):
    root_tables = [lookup(score, b, 3, 12)[0] for b in states]
    common = set.intersection(*(set(moves) for moves in root_tables))
    if len(common) < 2:
        return None
    totals = {uci: sum(w * moves[uci] for w, moves in zip(weights, root_tables, strict=True))
              for uci in common}
    candidates = sorted(common, key=lambda u: (-totals[u], u))[:3]
    groups = {}
    for action in candidates:
        groups[action] = []
        for board, weight in zip(states, weights, strict=True):
            after = child(board, action)
            if (value := terminal(after, side)) is not None:
                groups[action].append((weight, value, None, None))
                continue
            values, _ = lookup(score, after, 1, 64)
            if not values:
                return None
            odds = infoset._reply_odds(values)
            groups[action].append((weight, None, after, odds))
    return {u: totals[u] for u in candidates}, groups


def reply_picks(groups, side):
    picks = {}
    for action, worlds in groups.items():
        picks[action] = []
        for _, _, board, odds in worlds:
            if board is None:
                picks[action].append(([], [], []))
                continue
            ranked = sorted(odds, key=lambda u: -odds[u])
            picks[action].append((
                infoset.select_replies(board, odds, 3, side),
                infoset.select_replies(board, odds, 3, side, reserve_hidden=True),
                ranked[:8],
            ))
    return picks


def evaluate_arm(score, base, groups, picks, side, arm):
    output = {}
    calls = nodes = omissions = 0
    for action, worlds in groups.items():
        buckets = defaultdict(list)
        fixed = perfect = 0.0
        for (weight, terminal_value, board, odds), selections in zip(worlds, picks[action], strict=True):
            if terminal_value is not None:
                fixed += weight * terminal_value
                continue
            selected = selections[arm]
            normalizer = sum(odds[move] for move in selected)
            for reply in selected:
                after = child(board, reply)
                mass = weight * odds[reply] / normalizer
                if (value := terminal(after, side)) is not None:
                    fixed += mass * value
                    continue
                table, cost = lookup(score, after, 5 if arm == 2 else 3, 12 if arm == 2 else 8)
                if not table:
                    omissions += 1
                    continue
                calls += 1
                nodes += cost
                perfect += mass * max(table.values())
                buckets[referee.observation(after, side)].append((mass, table))
        contingent = 0.0
        for members in buckets.values():
            allowed = set.union(*(set(table) for _, table in members))
            contingent += max(sum(w * table.get(u, LOSS) for w, table in members)
                              for u in sorted(allowed))
        output[action] = fixed + contingent if arm == 2 else base[action] + contingent - perfect
    return output, {"nonterminal_tables": calls, "nodes": nodes, "unscored_leaves": omissions}


def sampling_audit(active, move, side, label, seed):
    weighted = [(w, unseen_king_attack(board, move, side))
                for board, w in zip(active.states, active.weights, strict=True)
                if w > 0 and board.turn == side and move in referee.fow_moves(board)]
    if not weighted:
        return None
    weights, events = zip(*weighted, strict=True)
    posterior = P1.normalize(weights)
    exact = sum(p * e for p, e in zip(posterior, events, strict=True))
    arms = {}
    for alpha in (0.0, 0.3):
        draws = [P1.sample(weights, events, 64, alpha, f"{seed}:{k}") for k in range(8)]
        estimates = [P1.expected_event(events, d) for d in draws]
        arms[str(alpha)] = {"brier": mean((p - label) ** 2 for p in estimates),
                            "mse_to_sampled_support": mean((p - exact) ** 2 for p in estimates),
                            "effective_draws": mean(d["ess"] for d in draws),
                            "estimates": estimates}
    return {"retrospective_label": label, "retained_support_risk": exact,
            "supported_worlds": len(events), "arms": arms}


def reconstruct(replay, game, score, material_model=None):
    flags = Counter()
    selected = {}
    records = []
    sampling = []
    material = []
    true_board = referee.FowBoard()
    histories = replay["frames"]
    with ExitStack() as cleanup:
        belief = {}
        for side in chess.COLORS:
            instance = PositionSet(side, [str(HELPER)], 4096, random.Random(f"{game}:{side}"))
            cleanup.callback(instance.close)
            belief[side] = instance
        for ply, frame in enumerate(histories):
            last_move = chess.Move.from_uci(frame["move"]) if ply else None
            if last_move:
                true_board.push_uci(last_move.uci())
            for color in chess.COLORS:
                if referee.observation(true_board, color) != frame[chess.COLOR_NAMES[color]]:
                    raise ValueError(f"{game}:{ply} has an inconsistent replay observation")
            if ply + 1 >= len(histories):
                break
            next_move = chess.Move.from_uci(histories[ply + 1]["move"])
            side = true_board.turn
            flags["plies"] += 1
            king_event = unseen_king_attack(true_board, next_move, side)
            flags["king_attack_events"] += king_event
            pieces = Counter(p.symbol().lower() for p in true_board.piece_map().values())
            flags["KQvK_plies"] += pieces == {"k": 2, "q": 1}
            if ply + 2 < len(histories):
                after = child(true_board, next_move.uci())
                reply = chess.Move.from_uci(histories[ply + 2]["move"])
                view = histories[ply + 1][chess.COLOR_NAMES[side]]
                flags["material_reply_opportunities"] += 1
                event = retrospective_material_loss(after, reply, view)
                flags["unseen_material_losses"] += event
                if material_model is not None:
                    category = move_category(frame[chess.COLOR_NAMES[side]], side, next_move)
                    probability = material_model["trained_event_probabilities"][category]
                    constant = material_model["train_baseline_probability"]
                    material.append({"ply": ply, "category": category, "event": int(event),
                                     "model_probability": probability, "constant_probability": constant,
                                     "model_brier": (probability - event) ** 2,
                                     "constant_brier": (constant - event) ** 2})
            for color, instance in belief.items():
                view = frame[chess.COLOR_NAMES[color]]
                try:
                    instance.observe(view, own_move=last_move if color != side else None)
                except (RuntimeError, ValueError):
                    flags["belief_repairs"] += 1
                    instance.repair(view, side)
            if score is not None and (ply < 12 or (ply - 12) % 7):
                continue
            flags["offered"] += 1
            active = belief[side]
            estimate = sampling_audit(active, next_move, side, king_event, f"{game}:{ply}")
            if estimate is not None:
                sampling.append({"ply": ply, **estimate})
            if score is None:
                continue
            ranked = sorted(zip(active.weights, active.states, strict=True), key=lambda row: (-row[0], row[1].fen()))
            unique = {}
            for weight, board in ranked:
                if weight > 0 and board.turn == side and engine_accepts(board):
                    unique.setdefault(referee.position_key(board), (weight, board))
            roots = list(unique.values())[:3]
            if not roots:
                flags["no_compatible_roots"] += 1
                continue
            weights, boards = zip(*roots, strict=True)
            total = sum(weights)
            probe = make_probe(score, boards, [w / total for w in weights], side)
            if probe is None:
                flags["no_common_tables"] += 1
                continue
            base, groups = probe
            picks = reply_picks(groups, side)
            changed = sum(arms[0] != arms[1] for choices in picks.values() for arms in choices)
            flags["scored"] += 1
            flags["native_fallback"] += active.fallback is not None
            flags["slot_exposures"] += bool(changed)
            flags["reply_sets_changed"] += changed
            flags["root_action_worlds"] += sum(len(v) for v in groups.values())
            entry = {"ply": ply, "side": chess.COLOR_NAMES[side], "changed_reply_sets": changed,
                     "sampled_roots": len(boards), "belief_size": len(active), "exact": active.exact,
                     "candidates": list(base)}
            records.append(entry)
            key = "replacement" if changed else "control"
            if key not in selected:
                selected[key] = ply
                evaluations = [evaluate_arm(score, base, groups, picks, side, arm) for arm in range(3)]
                reference = evaluations[2][0]
                actions = [max(table, key=table.get) for table, _ in evaluations[:2]]
                match = (evaluations[0][1]["nonterminal_tables"] == evaluations[1][1]["nonterminal_tables"]
                         and not any(work["unscored_leaves"] for _, work in evaluations))
                entry["ablation"] = {
                    "group": key, "moves": actions, "matched_complete_leaf_tables": match,
                    "regret": [max(reference.values()) - reference[m] for m in actions],
                    "values": [table for table, _ in evaluations],
                    "work": [work for _, work in evaluations],
                    "replies": picks,
                }
    return {"game": game, "counts": dict(flags), "decisions": records,
            "sampling": sampling, "material": material}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replays", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--event-audit", action="store_true",
                        help="Check all plies for P1 and score the frozen Stage 4 P5 model")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        raise ValueError("Run from a clean source commit")
    manifest = json.loads((args.replays / "manifest.json").read_text())
    summary = json.loads((args.replays / "report.json").read_text())
    if summary["invalid"] or summary["failure_codes"] or summary["worker_exit_codes"] != [0]:
        raise ValueError("Replay collection has invalid or failed games")
    paths = sorted((args.replays / "replays").glob("*.json"))
    if len(paths) != 6:
        raise ValueError("Expected the six declared replay histories")
    start = time.monotonic()
    with ExitStack() as cleanup:
        score = None
        model = None
        if args.event_audit:
            [archive] = (REPO / "research/archives/stage4-screen-20261122").glob("*.tar.gz")
            with tarfile.open(archive) as bundle:
                with bundle.extractfile("run/projects.json") as stream:
                    model = json.load(stream)["P5"]
        else:
            engine = cleanup.enter_context(
                chess.engine.SimpleEngine.popen_uci(str(ENGINE), cwd=ENGINE.parent, timeout=15))
            engine.configure({"Threads": 1, "Hash": 16})
            score = board_table(engine)
        games = []
        for path in paths:
            row = reconstruct(json.loads(path.read_text()), path.name, score, model)
            games.append(row)
            print(path.name, row["counts"], flush=True)
    with ENGINE.open("rb") as binary:
        engine_sha256 = file_digest(binary, "sha256").hexdigest()
    data = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "replay_source_commit": manifest["commit"], "engine_sha256": engine_sha256,
            "mode": "all_plies_events" if args.event_audit else "scheduled_engine",
            "games": games, "wall_seconds": time.monotonic() - start}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
