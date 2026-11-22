import json
import platform
import sys
from pathlib import Path
from tools import tournament

out = Path(sys.argv[1])
pairs = [("obscuro", "greedy"), ("greedy", "obscuro")]
base, increment = 45, 0.5
config = dict(pairs=pairs, base_seconds=base, increment_seconds=increment,
              max_plies=None, stockfish="off", pause_waiting_bot=True,
              seeds=None, source_commit=(out / "source-commit.txt").read_text().strip(),
              python=platform.python_version(), platform=platform.platform())
(out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
tournament._worker_init(True)
results = []
for number, (white, black) in enumerate(pairs, 1):
    game = tournament.play_game((number, white, black, tournament.local.bot_argv(white),
                                 tournament.local.bot_argv(black), base, increment,
                                 float("inf"), str(out), True))
    _, _, _, result, reason, plies, seconds = game
    print(game, flush=True)
    replay = json.loads((out / f"{number:03d}_{white}_vs_{black}.json").read_text())
    results.append(dict(white=white, black=black, result=result, reason=reason, plies=plies,
                        seconds=seconds, failed_side=replay.get("failedSide")))
(out / "report.json").write_text(json.dumps(results, indent=2) + "\n")
assert all(r["result"] in {"1-0", "0-1", "1/2-1/2"} and r["plies"] > 0
           and r["failed_side"] is None and r["reason"] != "Move limit reached" for r in results), results
