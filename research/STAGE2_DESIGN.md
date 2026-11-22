# Stage 2 — reference controls and a leakage-safe FoW corpus

**Stage goal:** establish reproducible local referee observations, replay validation, frozen B0/B1/B2 identities, controlled-color baseline matches and separated development/confirmation data *before* Stage 3 algorithms. This is measurement infrastructure, not a claim of superior chess strategy or a trained model.

## B0 / B1 / B2 contract

| Label | Bot | Settings | Scientific interpretation |
|---|---|---|---|
| B0 | bots/obscuro_v4 | Original frozen code, separate Stockfish 19/NNUE and compiled position helper; SHA protected by tests/frozen_bots.sha256 | Unmodified reference, always safe to use as comparator |
| B1 | bots/eBotI | **Proposed v4-parity profile** from tools/stage2_parity.py B1_ENV | Not assumed equal; separately verify common component values and black-box actions |
| B2 | bots/eBotI | Current default FOW profile, no overrides | The team's current experimental bot; differences from B0 include book, safe-first, exact risk, hang penalty and reserve clock |

The Stage 2 pipeline checks the frozen checksum inventory, records per-bot source, Stockfish and helper SHA256s, verifies all engines use the same NNUE and launches a shared-observation **black-box action-prefix test** using the same random seeds. After the first disagreement, it stops the trajectory: running forward would compare actions conditional on different own histories and yield false equivalence evidence. The probe checks both colors and several early decisions. Decision equality on finitely many histories does **not** prove all-history equivalence, and any divergence means B1 is **not** a validated clone of B0. In that case the next stages use B0 directly and label B1 merely a parity candidate.

The B1 settings are explicitly:
~~~text
FOW_SAFE_FIRST=0 FOW_EXACT_RISK=0 FOW_ATTACKED=6 FOW_HANG=0
FOW_CLOCK=v4 FOW_BOOK=none FOW_ROOTS=64 FOW_SCAN=256 FOW_DEPTH=12
FOW_SLICE=1.0 FOW_RISK_UNIFORM=0 FOW_TIME=1.0 FOW_FOG_TAX=0
FOW_HAZARD=0 FOW_CVAR=0 FOW_WORST=0 FOW_RISK_LAMBDA=1.0
FOW_THREAT=1.0 FOW_KING_PENALTY=0 FOW_RANDOM=0 FOW_INFOSET=0
~~~
Only the candidate receives those overrides. The match runner validates keys and forbidden component override flags; its manifest stores both bot environment dictionaries. The frozen baseline code remains unedited.

### Short-clock reference matches

Two separately committed configs are run via the established experiment workflow, one for B1-v4 and one for B2-v4:
- 'experiment/Infra-stage2-b1-parity-profile', 'experiments/configs/Infra.json'
- 'experiment/Infra-stage2-b2-current-default', 'experiments/configs/Infra.json'
Both use four games, two swapped-color seed pairs, seed 349701, base 36 seconds/increment 0.4, maximum 160 plies, two Stockfish processes per bot, and a single match worker. Purpose is **smoke**, not full-clock strength; report invalid/protocol/clock failures and empirical outcomes without making a win-rate inference. The source revision and complete replay remain in distinct draft Release or verified fallback archives. A short head-to-head game score does not establish B1 action parity.

## Core reference corpus

Implementation: 'tools/stage2_corpus.py'; runner: 'tools/stage2_pipeline.py'; hosted workflow: '.github/workflows/stage2.yml'. The run is initiated only with commit marker '[run stage2]' on the infrastructure branch. No schedule exists.

**72 locally generated FoW games**, in 36 whole-game color-swapped blocks, source seed 7106:
- 18 blocks / 36 games: train; simple observation-only uniform versus visible-capture-preference opponent
- 6 blocks / 12 games: development; the same in-family policies with distinct game/seed blocks
- 6 blocks / 12 games: untouched same-policy holdout, with distinct game/seed blocks
- 6 blocks / 12 games: **opponent-style shift** holdout, uniform vs an observation-only king-pressure/center policy not present in training or development

Policies use only the current 64-square observation and inferred legal attempted actions through the public starter ObservationTracker, not referee truth. For every ply the builder regenerates each player's view, checks the chosen attempt is legal under the full referee, and stores:
1. 'corpus/observations/<split>.jsonl' — **pre-decision** records with an exact `online_inputs` allowlist: own color, current view, own information-history digest, observation-derived legal attempts and visible counts. Game/ply/split are join metadata, **not model inputs**. Crucially no selected action, target, opponent policy identity, full true board or future event is in `online_inputs`.
2. 'corpus/retrospective_labels/<split>.jsonl' — **offline only**, selected action (the prediction target), true sampled policy identity/opponent style, full true board/FEN, true opponent king square, true legal moves, retrospective attack labels. These files must never be read by live bot features.
3. 'corpus/replays/<split>/<game>.json' — full referee frames for independent rule reconstruction.
4. 'corpus/corpus_manifest.json' — allowed splits, per-game policy styles, game IDs and limitations.
5. 'corpus/game_registry.json' — replay SHA256, paired block, side assignment, seed and termination reason.
6. 'data_split.json' — machine-readable data lineage with train/dev/holdout IDs and file checksums.
7. 'referee_checks.json', 'baseline_audit.json', 'metrics.json', 'notes.md' — rule tests, baseline behavior, measured integrity and caveats.

**No data leakage** is checked on per-game and group-split boundaries. A color-swapped pair never crosses a train/test partition. The opponent-shift style appears only in the shift holdout. The chosen action, opponent-style identity, and full chess board are present *only* in retrospective-label or replay files, not in pre-decision model feature records. This is a logical/data-path restriction plus tests; the files are still readable in the archive, so later training scripts must continue to enforce the separation.

### Referee rules validated

The program checks moves, full board and both observations at each recorded ply by reconstructing games from scratch, plus targeted legality rules:
- Fog of War castling is pseudo-legal through attacked squares when the path is empty
- en passant under the local FoW referee (including visible capture destination)
- threefold repetition with FoW-specific EP position key
- 50-move terminal draw
- immediate 'King capturable' termination
- own pieces remain visible in both colors' observations

These are *local starter referee* rules. If official MIT arena rules diverge, that must be documented before attributing a scientific result to the arena.

### Critical statistical caveat

This corpus is **synthetic observation-legal**, not a strong-player research sample. It validates the parser, observation-time feature interface, legal histories and split construction. It does not justify training a high-performing opponent model (P2), learned value function (P7), or an Elo claim. Later stages must add permissioned full-clock bot replays and held-out opponents without changing the predeclared 72-game fixture split or leaking its holdout labels.

## Stage 2 acceptance

- All Stage 2 tests and historical tests pass; frozen code hashes unchanged.
- A hosted Stage 2 workflow records 72 valid source-linked games, complete split counts, >0 observations, 100% exact referee state/view replay reconstruction and special-rule checks.
- Static parity controls and black-box parity results saved *even if they disagree*. No false B1=B0 claim.
- Both B1-v4 and B2-v4 controlled short match runs successfully archive full replays or explicitly preserve error records; their scores have no strength inference.
- Corpus, metrics, model-free source, binary/source hashes, split plan and observed failures are packaged with checksums, **remotely read back and verified** from GitHub.
- GitHub draft PR and stage-progress tracker updated; next stage is Stage 3 only when user asks.

Do **not** silently call Stage 2 complete if all its data are unarchived; the team must be able to recover the manifest and replays later when writing the report.
