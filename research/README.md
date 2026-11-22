# Fog of War Chess — Research Record

This folder is the durable record of the MIT 6.7980 Fog of War Chess project. Source code and reproducible experiment configs belong in the repository; large replays/logs belong in private archives referenced by SHA-256 checksums.

## Preserved research materials

- Research agenda: 46 proposed experiments across information-aware search, belief inference, material safety, game-theoretic search, learned corrections, and evaluation. The full version-controlled agenda is `research/idea_backlog.md` and the 46-entry registry is `research/experiment_registry.jsonl`.
- Living report outline: `research/report_outline.md` is now in this branch. Conclusions and individual contributions must be supported by commits, runs, and evidence.
- Existing prior-team results: `APPROACHES.md`, `docs/obscuro.md`, `docs/versions.md`, and `docs/research/`. Do not retroactively assign authorship.
- Phase 2 experiment infrastructure: **restored on `infra/experiment-setup`** with exact original source blob hashes, plus checked-in `.github/workflows/experiments.yml`. The original local commit `01f405174bf99f66fbaef508aef45c2ecd803a47` remains recoverable from the private Git-bundle archive; restoring the source produced a new Git commit.

## Durable private backups

- [Research starter archive (Drive)](https://drive.google.com/file/d/1AVTpSRqa3EgpDjeIYXastV50muvDD7Gg/view)
- [Phase 2 infrastructure archive (Drive)](https://drive.google.com/file/d/1oXz7_EgZVWmZGDG1O9nmC96RSrsAHgCl/view)

These links are to private files and may not be accessible outside the authorized account.

## Rules for evidence

For each experiment, preserve: research ID, hypothesis, baseline, exact commit/configuration, color/opening pairs and seeds, clock and CPU limits, full-game count, W/D/L, uncertainty, risk and material-loss diagnostics, runtime failures, replay links/checksums, and an evidence-based conclusion.

Never modify frozen baseline bot files. Never commit secrets or use future full-board replay information as playing-time input. Official arena submissions require explicit authorization and separate authentication.

**Status as of 2026-11-22:** GitHub identity `smhgeo422` has verified write access. Phase 2 source, experiment configurations, 46-idea registry, and report outline are published on this draft branch. The hosted Phase 2 CI run [45059968560](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45059968560) **passed 235 tests** and its capped integration smoke; artifacts uploaded. The branch is in [draft PR #2](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/2), **not merged into `main`**. Full-length strength evaluation and durable off-Actions replay archiving still need separate validation.
