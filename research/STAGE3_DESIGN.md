# Stage 3 — Nine separately falsifiable algorithmic v1 kernels

**Source-of-truth specifications:** 'research/projects/P1/proposal.md' through 'research/projects/P9/proposal.md'. **Status:** Stage 3 first-version algorithm/toy validation completed: 334 passing hosted tests and nine independently re-downloaded, SHA256-verified GitHub evidence archives. **Not playing-strength evidence.** See research/STAGE3_FINDINGS.md for results and limitations. This is a research *algorithm kernel* stage, not an integrated new playing bot or an unbounded all-nine full trial. Science-driven improvement and full-clock screening belong to later stages.

Every new kernel lives under tools/stage3/Pn.py and can be tested standalone. All nine branches now store permanent per-run catalogs, and each project has findings.md plus a v1 evidence ledger. Live playing-bot feature parity, real opponent held-out scores and full-clock strength experiments are explicitly untested and require Stage 4 or later. tools/offline_jobs/stage3.py runs the selected kernel with the tracked project/version/seed, archives the exact source SHA and source-file hash, and writes machine-readable results including negative findings. The same code and tiny deterministic toy trials are repeated from two runs with the same seed for stability. Full biological/game data never enter a toy model unless explicitly stated.

## v1 prototype matrix

| ID | Actual v1 mechanism | Exactly tested mathematical object | Explicit research gap before real chess test |
|---|---|---|---|
| P1 | Threat mixture proposal q=(1-alpha)p+alpha r with positive posterior support and corrected p/q importance weighting; ESS reporting | Exact four-world rare attack event probability versus sampled MSE, weighted risk and seed-stable ESS | Does not regenerate legal histories or improve belief posterior support; need real hidden-state posterior evaluation and fixed Stockfish roots |
| P2 | Positive-floor softmax style experts and Bayesian update using **observed event equivalence classes** marginalizing hidden opponent moves | Event-censored online style posterior, retrospective hidden action NLL on simulated capture/quiet agents | Opponent information distribution unknown; must use approved replay evidence and unseen-style NLL, never hidden moves as online input |
| P3 | Future observation+public-history-bucketed action-contingent evaluator with one feasible continuation per information set | Strategy-fusion gap with identical-view contradictory-world counterexample, distinct-view allowed actions and budget fallback | Current eBotI infoset planner already exists; v1 is a standalone exact value oracle, not yet CPU-matched Stockfish integration |
| P4 | Root-action **instrumental** value of future observation with matched direct/tactical value; no entropy proxy | Equal-visibility different-decision-value counterexample; value zero when optimal next action unchanged | Must measure real action-conditioned observation changes and avoid P3 double counting |
| P5 | Shrunk class-conditional hidden-event probability via Beta prior; selectively penalize exposed quiet moves, not captures | Proper Brier score against known synthetic event generator and class-stratified calibration | Need referee-derived retrospective attack/material labels with game-blocked holdouts and payoffs on a common utility scale |
| P6 | Restricted zero-sum regret matching+ with exact simultaneous best responses, security value and duality gap | Matching pennies/RPS equilibrium and exploitability oracle (pure predictable vs equilibrium mix) | Normal-form tiny solver is NOT full FoW extensive-form, safety of re-solving or deep cached Stockfish leaf integration |
| P7 | Strict allowlisted pre-decision feature map and ridge-regularized bounded residual, with ridge selected on development | Known synthetic counterfactual continuation teacher, held-out MSE, shuffled-target control, zero correction baseline | Must replace synthetic teacher with explicitly sourced fixed-policy rollouts/Stockfish targets and measure separate FoW action ranking |
| P8 | Bayesian-martingale-consistent exact one-computation VOC; hard clock reserve and overhead bound | Near-tie computation worth doing, decisive root skip, clock reserve enforcement | Computation-result distribution needs calibration to real Stockfish wall/node curves and equal total CPU |
| P9 | Bounded-horizon universal reachability solver choosing one common action across hidden worlds and all adversary outcomes | Two hidden-world probe then capture, escaped counterexample invalidates guarantee, real FoW hidden KQ/K observation parity | Only finite abstract graph certified; NOT global KQ-v-K theorem nor 8x8 endgame conversion policy |

**Independence boundary:** P1 changes which valid posterior worlds are evaluated (belief support/representation), P2 predicts adversary actions, P3 enforces a feasible contingent plan, P4 values information-changing root moves, P5 calibrates terminal/material loss utilities, P6 optimizes restricted-game security against adversarial policy, P7 predicts long-run utility residual from online features, P8 prices additional **computation**, and P9 solves restricted endgame reachability. Sharing referee or statistical primitives does not make these the same scientific hypothesis.

## Pre-registered run protocol for each project

1. Branch 'experiment/Pn-v1-toy-kernel' from pinned 'infra/stage3-independent-kernels'; commit tracked 'experiments/offline/Pn.json' with purpose=research, variant=v1, seed and single explicit hypothesis.
2. GitHub validation runs every regression test including frozen bots, referee rules, strict Stage 2 leakage schema, and the nine toy-kernel tests. A failing correctness test blocks offline execution.
3. A commit message containing '[run offline]' triggers the Stage 1 runner to construct a unique manifest containing exact source SHA, module digest, tested hypothesis and predeclared seed.
4. The independent script reports numerical primary metric and denominators, full toy evidence, known scientific limitations, data provenance and CPU wall time. An unfavorable metric is archived, not relabeled.
5. Archive to draft GitHub Release (or verified branch-backed fallback), re-download, validate tar.gz, sidecar and full file inventory, and write a permanent 'research/runs/' index on that exact experiment branch.
6. A future amendment creates a separate variant/branch; do **not** overwrite previous archives or reinterpret synthetic diagnostic results as strength.
7. Project scientific results can enter Stage 4 screening only with live bot integration and/or approved referee-replay data that satisfy that project's proper predictive endpoint. No code in this stage is a replacement for the unchanged frozen B0, and no performance claims follow from an exact toy result.

## Falsification and validity rules

- **P1:** check q_i>0 for all p_i>0, weight correction, ESS; proper calibration may worsen even when dangerous worlds are sampled more. Disallow arbitrary square-filled "belief repair".
- **P2:** if two hidden actions cause the same observable event, the online posterior update must be the same. Blind-board pseudo-observations cannot be mistaken for actual opponent view.
- **P3:** the same future information set cannot prescribe contradictory actions. Restrict to FoW legal attempts and return a frozen-root fallback on deadline.
- **P4:** visibility of many irrelevant squares has exactly zero instrumental VOI. Reject VOI identification when direct action payoffs differ; do not count P3's future information value twice.
- **P5:** a globally negative fog-capture penalty is invalid because many captures are profitable; report Brier by quiet/capture risk class and avoid calling probability a payoff.
- **P6:** solve known Nash restricted games with exact best responses and explicit duality gap; a mixed strategy can be necessary even when greedy actions appear attractive.
- **P7:** any forbidden retrospective target, hidden FEN or opponent-policy identity must be rejected by feature extraction. Chosen-action game outcomes do not identify causal counterfactual Q.
- **P8:** reject a proposed computation model whose posterior expectation violates the current action-value mean; stop if reserve/cost exceeds remaining time.
- **P9:** all hidden worlds sharing an observation must select one action, every opponent reply must be handled, and a losing branch invalidates the certificate. Do not claim a general endgame theorem from a bounded toy witness.

## Negative and positive evidence scope

A toy result can prove a mathematical implementation property or expose a counterexample. It **cannot** establish an improvement in true opponent prediction, posterior calibration, FoW tactical regret or chess game score. The playing bot, frozen B0 and hidden-referee rules remain unchanged; Stage 4 exists specifically for independent offline and short-game screening at properly matched computational budgets.

**No scheduling:** each stage starts only when requested by the user. No merge to main or official arena submission.
