# Stage 0 — Dependency DAG, implementation ordering and project independence

**Goal:** execute the nine research directions as separate scientific experiments while sharing necessary reproducibility infrastructure, without inventing a calendar schedule. The order below follows **technical prerequisites**, not dates.

## A. Necessary shared prerequisites

S1 — **Experiment-ID migration and evidence schema (Stage 1).** Current workflow accepts research IDs A01..F99 or Infra; new 'experiment/P1-v1-...' branches with 'experiments/configs/P1.json' will not automatically run until the workflow's validation/branch parser, archiver and config validators are updated and smoke-tested. Stage 1 must also preserve permanent *offline* evidence and model metrics, not just match replays. The feature runner must be able to tell feature-off parity from modified candidate behavior.

S2 — **Rules and reference control validation (Stage 2).** 'starter/referee.py' defines legal move attempts, visibility and terminal king capture; verify all bot-facing observation construction against it. B0 is frozen v4, B1 is actual decision-parity eBotI control, B2 is eBotI default. Existing old teammate matches may have worker-overlap confounds; do not blend them into control results.

S3 — **Independent offline data and game/outcome provenance (Stage 2).** A complete-game split, opponent-family holdout, observation-time feature capture, truth-as-label-only rule, paired seeds, and manifest SHA are required for all empirical projects. Some offline projects can be evaluated without training, but must still use held-out data.

The prerequisites form a gate: S1 + S2 + S3 → new intervention runs and claims. P9's tiny toy proofs may be developed before S3 but no empirical generalization claim can.

## B. Directed acyclic dependencies

~~~text
Stage 0: nine hypotheses, mathematical specs, preregistration
                   │
                   ▼
Stage 1: P1–P9 experiment IDs + archive + reproducible runner
                   │
                   ▼
Stage 2: legal/referee oracle ─ frozen B0/B1/B2 parity ─ held-out corpus
                   │
       ┌───────────┼───────────┬──────────┬───────────┐
       ▼           ▼           ▼          ▼           ▼
      P1          P2          P3         P5          P9
  posterior     opponent    contingent  risk        endgame
       │           │           │          │           │
       └─optional──┘        ┌──┴──┐       │           │
                             ▼     ▼       ▼           │
                            P4    P6      P7          │
                         info     strategic learned    │
                         value    solving  value       │
                            └─────┬───────┘            │
                                  ▼                    │
                            P8 metareasoning ◄─────────┘
                                  │
                         (integration only)
                                  ▼
                  verified full-clock final candidate
                                  │
                  archived evidence / report inputs
~~~

**Important:** Arrows after S2 are **practical opportunities for reuse**, not a requirement to combine mechanisms or to finish one entire contribution before another begins. Every project has a standalone v1 using B1/B2 and no outputs from the other new projects. For example: P4 can use the frozen baseline one-ply planner without P3; P7 can learn Stockfish residuals without P5; P8 can allocate baseline engine calls without using any P1–P7 algorithm. This separation is a non-negotiable scientific identification strategy.

## C. Orthogonality tests and shared-interface contracts

| Project | Input used in v1 | Single changed object | Hold fixed | Independence falsification test |
|---|---|---|---|---|
| P1 | Baseline weighted consistent states | State sampling/proposal approximation | Opponent π, value, search, clock | Feature off restores identical sampled-root distribution |
| P2 | Hypothetical legal boards + observed actions/events | Likelihood π_opponent | Belief cap, root sampling, payoff, clock | Same b and action choice when likelihood updates disabled |
| P3 | Baseline belief and one-ply action score | Future policy contingent on actual observation | b, π, payoff, per-move CPU | No hidden-state-specific future action for same own infoset |
| P4 | Action-conditioned own/opponent observations | Instrumental observation incentive | Immediate material payoff, π, risk | Equal-information-action pairs give equal bonus even if number of visible squares differs |
| P5 | Baseline b and candidate actions | Probability/utility assigned to hidden catastrophe | b, π, Stockfish budget | Capture vs quiet distinction, coefficient=0 restores B1 |
| P6 | Baseline roots and deep leaf values | Restricted game mixed strategy/security objective | Root posterior, leaf depth, clock | Toy equilibrium gap converges; pure optimizer is valid control |
| P7 | Baseline action features and fixed continuation target | Residual continuation value estimate | b, π, event risk, CPU | Zero residual gives exact baseline; no target leakage |
| P8 | Baseline action-value update traces | Selection/stopping rule for computations | b, π, utility and rules | Same total CPU; controller disabled matches reserve clock |
| P9 | Endgame legal information states | Certified reachability policy | Baseline outside certified domain | Disabled or outside domain returns baseline action |

**Data interfaces planned:** a versioned 'ObservationEvent' record with game_id, own_side, ply, own_view64, legal_attempts, public chronology, last own move, source SHA and 'time_of_availability'; a 'HypotheticalState' record with sampled legal board and weight and explicit marker 'not truth oracle'; a separate 'RetrospectiveLabel' containing hidden board, hidden action, later king/material events and forbidden-live flag; a 'DecisionTrace' with all candidate actions/values/clock and feature flags. Machine schema definitions and real implementation are **Stage 1/2**, not claims of code already present.

## D. Ordered feasibility gates for all nine

| ID | Smallest scientifically meaningful executable v1 | First gate to pass before tournaments | If gate fails |
|---|---|---|---|
| P1 | Importance-corrected danger-stratified sample of *existing* legal support | Tiny exact posterior, calibrated events at equal evaluations | Audit missing-support cause; cap repair only if justified |
| P2 | Fixed tiny style mixture + opponent-event likelihood update | Held-out action and visible-event NLL vs one-ply SF | Report negative predictive finding, don't run expensive games |
| P3 | Corrected existing infoset two-ply planning with strict clock | Two hidden worlds same view and opposed actions; accurate legality | Repair grouping/semantics before any strength test |
| P4 | Decision-focused VOI as cheap marginal action bonus | High-reveal but decision-irrelevant case scores ≈0 | Remove information bonus or change target; no double count |
| P5 | Quiet-material hazard predictor with capture exclusion | Held-out unseen-material probability calibration and no-leakage | Compare to HANG / safe-first before extending |
| P6 | Deep-leaf tiny game with exact CFR oracle | Exploitability gap and valid reach weights on toy game | Conclude solver implementation infeasible or incorrect |
| P7 | Ridge residual on observation-only features | Held-out correction gain and negative controls not leaking | Mark no predictive result, don't scale to RL |
| P8 | Cheap value-of-computation stop/slice selector | Equal-CPU action-regret and no extra late-clock forfeits | Revert to reserve clock |
| P9 | Small exact information-state reachability endgame solver | Exhaustive no-false-certificate proof on declared set | Narrow certified domain, no broad guarantee |

## E. When iteration is allowed

A project v2 is justified only when its v1 experiment identifies a concrete failure mode *within the same scientific object*. Examples:
- P1: capped support misses truth → history-valid repair; do not invent a separate opponent policy project within it.
- P2: mixture loses unfamiliar opponent → shrinkage/style adaptation; do not rebrand posterior calibration as prediction.
- P3: two-ply cannot predict attacks arriving after another hidden move → selective 3–5-ply expansion.
- P4: square-count bonus worthless → decision-focused VOI; if no incremental value once P3 is enabled, log redundancy instead of claiming additive benefit.
- P5: overdefensive quiet penalties → calibrated action-conditional capture propensity and material utility.
- P6: solver iterations insufficient → reduce tree and cache deeper leaves before promising equilibrium quality.
- P7: residual target biased by observed action → define simulated counterfactual teacher, keep new train/test split.
- P8: uncertainty proxy doesn't predict value-of-computation → use action margin and expected reversal probability.
- P9: full 8×8 belief space huge → prove restricted invariant class or produce adversarial counterexample, don't fake complete tablebase.

No v2 should simply tune five numbers until a short tournament is positive. Preserve hypotheses and parameter-selection history.

## F. Resource and science budgeting

The order of *first tests* should prioritize tiny exact rules and offline diagnostics, then launch small games, then full-clock validation of credible winners. CPU-only execution is likely; no user-provided GPU is established. Hardest feasibility risks are P6 deep-leaf solver, P7 off-policy value learning and P9 large information-state enumeration. None is guaranteed to yield a competitive strength gain. Treat 20-game matches as exploration, not definitive strength. Larger 180+2 confirmation may be split across independently archived immutable runs under GitHub's job cap.

There is **no requirement** to finish P1 before launching P2–P9 once shared prerequisites exist. Developing separate independent code branches and launching several smoke tests is compatible with the plan. However, choose hypothesis-guided v2 improvements only after collecting the corresponding v1 evidence, not on a preselected calendar.

## G. Stage 0 completion audit

1. All nine project specifications exist with original scientific question, mathematics, algorithm version path, actual repository touchpoints, baseline, primary outcome, negative control, and stop criteria.
2. Every legacy A01..F08 ID appears exactly once in 'research/consolidated_crosswalk.json'; F01, F07, F08 are marked support and not a tenth contribution.
3. Annotated source bibliography and prior-team novelty limits exist in 'research/stage0_literature_review.md'.
4. Main preregistration exists in 'research/stage0_preregistration.md'; exact seeds/splits remain intentionally pending Stage 2.
5. Branch/CI migration explicitly remains Stage 1; no code or tournaments were performed during Stage 0.
6. The planning PR remains draft; merging into main is not needed to proceed on a research branch.

**Next authorized action (only when user says 'next stage'): Stage 1 infrastructure upgrade, not Stage 3 coding.**
