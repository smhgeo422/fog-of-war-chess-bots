# Fog of War Chess — Research Record

This folder is the durable record of the MIT 6.7980 Fog of War Chess project. Source code and reproducible experiment configs belong in the repository; large replays/logs belong in private archives referenced by SHA-256 checksums.

## Preserved research materials

- Research agenda: 46 proposed experiments across information-aware search, belief inference, material safety, game-theoretic search, learned corrections, and evaluation. The detailed `research/idea_backlog.md` is in the preserved research starter archive until imported here.
- Living report outline: `research/report_outline.md` in the preserved archive. Conclusions and individual contributions must be supported by commits, runs, and evidence.
- Existing prior-team results: `APPROACHES.md`, `docs/obscuro.md`, `docs/versions.md`, and `docs/research/`. Do not retroactively assign authorship.
- Phase 2 experiment infrastructure: saved at original local commit `01f405174bf99f66fbaef508aef45c2ecd803a47`, based on `580618950b9925521229bc076169967de2d87048`, in a Git bundle to restore on the connected `smhgeo422` account.

## Durable private backups

- [Research starter archive (Drive)](https://drive.google.com/file/d/1AVTpSRqa3EgpDjeIYXastV50muvDD7Gg/view)
- [Phase 2 infrastructure archive (Drive)](https://drive.google.com/file/d/1oXz7_EgZVWmZGDG1O9nmC96RSrsAHgCl/view)

These links are to private files and may not be accessible outside the authorized account.

## Rules for evidence

For each experiment, preserve: research ID, hypothesis, baseline, exact commit/configuration, color/opening pairs and seeds, clock and CPU limits, full-game count, W/D/L, uncertainty, risk and material-loss diagnostics, runtime failures, replay links/checksums, and an evidence-based conclusion.

Never modify frozen baseline bot files. Never commit secrets or use future full-board replay information as playing-time input. Official arena submissions require explicit authorization and separate authentication.

**Status:** connection to the researcher's GitHub account has been verified. The Phase 2 source code and full research backlog are archived but are not yet published on this branch. Do not claim hosted CI has run until an actual workflow run passes.
