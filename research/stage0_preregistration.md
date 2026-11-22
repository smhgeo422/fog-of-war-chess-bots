# Stage 0 — Global preregistration and experimental standards

**Scope:** All nine project hypotheses P1–P9; created before new bot implementations or research tournaments. This is a methodological preregistration **framework**. Exact game IDs, seed blocks, opponents, sample sizes and software environments must be instantiated and committed in Stage 2 *before* seeing new results. A prospective item without feasible data may be marked blocked, not silently substituted with an easier question.

## I. Hypothesis family and primary outcome hierarchy

| ID | Null hypothesis for independent experiment | Primary endpoint (held-out) | Secondary results required before a playing-strength claim |
|---|---|---|---|
| P1 | New state sampler/repair does not improve a correctly defined hidden-threat probability estimate | Game-clustered Brier for hidden king/material attack event at a pre-action observation | Support inclusion, ESS, root event recall, p95 CPU, then game score |
| P2 | History-adaptive policy does not improve opponent action/event prediction | Per-game action NLL on hidden referee-labeled opponent actions; observable-event NLL must also be reported | Normalization/floor, unseen opponent groups, belief rank, then game score |
| P3 | Contingent search has no better performance at fixed CPU than the existing two-ply method | Observation-consistent policy regret on preselected tactical fixtures | No strategy fusion on toy cases, decision reversals, future loss, CPU, then game score |
| P4 | Valuing/restricting information does not predict better next observations' decision value | Incremental action-sensitive VOI on matched outcomes where direct tactical value is controlled | Entropy/square-count baselines, opponent reaction, time and score |
| P5 | New calibrated danger utility does not improve catastrophic event prediction | Held-out Brier/calibration of quiet-move unseen material-loss or king-loss risk, with event fixed before coding | Capture/quiet split, false alarms, foregone material, clock, wins |
| P6 | Restricted resolver has no advantage over greedy strong-leaf policy at equal budget | Toy-game exploitability/security value with exact best response | Solver convergence, leaf depth, compute, worst-opponent score |
| P7 | A learned continuation residual does not improve prediction over Stockfish-only | Held-out game-clustered loss for fixed target (value MSE or outcome Brier, target frozen) | Action ranking with matched counterfactual rollouts, latency, matches |
| P8 | Adaptive computation is no better at fixed total CPU/clock | Offline matched-budget action-regret difference to high-budget reference | Controller overhead, timeouts, late-game clock, game score |
| P9 | Restricted endgame policy fails soundness or adds no verified conversion coverage | **Zero false winning certificates** on fully enumerated declared domain, and certified domain coverage | Worst-case plies, memory, natural-game occurrence, endgame match score |

**Interpretation hierarchy:** correctness > predeclared diagnostic/offline primary metric > full-clock game-strength evidence > engineering integration. Diagnostic accuracy alone is never called stronger chess. P9's logical verification replaces conventional statistical significance on its fully enumerated domain; natural-game Elo is only secondary.

## II. Frozen controls and factors

Before any new performance comparison, establish:
- **B0** unmodified 'bots/obscuro_v4', hash-verified by existing 'tests/frozen_bots.sha256'. B0 is not a source of code changes.
- **B1** 'bots/eBotI' with explicitly listed environment variables for v4-equivalent behavior, checked with recorded *action parity*, not merely name similarity. Known configuration flags alone do not prove parity.
- **B2** current team's eBotI default (may include HANG, SAFE_FIRST, EXACT_RISK, book, reserve clock). Config and source SHA must be frozen.
- **B3** *future* best validated research candidate; never preemptively label any version B3.
- For P1/P2/P5/P7, hold all unrelated models fixed and distinguish modified distributions from modified utilities; for P3/P4/P6/P8/P9, hold state posterior, book, opponent policy, binary, clock rules and seed assignments fixed unless explicitly the manipulated variable.

Reconstruct reference performance **with controlled single-worker CPU**. Old matched-games affected by oversubscription or nonuniform hardware are descriptive historical data, not pooled indiscriminately with new results.

## III. Experimental units, splits and allowed information

The independent statistical unit is **game or color-swapped opening/seed block**, not an individual move. Thousands of correlated plies from ten games do not create thousands of independent observations. Log both per-move sample size and per-game/opponent cluster count.

Offline replay truth—full hidden boards and hidden opponent actions—is allowed only for retrospective labels and validation tests. Features for **live action selection** may depend solely on what the course protocol delivers or what the bot can infer from those observations. Use a test-only 'truth oracle' explicitly denied to live evaluation. Feature records must store the exact information cutoff and an observation-history hash.

Split complete game IDs into training, development and untouched holdout, with separate opponent-group holdout when there are enough opponents. Near-duplicate opening seeds and color-swapped matched games stay in the same split. When training synthetic data from the referee, the validation generator must have independent seeds/initialization. The Stage 2 corpus manifest must record all provenance and licensing/course permission checks.

If external opponents or public arena replays are forbidden by course policy, do not fetch or train on them; generate local games or restrict to permitted data and label the resulting generalization limits.

## IV. Unit, toy and counterfactual gates

A new version cannot trigger research-strength matches before:
1. Python/C++ build, deterministic tests, exception/timeout safety and protocol correctness pass.
2. Feature-off mode matches B1/B2 control on fixed, recorded observation histories (parity within intended stochastic tolerance).
3. A small **reference oracle** test passes: P1 exact microbelief, P2 ambiguous action/event likelihood, P3 indistinguishable states, P4 irrelevant reveal, P5 fog capture vs quiet hazard, P6 known equilibrium, P7 leakage and shuffled-label control, P8 positive/negative VOC examples, P9 exhaustive winning-policy certificate.
4. Code, configuration and intended data split are already committed and source SHA logged.

If a toy test uncovers a preexisting bug in baseline code, fix on a separately documented infrastructure/validation branch with no accidental silent baseline shift; repeat the baseline comparison after repair.

## V. Screening, replication and confirmatory matches

**Screening**: predeclare ~20 games per candidate as an engineering budget example, with even number of color-swapped games from paired seed/opening blocks; game count can vary by runtime. These results guide whether to gather more evidence but cannot decisively establish a +1–5 percentage-point gain. Do not stop early just because first several games are wins. A match invalidated by protocol failure is a failure record, not a missing observation to discard. Record both game outcome and exact failure code.

**Replication**: use new seeds and at least one materially different local opponent style; never tune hyperparameters against the same match outcomes used for evaluation. Repeat on separate run SHAs to test reproducibility.

**Confirmatory**: pre-register candidate versions, hyperparameters, opponents, opening/color/seed blocks, CPU quota and 180+2 clock in a tracked config. Reserve a holdout opponent/seed set that was not used for version selection. Run enough games that a CI is informative, subject to computational practicality; do not call a small game count 'statistically significant'. GitHub job runtime cap (~350 min) may require separately archived immutable shards. Shards must have disjoint game IDs/seeds and exact common feature/config/binary/source SHA. Incomplete or failed shards remain visible and never get silently dropped.

**Statistical estimator**: for a complete valid match, score=(wins+0.5 draws)/valid games. Paired color-swapped block scores aggregated by block; report the 95% paired bootstrap interval over **independent blocks** or use an appropriate blocked estimator. Present full W-D-L, seeds, opponent distribution, time and protocol failures. If there are too few blocks, explicitly say the CI is unstable; don't substitute an unpaired move-level interval. Avoid cross-variant claim fishing after dozens of comparisons; prelabel Stage 4 exploratory screens, Stage 6 confirmatory comparisons and use independent holdouts.

**Practical-effect target:** for strength we care about approximately ≥5 percentage-point score improvement versus the relevant baseline at equal compute, but that is a prioritization threshold, **not** an arbitrary significance rule or a guarantee that sample sizes can detect it. Report all smaller measured outcomes with uncertainty.

## VI. Ablations and confounds

- One feature at a time for standalone projects; all variants use a consistent baseline protocol.
- **Opponent identity**: prevent identity leakage if not available under the course protocol. Compare familiar and new styles.
- **Opening book**: freeze same book on both sides unless a project specifically changes it; opening changes are shared engineering, not a project contribution.
- **Clock policy**: equal move time and CPU for P1–P7/P9. P8 alone manipulates timing, but equalize total budget, late reserve and forfeit accounting.
- **Stockfish**: pin executable/net hash and allowed process count; log engine nodes and evaluation depth.
- **Position cap**: record helper-vs-fallback switch, ESS, and state counts; no silent change across treatment/control.
- **Result labels**: distinguish probability a piece is attacked from probability the opponent actually captures it.
- **Target selection**: separate on-policy actual actions from counterfactual alternative actions requiring a defined continuation simulator.
- **GPU/training**: do not compare an expensive offline oracle deployed at chess time against a baseline with only two CPUs; report offline training compute separately from inference.
- **Multiple testing**: keep nine fixed families and version-level exploratory status; no unregistered 'new contribution' from convenient positive subgroup patterns.

## VII. Mandatory per-run data contract

Every archived experiment must include:

1. project ID P1–P9 and exact variant ID/version; hypothesis and primary metric;
2. full git SHA + branch + committed config SHA; target bot vs frozen baseline SHA;
3. Stockfish version/net SHA; environment variables, clock, CPU/core quota, worker concurrency, runtime platform;
4. game ID, opening block, paired color, RNG seed, opponent variant and policy/data source;
5. full per-game W-D-L outcome, reason, failures, timeouts, CPU/wall, plies, complete referee replay;
6. if offline: observation-only features, target construction method, train/test split manifest, model/checkpoint hash and evaluation rows or verified hashed derivatives;
7. aggregate estimate, uncertainty interval and labeled exploratory/confirmatory status;
8. exact artifact archive path, SHA-256, draft GitHub Release URL, machine index entry and verification report;
9. scientific conclusion, limitations, unsuccessful variants, and correct human/teammate/AI contribution attribution.

Existing 'tools/archive_research_run.py' can handle game runs; Stage 1 must additionally define durable *offline metric and model artifact* schemas, and verify them before presenting a successful outcome.

## VIII. Failure and stop-status vocabulary

Each version and project has one of:
- 'proposed' — not yet coded;
- 'implemented_unvalidated' — correctness/CI may pass, evidence still absent;
- 'toy_validated' — reference microtest passes;
- 'offline_supported' or 'offline_refuted' — predeclared metric measured, no strength claim;
- 'screened' — game screening recorded, inconclusive strength unless follow-up;
- 'confirmatory_supported', 'confirmatory_refuted', or 'inconclusive' — result with full uncertainty and limitations;
- 'blocked' — attempt made but scientific/compute/legal blocker documented;
- 'not_attempted' — explicitly no evidence.

Do not use the word 'finished' as a synonym for 'positive'. An audited negative result *can* close the project's investigation if enough evidence makes further iteration unjustified.

## IX. Stage 0/1 boundary

Stage 0 freezes **scientific questions, metrics, controls and planned algorithms**, not implementation outcomes. Stage 1 modifies CI identity and archival infrastructure. Stage 2 instantiates the precise data splits, benchmark settings and seeded tournament configs before exposure to new scores. Stage 3 begins algorithm coding. The user initiates each stage; no recurring research task, no automatic merges into main or official arena submissions.
