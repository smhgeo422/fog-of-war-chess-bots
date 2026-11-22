"""Deterministic, referee-validated observation-only Stage 2 reference corpus.

Generates *synthetic starter-policy* FoW games, not strong-player match data.
All online features are saved separately from private replay/label truth.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import fow  # noqa: F401,E402 (puts starter on sys.path)
import chess  # noqa: E402
import referee  # noqa: E402
from uniform_random import ObservationTracker  # noqa: E402

POLICIES = ("uniform", "visible_capture", "king_pressure")
COUNTS = {"train": 18, "development": 6, "holdout": 6, "opponent_shift": 6}
MAX_PLIES = 100


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(stable(value).encode("utf-8")).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def write_jsonl(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in values:
            handle.write(stable(item) + "\n")


def score(move, view, side, policy):
    """Only use current 64-square view and move coordinates; never referee truth."""
    dest = view[move.to_square]
    enemy = "pnbrqk" if side else "PNBRQK"
    if policy == "uniform":
        return 1.0
    if policy == "visible_capture":
        return 4.0 if dest in enemy else (2.0 if move.promotion else 1.0)
    if policy == "king_pressure":
        enemy_king = "k" if side else "K"
        found = [i for i, ch in enumerate(view) if ch == enemy_king]
        if found:
            to = move.to_square
            distance = abs(chess.square_file(to) - chess.square_file(found[0])) + abs(
                chess.square_rank(to) - chess.square_rank(found[0]))
            return 1.0 + (10 - min(distance, 10)) * 0.5
        # King not visible: a fixed center preference; no oracle king square.
        to = move.to_square
        return 1.0 + (3.5 - abs(chess.square_file(to) - 3.5)) / 4.0
    raise ValueError("unknown synthetic policy")


def choose(moves, view, side, policy, rng):
    weights = [score(move, view, side, policy) for move in moves]
    assert weights and all(w > 0 for w in weights)
    return rng.choices(moves, weights=weights, k=1)[0]


def full_board(board):
    return "".join(board.piece_at(i).symbol() if board.piece_at(i) else "-"
                   for i in range(64))


def validate_replay(replay):
    """Independently rebuild every full state and view from published move history."""
    board = referee.FowBoard()
    frames = replay["frames"]
    if not frames or frames[0]["ply"] != 0:
        raise ValueError("missing initial replay frame")
    reps = Counter({referee.position_key(board): 1})
    for i, frame in enumerate(frames):
        if frame["ply"] != i or frame["board"] != full_board(board):
            raise ValueError("replayed full board disagrees at ply " + str(i))
        for side, key in ((chess.WHITE, "white"), (chess.BLACK, "black")):
            if frame[key] != referee.observation(board, side):
                raise ValueError("reconstructed observation disagrees at ply " + str(i))
        if i + 1 < len(frames):
            uci = frames[i + 1]["move"]
            move = chess.Move.from_uci(uci)
            if move not in referee.fow_moves(board):
                raise ValueError("illegal referee move at ply " + str(i))
            board.push(move)
            reps[referee.position_key(board)] += 1
    term = referee.outcome(board, reps)
    if term is None:
        if len(board.move_stack) != replay["max_plies"] or replay["reason"] != "Synthetic ply cap":
            raise ValueError("nonterminal replay has no declared synthetic cap")
    elif replay["reason"] != term[1] or replay["result"] != term[0]:
        raise ValueError("terminal replay result contradicts referee")
    return len(frames) - 1


def pair_seed(root_seed, block, swap, side):
    raw = f"stage2-corpus|{root_seed}|{block}|{swap}|{int(side)}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def play(game_id, root_seed, block, swap, split, white_policy, black_policy):
    board = referee.FowBoard()
    reps = Counter({referee.position_key(board): 1})
    trackers = {side: ObservationTracker(side) for side in (chess.WHITE, chess.BLACK)}
    histories = {side: [] for side in trackers}
    styles = {chess.WHITE: white_policy, chess.BLACK: black_policy}
    rngs = {side: random.Random(pair_seed(root_seed, block, swap, side))
            for side in trackers}
    observations, labels = [], []
    replay = {"id": game_id, "source": "locally generated observation-only starter policies",
              "split": split, "policies": {"white": white_policy, "black": black_policy},
              "seed_block": block, "swap": swap, "max_plies": MAX_PLIES,
              "time_control": "none; synthetic referee simulation",
              "result": "*", "reason": "In progress",
              "frames": [referee.make_frame(board, (0.0, 0.0))]}
    for ply in range(MAX_PLIES + 1):
        ended = referee.outcome(board, reps)
        if ended is not None:
            replay["result"], replay["reason"] = ended
            break
        if ply >= MAX_PLIES:
            replay["result"], replay["reason"] = "1/2-1/2", "Synthetic ply cap"
            break
        views = {side: referee.observation(board, side) for side in trackers}
        for side, tracker in trackers.items():
            tracker.observe(views[side])
            histories[side].append({"type": "observation", "ply": ply, "view": views[side]})
        side = board.turn
        ours = trackers[side]
        attempts = ours.legal_moves()  # rule calculation from observation only
        authorized = set(referee.fow_moves(board))
        if not attempts or any(move not in authorized for move in attempts):
            raise ValueError("observation-only legal moves contradict local referee at "
                             + game_id + ":" + str(ply))
        chosen = choose(attempts, views[side], side, styles[side], rngs[side])
        own_view = views[side]
        feature = {
            "schema": 1, "game_id": game_id, "split": split, "ply": ply,
            "side": "white" if side else "black", "view": own_view,
            "own_history_sha256": digest(histories[side]),
            "legal_attempts": sorted(move.uci() for move in attempts),
            "selected_action": chosen.uci(),
            "policy": styles[side], "opponent_policy": styles[not side],
            "visible_enemy_count": sum(c in ("pnbrqk" if side else "PNBRQK")
                                       for c in own_view),
            "visible_square_count": 64 - own_view.count("?"),
        }
        forbidden = {"fen", "board", "true_board", "future", "hidden", "opponent_action"}
        if forbidden.intersection(feature):
            raise ValueError("private referee truth leaked into public feature")
        observations.append(feature)
        labels.append({
            "schema": 1, "game_id": game_id, "ply": ply,
            "truth_board_fen": board.fen(),
            "truth_board_64": full_board(board),
            "truth_enemy_king_square": chess.square_name(board.king(not side))
            if board.king(not side) is not None else None,
            "truth_our_king_in_check": board.is_check(),
            "truth_legal_moves": sorted(move.uci() for move in authorized),
            "selected_action": chosen.uci(),
            "retrospective_only": True,
        })
        ours.record_move(chosen)
        histories[side].append({"type": "own_action", "ply": ply, "uci": chosen.uci()})
        board.push(chosen)
        reps[referee.position_key(board)] += 1
        replay["frames"].append(referee.make_frame(board, (0.0, 0.0), chosen.uci()))
    plies = validate_replay(replay)
    if plies != len(observations) or len(observations) != len(labels):
        raise ValueError("replay/feature/label count mismatch")
    return replay, observations, labels


def build(root, root_seed=7106):
    """Write 36 color-swapped blocks (72 games) with stable disjoint splits."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    all_games, all_features, all_labels, groups = [], [], [], []
    block_no = 0
    for split, count in COUNTS.items():
        for _ in range(count):
            block_no += 1
            left, right = ("uniform", "king_pressure") if split == "opponent_shift" else (
                "uniform", "visible_capture")
            for swap in (0, 1):
                white, black = (left, right) if swap == 0 else (right, left)
                name = f"s2-{block_no:03d}-{'ab' if swap == 0 else 'ba'}"
                replay, feature, label = play(name, root_seed, block_no, swap, split, white, black)
                path = root / "replays" / split / (name + ".json")
                write_json(path, replay)
                all_games.append({
                    "game_id": name, "split": split, "pair_block": block_no,
                    "policy_white": white, "policy_black": black,
                    "seed_white": pair_seed(root_seed, block_no, swap, True),
                    "seed_black": pair_seed(root_seed, block_no, swap, False),
                    "plies": len(replay["frames"]) - 1, "replay": path.relative_to(root).as_posix(),
                    "replay_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "result": replay["result"], "reason": replay["reason"],
                })
                all_features.extend(feature)
                all_labels.extend(label)
                groups.append((name, split, block_no))
    for split in COUNTS:
        fs = [x for x in all_features if x["split"] == split]
        ls = [x for x in all_labels if
              next(g[1] for g in groups if g[0] == x["game_id"]) == split]
        write_jsonl(root / "observations" / (split + ".jsonl"), fs)
        write_jsonl(root / "retrospective_labels" / (split + ".jsonl"), ls)
    if len(set(x["game_id"] for x in all_games)) != len(all_games):
        raise ValueError("duplicate game ID")
    by_split = {name: [x["game_id"] for x in all_games if x["split"] == name]
                for name in COUNTS}
    if any(set(by_split[a]) & set(by_split[b])
           for a in by_split for b in by_split if a != b):
        raise ValueError("game leakage between data splits")
    block_splits = {x["pair_block"]: x["split"] for x in all_games}
    if any(block_splits[x["pair_block"]] != x["split"] for x in all_games):
        raise ValueError("paired color blocks split apart")
    if any(x["opponent_policy"] == "king_pressure" for x in all_features
           if x["split"] != "opponent_shift"):
        raise ValueError("unseen opponent style leaked into train/dev/test")
    manifest = {
        "schema": 1, "provenance": "fresh synthetic games, local starter FowBoard/ObservationTracker; no public arena or private replays",
        "seed": root_seed, "generator": "tools/stage2_corpus.py",
        "games": len(all_games), "pairs": block_no, "max_plies": MAX_PLIES,
        "split_groups": by_split, "pair_blocks": block_splits, "style_holdout": "king_pressure",
        "training_allowed": ["train"], "model_selection_allowed": ["development"],
        "confirmatory_holdout": ["holdout"], "opponent_shift_holdout": ["opponent_shift"],
        "private_label_path": "retrospective_labels/<split>.jsonl",
        "online_only_path": "observations/<split>.jsonl",
        "not_competitive_training_data": True,
        "no_chess_clock": True, "no_official_arena_data": True,
        "limitations": [
            "Observation-only simple synthetic opponents are not representative of high-skill FoW play.",
            "The same small policy families appear in train/dev/ordinary holdout; opponent_shift is separately isolated.",
            "Synthetic paired positions are correlated by source-game and must be clustered by full game/block.",
            "Private truth labels are retrospective and forbidden as online model input.",
            "No time-control or Stockfish result is established by this synthetic corpus.",
        ],
    }
    write_json(root / "corpus_manifest.json", manifest)
    write_json(root / "game_registry.json", all_games)
    return manifest, all_games, all_features


def audit(root):
    """Re-read generated files, detect edits and verify all label/feature pairs."""
    root = Path(root)
    manifest = json.loads((root / "corpus_manifest.json").read_text())
    games = json.loads((root / "game_registry.json").read_text())
    split_by_game = {x["game_id"]: x["split"] for x in games}
    if len(games) != manifest["games"]:
        raise ValueError("registry counts disagree")
    observed_count = 0
    for game in games:
        path = root / game["replay"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != game["replay_sha256"]:
            raise ValueError("replay SHA mismatch")
        data = json.loads(path.read_text())
        if validate_replay(data) != game["plies"]:
            raise ValueError("replay plies disagree")
    for split in COUNTS:
        fpath = root / "observations" / (split + ".jsonl")
        lpath = root / "retrospective_labels" / (split + ".jsonl")
        fs = [json.loads(line) for line in fpath.read_text().splitlines() if line]
        ls = [json.loads(line) for line in lpath.read_text().splitlines() if line]
        if len(fs) != len(ls):
            raise ValueError("feature and label count mismatch")
        for f, label in zip(fs, ls):
            if (f["game_id"], f["ply"]) != (label["game_id"], label["ply"]):
                raise ValueError("observation/label alignment mismatch")
            if split_by_game[f["game_id"]] != split:
                raise ValueError("cross-split feature contamination")
            if len(f["view"]) != 64 or len(label["truth_board_64"]) != 64:
                raise ValueError("incorrect square count")
            if "truth_board_64" in f or "truth_board_fen" in f:
                raise ValueError("private truth in online feature data")
            if f["selected_action"] not in f["legal_attempts"]:
                raise ValueError("selected action unavailable to player")
        observed_count += len(fs)
    return {"games_checked": len(games), "pairs_checked": manifest["pairs"],
            "decisions_checked": observed_count, "replay_reconstruction_rate": 1.0,
            "split_counts": {k: len(v) for k, v in manifest["split_groups"].items()}}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", type=int, default=7106)
    args = p.parse_args()
    build(args.output, args.seed)
    print(json.dumps(audit(args.output), indent=2))
