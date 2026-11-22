# Methods and reproducibility notes

## Rules and information

The local course starter referee implements Fog of War movement, including castling through attacked squares, en passant visibility, termination when a king is capturable, repetition and the 50-move rule. The bot observes only its own 64-square view and protocol history. For offline scoring, the referee's complete board, selected action and policy identity are retrospective labels. They are stored separately from the six permitted predecision fields and never serve as live features. [Referee](../../starter/referee.py) · [Protocol](../../starter/README.md)

## Controls and data

- **B0** is frozen `obscuro_v4` with its pinned Stockfish 19 network and native position helper. **B2** is default eBotI. B1 was a v4-like eBotI configuration with 6/9 observed action agreements versus 10/11 for the v4-versus-v4 control. B1 therefore cannot substitute for B0. [Baseline audit](../STAGE2_FINDINGS.md)
- Stage 2 schema 2 is the canonical synthetic fixture. Seed 7106 produced 72 games in 36 color-swapped blocks and 2,190 observations. Training, development, ordinary holdout and opponent shift contain 36, 12, 12 and 12 games respectively. Whole games and color pairs stay together. Stage 4 regenerated this construction locally and revalidated the full replay histories. Its starter-policy games have no real chess clock. [Stage 2 findings](../STAGE2_FINDINGS.md) · [Stage 4 records](../runs/stage4-screen-20261122.json)
- Stage 3 used separate toy/restricted tests for the nine mechanisms. Stage 4 used the synthetic replays and bounded, mirrored referee fixtures. Stage 5 P3 used scripted reply probabilities with the same reply and nonterminal leaf counts, scored against an observation-consistent referee oracle. Stage 5 P8 used four new corpus seeds, a fixed shortlist, matched root quota, and reference worlds disjoint from evaluation worlds within each decision. The original P8 bootstrap resampled paired blocks within each seed. Repeated observation histories and per-block engine-work differences limit the result. [Stage 3 findings](../STAGE3_FINDINGS.md) · [Stage 5 findings](../STAGE5_FINDINGS.md)
- Compare Brier scores and log loss only within the same prediction target and control. Compare root regret within its specific oracle, payoff, and action set. Treat the P8 intervals as exploratory and the fixed tactical motifs as a declared fixture domain. Capped integration smokes and synthetic replay tests provide no estimate of live playing strength. [Preregistration](../stage0_preregistration.md)

## Reproduce or verify

Use Python 3.14 and `uv sync --locked`. From the specified clean source commit on its experiment branch, use the tracked offline config or Stage 4 runner. `tools/setup-experiments.sh` builds the pinned engines for tests that require them. The Stage 4 and 5 findings give the exact entry points. The archive inventory lists source SHA, config and input provenance. [Stage 4 reproduction](../STAGE4_FINDINGS.md#validation-and-reproduction) · [Stage 5 reproduction](../STAGE5_FINDINGS.md#validation-and-reproduction)

The report tables and figure can be rebuilt without launching experiments. [Package commands](README.md)
