# Stage 2 Findings — Controls, Local Rules, and a Leakage-Safe Reference Corpus

**Status:** all measurement and archival acceptance criteria verified on November 22, 2026. The work is in [draft PR #6](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/6), on a separate infrastructure branch. This file documents actual evidence, not stronger-chess claims. No frozen bot, upstream repository, official MIT arena, or main branch was modified.

## 1. Canonical baseline definitions

| Label | Bot | Configuration | Interpretation |
| --- | --- | --- | --- |
| B0 | frozen obscuro_v4 | Untouched original and own pinned Stockfish 19/NNUE/helper | **Control for future playing-strength experiments** |
| B1 | eBotI | 21 explicit v4-like environment flags from tools/stage2_parity.py | Proposed emulation only, **not established action-equivalent** |
| B2 | eBotI | Existing default settings without overrides | Current experimental bot, distinct from B0 and B1 |

Nineteen frozen v4 source inventory entries were verified against tests/frozen_bots.sha256. Inventory file SHA256: 14841815a2b11e485647db5a3b187fb2e3d995017ba367eaba312f8eae90477e. Frozen v4 bot.py SHA256: 5817d30ae2ecd3ffe71da40ca1667d4576280bdb6f6424e44ace66c82fb3c15b. Stockfish NNUE SHA256: 1a298aa575a085434d29027978dc36867fe9c5bcea9376654b7a8eba1e52dfc2.

On the [canonical corpus and parity run 45073998777](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45073998777), **six deterministic shared-component checks passed**: root sampling, attacked-king weight, root/scan/depth/slice constants, move-clock budget, risk/value aggregate on controlled arrays, and FoW move classification. This does not establish whole-program equivalence.

A black-box probe compared both bots on the exact same public observation/action prefix, stopping each trial at its first divergence. B1-v4 made the same action in **6 of 9** comparisons, with **3 differences** and zero runtime errors. Even v4-v4, in identical process settings, agreed on only **10 of 11** comparisons, showing timing-sensitive variability; it does **not** identify whether B1-specific code or runtime noise caused the B1 differences. The scientifically correct conclusion is **B1 NOT proven equivalent**. Do not substitute B1 for frozen B0 in primary comparisons.

## 2. Short-clock bot-to-bot reference matches

Both experiments use 36+0.4 time control, four games/two swapped-color pairs, seed 349701, max 160 plies, one match worker, two engine processes per bot. All eight games were valid and ended via 'King capturable', with zero reported protocol/component failures.

| Controlled contrast | GitHub Actions run | W-D-L for candidate | Smoke score | Full archival evidence |
| --- | --- | --- | --- | --- |
| B1 v4-like eBotI vs frozen B0 | [45073041219](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45073041219) | **1-0-3** | 25% | [Permanent run catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/Infra-stage2-b1-parity-profile/research/runs/research-evidence-45073041219-1.json) |
| B2 default eBotI vs frozen B0 | [45073046202](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45073046202) | **1-0-3** | 25% | [Permanent run catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/Infra-stage2-b2-current-default/research/runs/research-evidence-45073046202-1.json) |

B1 run SHA b618abd0cd9ba735aec7321d0f0c092d9faf2214, archive SHA256 e381e573022fe905064346867e6ae7f887ed751464a74a3cae659cb635661cc6. B2 run SHA 1e98c1b605202d95e0995a109b2e5b3492ef9b64, archive SHA256 0d3665f03288acb5cd272aaeb6d8a4f70881fddd0f6367e6fda8bf0610773373.

**Interpretation:** four games and only two paired blocks cannot establish strength, equivalence, regression, or a useful confidence interval. Both reports explicitly say purpose=smoke. Each archive contains exact source SHA, game configuration, binary and network hashes, complete referee replays, outcomes, clocks, failures/diagnostics, and checksum verification. GitHub Actions uploaded each as a draft Release, downloaded its assets back, verified the archive/sidecar/catalog and permanently indexed the result.

## 3. Canonical reference corpus — strict pre-decision schema 2

**GitHub run:** [45073998777](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45073998777). Source commit 20e412827bded1e6352bcbc043a7c6d00ca7731a. Permanent [verified corpus catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/infra/stage2-baselines-corpus/research/runs/research-offline-evidence-45073998777-1.json). Draft GitHub Release contains a 354,506-byte compressed archive of 104 evidence files plus SHA256 and JSON catalog. Archive SHA256: ae507b8f113bacaec0e9f54b65a27ca210b60adcfdc371425047d8b2c885ddc3. Remote files were downloaded and verified in CI; a separate inspection of the full downloaded artifact checked representative rows of all four splits.

| Split | Paired blocks | Complete games | Pre-decision observations |
| --- | ---: | ---: | ---: |
| Training | 18 | 36 | 902 |
| Development | 6 | 12 | 310 |
| In-family holdout | 6 | 12 | 442 |
| Opponent-style-shift holdout | 6 | 12 | 536 |
| **Total** | **36** | **72** | **2,190** |

**72 of 72 full games** passed complete replay reconstruction, including every board/observation on every ply, for **100% referee reconstruction consistency**. Seven of seven targeted FoW checks passed: pseudo-legal castling through attacked squares, en passant, FoW repetition, 50-move draw, king-capturable termination, and visibility of all own pieces for both colors. Seventy-one synthetic games terminated by capturable king; one reached its explicit 100-ply synthetic cap. These starter-policy games have no chess clock and are **not** a representative competitive sample.

**Leakage-safe schema:** Each observations record has only join metadata (sample_id, game_id, split, ply) and a nested online_inputs dictionary with precisely six authorized predecision fields: side, view, own_history_sha256, legal_attempts, visible_enemy_count, visible_square_count. The chosen action/target, opponent-style identity, true board/FEN, true legal moves, and hidden king are stored **only in separate retrospective_labels files**, never in online_inputs. Game and split IDs are not allowed as learned live features. An explicit test adds a selected-action target to online_inputs and requires the audit to reject it.

Whole games stay together across train/development/holdout, and every color-swapped pair stays within the same split. The opponent-shift policy king_pressure appears only in the final 12 games, with both policy actors producing moves; future style-specific evaluations must select actions by the **retrospective target-actor style** rather than assuming every row in an opponent-shift game belongs to the new style. The generator uses only the player's current FoW observation and ObservationTracker legal attempts, never referee truth to choose a move. Independent reconstruction uses full truth only afterward.

**Important version boundary:** Prior Stage 2 archived runs 45073161259 and 45073516711 are retained as earlier validation/provenance, but their observation schema exposed the chosen action as top-level data. The canonical leak-safe baseline is the strict schema-2 archive 45073998777. Do not train/deploy on earlier records as if they have the strict online_inputs guarantee.

## 4. Project readiness and limits

P1 can measure belief-support and event probabilities with retrospective truth; P2 can score next-action likelihood without target leakage; P3/P4/P6/P9 can test referee-faithful information and toy games; P5 can derive hidden tactical event labels; P7 can train low-capacity residuals with separate targets and strict game splits; P8 can test budget policies in real game traces, but the synthetic corpus itself has no clocks. These are **infrastructure affordances**, not actual new algorithmic findings.

The synthetic games are insufficient for robust opponent-model or learned-value generalization claims. The two archived four-game reference matches are genuine bot-to-bot replays but still underpowered. Any later true strength result must be based on permitted, separately sourced full-clock games and untouched confirmatory seeds/opponents. These data shortcomings must not be disguised as a successful performance experiment.

No P1–P9 scientific intervention has been implemented, no full-clock playing-strength trial or official arena game has run, and no report has been drafted. The frozen B0 remains authoritative. For complete methodology, see STAGE2_DESIGN.md and stage0_preregistration.md.

**Next user-controlled stage:** Stage 3, independent P1–P9 first implementations and toy/offline validation. No automatic schedule or merge.
