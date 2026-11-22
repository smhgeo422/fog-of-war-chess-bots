# Local bot experiments

Use a Linux x86-64 host with AVX2, Git, Bash, curl, GNU coreutils, g++, make, and uv 0.13.9. The setup command can serve as a Codex Cloud setup script after the repository is connected. Allow access to GitHub, the uv/Python package sources, and the Stockfish network host or its GitHub mirror. The script installs locked Python dependencies with CPython 3.14.10, checks the Stockfish source revision and NNUE SHA-256, and builds each bot's own engine and helper. Repeated runs verify cached artifact hashes and rebuild when inputs change.

```bash
tools/setup-experiments.sh
tools/check-experiments.sh --id validation-001
```

The second command runs the same setup, full suite including real-engine and protocol tests, and smoke configuration as GitHub CI. It uses a new ID so previous runs are preserved. Setup and test logs live under `data/research/`. Setup accepts additional bot directory names with their own `build.sh` and component markers.

## Running a hypothesis

Start each implementation on a separate branch or worktree. Commit the implementation and configuration before running. Keep the frozen `obscuro_v4` baseline on that branch. See `configs/screening.json` and `configs/arena-clock.json` for short-clock and 180+2 examples. Select an even game count. Each pair reuses per-bot seeds with swapped colors, and the seed sequence comes from the configured root seed.

```bash
tools/setup-experiments.sh
.venv/bin/python tools/experiment.py experiments/configs/screening.json --id my-branch-screen-001
.venv/bin/python tools/experiment.py experiments/configs/arena-clock.json --id my-branch-arena-001
```

The runner accepts named bots under `bots/` with a `run.sh` that accepts `--seed`. Native bots should provide `REQUIRE_STOCKFISH` and/or `REQUIRE_POSITIONS` and emit the same readiness and component-loss log messages as the current bots. The runner supplies absolute binary paths, removes inherited component overrides, and requires both sides to use separate engine files. Missing readiness or a reported component loss invalidates the score and produces a nonzero exit. Time forfeits and other referee-level bot failures remain visible in the recorded result and also produce a nonzero exit. The waiting bot is paused. The runner limits workers using CPU affinity and the container CPU quota. Use one experiment invocation per machine at a time for timing measurements and keep a single worker on a two-CPU host. Seeded choices still depend on clock deadlines.

## Reading and retaining results

Each unique run directory contains the following.

| File | Contents |
|---|---|
| `manifest.json` | Exact commit and ref, environment, resolved settings, binary paths and hashes, Stockfish version |
| `registry.json` | Unique ID, hypothesis, implementation reference, baseline, settings, result pointer, and conclusion |
| `replays/*.json` | Referee frames, per-game seeds, raw outcome and termination reason, protocol and component diagnostics |
| `report.json`, `report.md` | Machine-readable and human-readable summaries |

Game lengths and clock statistics report sample sizes. Clock usage measures accepted moves and any remaining clock charged on a time forfeit. The king metric counts post-move frames with a geometrically attacked king. Hidden captures count pieces lost when the capturing piece's origin was unseen by the victim immediately before the move, including en passant. These replay diagnostics are proxies. The exploratory paired bootstrap estimates score uncertainty from complete color pairs and is suppressed for smoke runs or fewer than five pairs. Inspect exclusions and color splits before interpreting results. Enter the research conclusion in the retained registry after review.

For unattended runs on GitHub, dispatch **Fog of War validation** on the implementation branch with a tracked experiment config path. The workflow archives logs and reports even on ordinary failures. Validation artifacts expire after 30 days and experiment artifacts after 90 days. A workflow must be present on the default branch before GitHub enables manual dispatch. Use `--results /path/to/durable/storage` on hosts with a connected persistent volume, or archive the complete per-run directory and retain it in approved storage before the workspace or Actions artifact expires. Multiple branches can share a results root when experiment IDs are globally unique. Keep raw replays and registry files together with their commit references. The workflow has read-only repository permissions and relies on the artifact service for results.
