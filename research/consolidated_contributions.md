# Nine independent research directions for Fog of War Chess

**Research-design revision: 2026-11-22. Status: proposals, not implemented contributions or performance claims.**

**Decision:** replace the 46-item brainstorming backlog as the *primary execution plan* with **nine scientifically distinct algorithmic hypotheses**. Keep the original 46 items as a lossless idea inventory and as variations within these nine projects. Three additional items are shared experimental/engineering infrastructure and are explicitly *not* independent scientific contributions. Do not add a tenth idea or reclassify a contribution without a reason and the user's instruction.

**Repository context:** smhgeo422/fog-of-war-chess-bots, experimental branch infra/autonomous-experiments. Work on isolated branches. Leave the frozen v4 bot, upstream team repository, main, and official arena untouched without explicit authorization.

## A. Scope, the evidence we actually have, and the novelty boundary

The existing baseline maintains a consistent set of hidden boards (reported cap 200,000), weights successor boards using an opponent action likelihood, samples approximately 64 states for Stockfish-based move evaluation, and computes king-loss risk. Prior code implements an experimental observation-grouping two-ply correction ('FOW_INFOSET', off by default), fog material penalty ('FOW_HANG'), safe-first action selection, exact king risk, clock rules, and multiple search modes. **None of these may be claimed as a new algorithm merely by toggling a switch.**

Prior internal evidence from 'APPROACHES.md' reports: (i) an Obscuro-inspired large GT-CFR tree lost small comparisons to deep belief-weighted Stockfish; (ii) blindly increasing roots from 64 to 384 often reduced search depth and did not help; (iii) CVaR/worst-board penalties, global risk multipliers, and a crude 'blind-board' opponent policy did not show reliable wins. One previously noted confound is concurrent tournaments oversubscribing CPUs; these observations motivate controlled replication rather than categorical theorems. An existing 'material-leaks.md' analysis of 150 v4 and 179 Greek Gift games found 9.27 versus 7.78 pawn-points/game lost to unseen captures, with much of the gap in quiet moved/standing undefended pieces. This is *observational*, not evidence that a proposed penalty will improve game score.

**Control hierarchy:** B0=frozen 'obscuro_v4'; B1='eBotI' configured and action-validated for v4-equivalent behavior; B2=current eBotI default; B3=independently validated research winner. A proper one-factor experiment compares to the relevant B1/B2 control with identical engine revision, book, clock policy, CPU quota, seeds, and root-count budget. Declare deviations. Saved replays may contain full-board truth for *offline labels only*, never for the bot's playing-time decisions.

**Independence rule:** each project must have a distinct *latent variable, decision variable, or optimization objective*, a standalone ablation, and a specific result that would falsify its premise. A feature that merely invokes another project's algorithm is an ablation or integration, not a new contribution. Different projects can later interact, but a combination is not counted as an additional independent idea.

## B. Re-verified literature and what it supports

- **[L1] Zhang & Sandholm, ICLR 2026, "General search techniques without common knowledge for imperfect-information games, and application to superhuman Fog of War chess."** https://proceedings.iclr.cc/paper_files/paper/2026/hash/9705eec26e511d7844a591ce10c33a3f-Abstract-Conference.html — Obscuro shows that information-aware imperfect-information subgame search can succeed at superhuman Fog of War play; it does *not* imply a small course implementation will outperform a deep engine on limited CPUs.
- **[L2] Zhang & Sandholm, NeurIPS 2021, "Subgame solving without common knowledge."** https://proceedings.neurips.cc/paper/2021/hash/c96c08f8bb7960e11a1239352a479053-Abstract.html — knowledge-limited subgames avoid brute-force common-knowledge closure; safety is delicate.
- **[L3] Cowling, Powley & Whitehouse (2012), "Information Set Monte Carlo Tree Search."** https://eprints.whiterose.ac.uk/id/eprint/75048/ — diagnoses strategy fusion when determinization permits different actions in indistinguishable states.
- **[L4] Silver & Veness, NeurIPS 2010, "Monte-Carlo Planning in Large POMDPs."** https://proceedings.neurips.cc/paper/2010/hash/edfbe1afcf9246bb0d40eb4d8027d90f-Abstract.html — simulation-based belief tracking and information-conditioned planning; FoW additionally has an adversarial opponent.
- **[L5] Solinas et al., NeurIPS 2023, "History Filtering in Imperfect Information Games: Algorithms and Complexity."** https://proceedings.neurips.cc/paper_files/paper/2023/hash/87ee1bbac4635e7c948f3eea83c1f262-Abstract-Conference.html — consistent history sampling and subgame-root construction can be computationally difficult; history-valid particle proposals matter.
- **[L6] Clark, NeurIPS 2021, "Deep Synoptic Monte-Carlo Planning in Reconnaissance Blind Chess."** https://proceedings.neurips.cc/paper_files/paper/2021/hash/215a71a12769b056c3c32e7299f1c5ed-Abstract.html — belief particles and compact uncertainty abstractions can drive planning; RBC has a separate sensing action and is *not* the same game as FoW.
- **[L7] Fianchetto, "Speed, Belief, Guile, Caution to Win at Reconnaissance Blind Chess."** https://taufeeque9.github.io/assets/pdf/bachelors_thesis.pdf — practical inspiration for persistent beliefs, opponent-likelihood models and cautious action; again do not port RBC sensing mechanics verbatim.
- **[L8] Brown & Sandholm, NeurIPS 2017, "Safe and Nested Subgame Solving."** https://papers.nips.cc/paper_files/paper/2017/hash/7fe1f8abaad094e0b5cb1b01d712f708-Abstract.html — robust local re-solving must respect the surrounding blueprint strategy.
- **[L9] Farina, Kroer & Sandholm, AAAI 2021, "Faster Game Solving via Predictive Blackwell Approachability."** https://ojs.aaai.org/index.php/AAAI/article/view/16676 — predictive regret matching has practical convergence advantages on benchmark games; it does not guarantee a win-rate improvement for this bot.
- **[L10] Schmid et al. (2023), "Student of Games."** https://pubmed.ncbi.nlm.nih.gov/37967182/ — growing-tree CFR combines learning and local search; large training/search systems are not trivial replications.
- **[L11] Brown et al., NeurIPS 2020, "Combining Deep Reinforcement Learning and Search for Imperfect-Information Games (ReBeL)."** https://proceedings.neurips.cc/paper/2020/hash/c61f571dbd2fb949d3fe5ae1608dd48b-Abstract.html — framework for learned values plus search; a lightweight residual predictor is a pragmatic hypothesis, not equivalent to full ReBeL.
- **[L12] Hay, Russell, Tolpin & Shimony (2012), "Selecting Computations: Theory and Applications."** https://proceedings.mlr.press/r10/hay12a.html — meta-level decisions over what to compute; directly relevant to clock-budget allocation.
- **[L13] Gneiting & Raftery (2007), "Strictly Proper Scoring Rules, Prediction, and Estimation."** https://doi.org/10.1198/016214506000001437 — evaluates probabilistic forecasts; game-score and calibration measure different properties.
- **[L14] Gehnen & Stannat, FUN 2026, "Endgames in Fog of War Chess."** https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2026.21 — theoretical differences between FoW queen-vs-king and rook-vs-king endings create a concrete domain for special-purpose exact policies.

**Research gap (our inference, not a published theorem):** a strong, affordable course bot may be limited less by nominal chess evaluation depth than by (a) how uncertainty is represented, (b) whether future contingent actions are legal under its information, (c) how hidden tactical catastrophes are priced, and (d) when limited compute is spent. The following nine projects separately test those possibilities. The bibliography is a fresh verification of relevant published work; it is *not* a claim to have reproduced every proof or appendix of every paper.

---

## P1. History-consistent belief reconstruction and posterior calibration

**Independent question.** Is the dominant error that the true state is absent from, underweighted in, or poorly represented by the bot's belief set, even when its decision rule is unchanged?

**Mathematical object.** A posterior over hidden legal histories or boards, b_t(s)=P(s_t=s | own observation/action history). Formally, after an observed opponent transition o, b_{t+1}(s') is proportional to the observation likelihood times the sum over prior states and plausible opponent actions that legally transition to s'. State support and probability weight are distinct; a calibrated hazard marginal need not imply calibrated full-board probabilities. Proposed weighted sampling q(s) may deliberately overrepresent threatening states, but action expectations must use importance weights b(s)/q(s), with reported effective sample size.

**Substantial algorithmic variants.** (v0) Reconstruct the current team's weighted beliefs on held-out game histories, quantify actual state inclusion and posterior rank; (v1) capped, history-consistent stratified particles, with move-sequence legality and evidence-preserving rejuvenation; (v2) threat-stratified proposals corrected for sampling probability; (v3) learn compact piece-location proposal distributions that still pass legality/history filters; (v4) robust posterior-temperature ensemble only if a concrete calibration deficiency remains. Do not independently sample squares and pretend the resulting board is legal.

**Existing work / novelty.** The team already has position enumeration and a Stockfish-based likelihood; general particle filtering is not novel. Our possible contribution would be a *tested, history-consistent, decision-relevant proposal/repair mechanism* that is measurably better at detecting threats while keeping inference overhead fixed. [L4,L5,L6,L7,L13]

**Experiments.** Hold out full referee-truth replays by game and opponent; replay only legal bot observations to construct b. Measure full-state inclusion, weighted rank, ESS, enemy-square Brier/log score where a proper probability is available, hidden-attack recall in sampled roots, errors by phase and position cap, and per-turn wall/CPU. Test against exact small-support enumerations. At fixed Stockfish evaluation count, compare altered posterior versus baseline without changing the action selection function. Use next-turn unseen-material and game score as downstream checks, not as substitutes for posterior metrics.

**Falsification / failure.** If truth is usually retained and properly weighted yet losing actions persist, or if importance weights have unusably low ESS, posterior repair is not an empirically useful primary lever. Illegal states or full-board leak invalidate the method.

**Original IDs:** B01, B04, B05, B06, B07, E04. **Cost:** medium-to-large. **First gate:** an error-decomposition table, not a 20-game headline.

## P2. Opponent policy identification and online style adaptation

**Independent question.** Does modeling the *opponent's policy* from allowed histories yield better likelihoods and better best responses than a single fixed one-ply Stockfish proposal?

**Mathematical object.** P_theta(a_t | I_t^{opp}, z_t) where I_t^{opp} is what the opponent could have observed and z_t is a latent style mixture inferred *online* from legal observed actions. A probability floor prevents posterior collapse. The opponent's hidden observation is itself uncertain to us; infer over plausible opponent information, not a literal board with all our unseen pieces removed. Critically, prediction of opponent moves is the objective even with our posterior and our action planner held fixed.

**Algorithmic variants.** (v0) Replicate fixed Stockfish-1-ply plus uniform mixture and the already-rejected blind-board model as controls; (v1) fit/shrink lightweight style experts for capture preference, checking, development, tactical greed and king pressure; (v2) update mixture weights by likelihood on actual observed move consequences; (v3) infer small opponent-view particles where permitted and feasible; (v4) opponent-specific versus identity-agnostic evaluation, depending on whether identity is available under the actual bot protocol.

**Existing work / novelty.** Prior 'APPROACHES.md' measured a crude blind-board proposal as substantially worse than the full-board policy. Simply calling that proposal 'opponent-aware' would repeat a failed experiment. Our independent mechanism is a *history-conditioned predictive model*, validated by proper scoring rules before game play. [L1,L6,L7,L13]

**Experiments.** Split opponents and games temporally. Record observed legal actions, candidate action sets and observation likelihood without giving the model information unavailable at decision time. Compare held-out negative log likelihood, top-k recall, calibration, Bayesian regret against a fixed model, and downstream likelihood assigned to actual transition histories. Then vary only opponent likelihood inside the full bot; compare same CPU/clock games versus B1/B2 and across unseen opponent styles. Include a 'uniform floor' and no-identity ablation.

**Falsification.** If predictive gains disappear on held-out opponents, or slight opponent exploitation leads to serious worst-case regressions, do not claim general improvement. A behavior model can be good for likelihood without being a superior playing strategy.

**Original IDs:** B02, B03, B08, E05. **Cost:** medium-to-large. **First gate:** out-of-sample predictive advantage over the existing one-ply model.

## P3. Observation-consistent contingent tactical planning

**Independent question.** Does perfect-information evaluation cause optimistic strategy fusion, and can a shallow *contingent policy* remedy that bias without surrendering deep Stockfish tactical accuracy?

**Mathematical object.** A future policy maps a *future information set* (observation history), not a hidden true board, to a legal action: pi(o_{t+1}) in A(o_{t+1}). For root move a, optimize E_{s,r,o}[U(s,a,r,pi(o))] under the observation-consistency constraint, rather than E_s[max_{a'} U(s,a,r,a')] where different hidden states improperly select different replies. The discrepancy can be estimated on matched tactical cases.

**Algorithmic variants.** (v0) Unit test the existing 'FOW_INFOSET' implementation, especially legality and grouping by exactly the view that will be observed; (v1) two-ply observation-grouped tactical correction with calibrated fallback; (v2) targeted 3–5-ply extensions and repeated observation grouping; (v3) cache subtrees across turns only when observation-history and rights/repetition invariants match. Search remains among a restricted number of moves, states, and opponent replies.

**Existing work / novelty.** The repository already has a two-ply grouping correction; it must be validated and extended, not reintroduced as a new algorithm. Obscuro and ISMCTS already address imperfect-information search in general. The research contribution would be **a budget-matched correction preserving our specific strong deep-evaluator baseline**, not a novel invention of infosets. [L1,L2,L3,L4]

**Experiments.** Construct toy worlds where two true states look identical but favor incompatible continuations; verify the proposed policy chooses one observation-consistent response. Reproduce baseline action rankings on saved observations with and without the correction. Measure strategy-fusion gap, decision reversals, subsequent 2–5-ply material/king losses, number of engine calls, p95 per-move CPU. Compare fixed-depth search and the existing two-ply mode at matched CPU. Only then run paired matches.

**Falsification.** If correction costs more Stockfish depth than the avoided false optimism is worth, or policy grouping is incorrect, abandon that variant. A decrease in offline tactical regret without a matching robust game benefit must be reported as such.

**Original IDs:** A01, A02, A07. **Cost:** medium-to-large. **First gate:** exact toy counterexample plus reliable no-leakage implementation.

## P4. Strategic value of information and information denial

**Independent question.** Can a move be selected *because it changes who will know what*, beyond its immediate tactical/material value? This is distinct from P3: P3 avoids impossible future policies; P4 assigns **positive or negative decision value to observations themselves**.

**Mathematical object.** Approximate the action-conditioned continuation value of information:
VOI(a) = E_{o | a}[max_{u in A(o)} E[U | o,a,u]] - max_u E[U | a,u].
This is not the information entropy reduction H(b)-E H(b|o); information has instrumental value only when it changes a good future decision. For denial, evaluate how a changes the opponent's legal observation and resulting distribution over their future actions.

**Algorithmic variants.** (v0) Identify positions with alternative moves of nearly equal baseline tactical value but materially different information exposure; (v1) one-turn lookahead decision-focused VOI with no double-counting of material or direct search value; (v2) attack-line/own-piece exposure model for the opponent's next view; (v3) deliberate non-revealing or misleading tactical actions with a fixed safety constraint. Bluffing is not just adding random moves; test induced incorrect opponent responses.

**Existing work / novelty.** Obscuro already reasons about signaling and private information; this is not the discovery of information value. The concrete hypothesis is that an explicit **decision-focused** information term can outperform simple square-count or entropy heuristics under a course compute budget. [L1,L3,L4]

**Experiments.** Use offline matched-action sets controlling for material, king risk and Stockfish score. Measure realized observation change, how frequently information alters later choices, posterior action regret given information, opponent-response likelihood and actual game performance. Construct no-benefit cases where observing more squares cannot change the best future action: VOI should be approximately zero. Test a 'reveal-more' heuristic as a negative control.

**Falsification.** If calculated VOI reflects only higher immediate tactical value, or the information term does not predict an actual changed future choice, it is not an independent contribution. Do not equate deceptive behavior with robust improvement without adversarial evidence.

**Original IDs:** A03, A04, D01. **Cost:** medium. **First gate:** matched positions demonstrating instrumental rather than merely geometric information value.

## P5. Calibrated catastrophic risk and hidden-material preservation

**Independent question.** Does the scoring rule systematically misprice immediate king loss and future hidden-material catastrophe, so that better *utility calibration* wins more games even with the same posterior and search?

**Mathematical object.** Calibrate P(KingCaptured | b,a), P(UnseenMaterialLost_{1:3} | b,a), and P(eventual win | h,a) separately. A playing utility could use E[terminal game reward | h,a] with calibrated imminent failure probabilities, instead of mixing a raw king-risk probability and tanh-scaled centipawn values with an arbitrary scalar. We must avoid treating any one heuristic coefficient as the actual probability of loss.

**Algorithmic variants.** (v0) Reproduce existing 'FOW_HANG', 'FOW_SAFE_FIRST', 'FOW_FOG_TAX', exact risk and risk-lambda experiments under clean controls; (v1) predict quiet-move undefended material loss separately from favorable fog captures; (v2) two- or three-ply exposure/capture-propensity model; (v3) calibrated win-probability conversion for king threats, including losing-material-but-live-king cases; (v4) conditional anti-hunt/king-hunt policies driven by confirmed risk estimates. A trained immediate hazard predictor belongs here, rather than inventing another contribution called 'ML hazard'.

**Existing work / novelty.** The internal 'material-leaks.md' describes a 9.27 vs 7.78 pawn-points/game loss gap and says the excess is concentrated in quiet exposed or standing undefended pieces. Several defensive heuristics already exist, including failed global risk multipliers. Our contribution requires **new calibrated, selective hazards and causal ablations**, not another constant penalty. Proper probability validation and the correct terminal game objective matter. [L7,L13,L14]

**Experiments.** Build an offline hazard-label dataset from refereed replays: observations at decision time are features, later full-board outcomes are labels only. Split by game/opponent; report reliability curves/Brier score, discrimination and error by material class, quiet/capture split, and game phase. Construct situations where a fog capture has positive expected recapture trade, so an indiscriminate 'avoid fog' rule should fail. In controlled games record hidden-material losses, king captures, active-play reduction, W/D/L, and interaction with safe-first. For every claimed change, show what portion of measured improvement is driven by fewer true catastrophic decisions rather than mere passivity.

**Falsification.** If offline calibration improves but game score falls or clock cost dominates, report a calibration improvement without claiming strength. Prior penalties may already saturate the useful effect.

**Original IDs:** C01–C08, E01. **Cost:** medium. **First gate:** calibrated hidden-material-risk model on held-out games, stratified by move type.

## P6. Bounded game-theoretic re-solving and robust mixed strategies

**Independent question.** When the opponent may strategically exploit a predictable policy, can a small imperfect-information *mixed strategy* be more robust than any greedy best-response heuristic? Unlike P2 this optimizes **robustness/exploitability**, not the prediction of a specific opponent's next move; unlike P3 it explicitly solves a local strategic game.

**Mathematical object.** A restricted zero-sum extensive-form game with action-observation infosets, credible prior-reach/opponent-root distributions and continuation values. Regret matching / predictive CFR+ approximates a mixed strategy; compare approximate exploitability, security value and equilibrium gap on small known games. Blueprint preservation and alternate values constrain unsafe local deviations; do not assert a theoretical safety guarantee for an unverified approximation.

**Algorithmic variants.** (v0) Reproduce internal C++/Python GT-CFR failed settings under controlled CPU; isolate impact of shallow leaf evaluations; (v1) solve exact tiny toy imperfect-information games with known solutions; (v2) 3–6 root actions, 8–32 belief states, deep cached Stockfish leaf values and bounded regret iterations; (v3) blueprint-aware Resolve vs Maxmargin ablations and root-prior mixtures; (v4) controlled purification versus mixed play; (v5) opponent population stress tests / PSRO-lite **inside this same strategic robustness contribution**, not an additional idea.

**Existing work / novelty.** The team attempted large GT-CFR and lost small matches, probably because evaluator depth and solver budget traded off badly. Obscuro, knowledge-limited solving, safe re-solving and PCFR+ are published methods. The contribution is an empirical/theoretical case for or against **small, evaluator-preserving game-theoretic corrections** on this course hardware. [L1,L2,L8,L9,L10]

**Experiments.** Check equilibrium/regret convergence on Kuhn-poker-like toy games, a constructed small fog tactical game, and adversarial policy-matching cases. Hold leaf evaluation quality fixed while varying CFR iterations, root count, expansion asymmetry, blueprint, and mixing/purification. Compare average score *and* worst-opponent/population score under matched CPU, with uncertainty estimates and deterministic seeded controls. If solver exploitability improves on toy games but full FoW win rate degrades, explain why.

**Falsification.** Solver with unresolved regret, incorrect counterfactual reach weights, or weaker Stockfish leaf quality is not an interpretable test. If no feasible subgame budget passes all toy checks, stop after a documented negative result; do not pretend this is ready for the final bot.

**Original IDs:** A06, A08, D02–D07. **Cost:** large / exploratory. **First gate:** exact small-game correctness and actual runtime feasibility.

## P7. Learned continuation-value correction, not another heuristic penalty

**Independent question.** Can supervised learning predict *FoW-specific long-run game utility* missed by perfect-information Stockfish, without access to hidden truth at play time? This targets **value-function approximation**, not posterior reconstruction, opponent behavior or immediate capture risk.

**Mathematical object.** V(h,a) ≈ g(V_Stockfish(b,a), f_theta(phi(h,a))), where the correction uses permitted observation/history features, belief uncertainty summaries and perhaps recent search diagnostics. Train on held-out outcomes or carefully defined multi-ply counterfactual targets, with explicit target selection bias and game-level clustering. Constrain the model to be small and fast enough for CPU inference; retain a zero-correction fallback.

**Algorithmic variants.** (v0) Make a legal feature/target audit and partition data by game/opponent/time; (v1) regularized linear or small tree-based residual predictor for 3–10-ply FoW value changes; (v2) rank candidate moves using learned residual at a fixed engine budget; (v3) distill a strong offline observation-consistent search teacher (P3 is only the teacher, not part of the learned model); (v4) consider brief imitation/self-play fine-tuning **only if labels, resources, and independent validation justify it**. Full tabula-rasa deep RL is a separate high-cost *variant of this learned-policy direction*, not a promised achievable experiment.

**Existing work / novelty.** Student of Games, ReBeL and RBC synoptic planning establish broad value/policy-learning precedents. A novel result here would be a precise, leakage-safe small correction that adds predictive quality beyond Stockfish on **this team's** hidden-information failures and has measured playing value. [L6,L10,L11,L13]

**Experiments.** Use time-/opponent-held-out games and features from the same information available to the bot at each decision; avoid distributing correlated positions across train and test. Compare value MSE/calibration, held-out move ranking on matched counterfactual cases, inference latency, and candidate-vs-baseline game score. Negative controls: random labels, history-shuffled features, Stockfish-only, constant bias, and an immediate-risk-only model. Report performance by game phase and opponents. If training targets are biased by the behavior policy, explain counterfactual limits instead of calling the model causal.

**Falsification.** Offline accuracy that doesn't improve chosen decisions or games is not sufficient. Any use of future hidden state as input or leakage through train/test splits invalidates the result.

**Original IDs:** E02, E03, E07. **Cost:** medium pilot, very large full self-play. **First gate:** leakage-safe data and honest held-out predictive gain.

## P8. Rational metareasoning under a hard chess clock

**Independent question.** Given a fixed information-state evaluation algorithm, can the bot learn *when another Stockfish call or information-aware search is worth its time*? This is a different objective: allocate computation, rather than change the posterior or evaluation function.

**Mathematical object.** At a decision, estimate value-of-computation VOC(c) = E[max_a estimated U_after computation c] - max_a estimated U_now - lambda·time(c) - opportunity cost of future moves. Computations include one more root sample, deeper engine evaluation, more tactical replies, or more CFR iterations. A stopping policy should approximate positive marginal improvement under a fixed clock. Estimate VOC without looking at withheld true-board state during play.

**Algorithmic variants.** (v0) Reproduce constant 64-root depth/clock controls and prior breadth-vs-depth loss; (v1) instrument value stability and near-tie action margins over incremental Stockfish calls; (v2) choose roots versus depth based on ESS, king danger and action disagreement; (v3) move-specific, game-phase-dependent clock allocation with reserve against flagging; (v4) amortize search across turns only with correct cache state, if doing so measurably reduces work.

**Existing work / novelty.** The team already has a reserve clock and tested crude uncertainty/time heuristics; generic rational metareasoning is a long-established area. Our empirical contribution would be a *trained or calibrated marginal-computation allocation rule* that lowers decision regret or increases strength **at exactly the same total compute and time-forfeit risk**. [L10,L12]

**Experiments.** Replay budget curves on held-out observations: decision ranking and marginal value as a function of extra computations. Include a matched-total-CPU and matched-clock comparison; use p95 wall time, per-move timeouts, total Stockfish nodes, action-choice stability and score. Randomly assign fixed-budget controls to avoid confounding hard positions with increased compute. Always include a rule that stops before the referee limit.

**Falsification.** If apparent gains come from giving a variant more compute or selectively omitting flag losses, they don't count. Predictors should show incremental benefit over a simple reserve rule, not only over an intentionally weak clock.

**Original IDs:** A05, F02, F03, F04, E06. **Cost:** medium. **First gate:** action-stability/VOC curves and equal-budget improvement.

## P9. Information-state endgame conversion and king pursuit

**Independent question.** In small-piece endgames, can we exploit special properties of Fog of War visibility and capture objectives to use *provable or exhaustive information-state policies*, instead of relying on perfect-information chess's mating heuristics?

**Mathematical object.** A restricted endgame belief-state reachability game: classify actions and observation branches that force king capture under the FoW referee rules versus actions that allow indefinite escape. Depending on which endgame and knowledge assumptions are satisfied, use backward reachability/dynamic programming on small states and certified invariants. Never generalize a restricted guarantee to arbitrary midgames.

**Algorithmic variants.** (v0) Reproduce tiny-rule legality and observation tests using the existing referee; (v1) implement state-space searches for limited king+queen versus king and compare to baseline tactic; (v2) prove/validate small tablebase cases and identify situations where king+rook versus king cannot force conversion; (v3) extend to safe king pursuit under uncertainty when pieces remain, only if correctness permits. Opening repertoire and packaging do not belong to this mathematical contribution.

**Existing work / novelty.** Gehnen & Stannat (FUN 2026) already prove important K+Q, K+R and K+2R distinctions. Reimplementing their theorem is **not** a novel discovery. A credible contribution would be a *sound, efficient endgame policy under our bot's actual observation protocol* and quantified practical impact, clearly attributing the published theory. [L14]

**Experiments.** Enumerate restricted positions and observation-equivalence classes; verify each recommended action against all feasible hidden states. Measure guaranteed-conversion rate when guarantees apply, worst-case number of plies, false guarantees, CPU/memory and score on held-out endgame setups. For whole games, measure endgame frequency and conversion quality after correct material reduction; don't infer broad Elo from an artificially enlarged endgame test set.

**Falsification.** Any wrong 'forced win' certificate is a critical failure. If accessible endgame states are too rare or full-state restrictions too stringent, this can be a rigorous small negative/limited contribution rather than a top-level winning feature.

**Original IDs:** F05, F06. **Cost:** medium-to-large. **First gate:** exact toy/endgame certification with full observation-consistency.

---

## C. Three original items that are not independent scientific hypotheses

- **F01: Opening protocol / repertoire.** Shared match-control or optionally tuned opening-book engineering. Freeze the same opening distribution for treatment/control; don't claim book tuning as an independent theoretical result by default.
- **F07: CPU, packaging and protocol optimization.** Necessary correctness and performance engineering. Measure and report overhead; it does not establish an algorithmic FoW contribution by itself.
- **F08: Hybrid portfolio arbitration.** *Integration/ablation*, not a tenth scientific project. After independent projects pass their gates, build an integrated candidate and test one-by-one and pairwise interactions. Merely combining P1/P3/P5 gains is not a new idea; report genuine interaction only if supported by its own controlled tests.

Every one of the 46 previous IDs maps to exactly one of P1–P9 or the shared-engineering group in 'research/consolidated_crosswalk.json'. This is an accounting map, not a commitment to implement every legacy sketch.

## D. Research independence audit: what would falsify each contribution

| Project | Core thing changed | Primary evidence | Distinct from nearest neighbor |
|---|---|---|---|
| P1 | Posterior / state-support estimator | Coverage, rank, proper risk calibration, ESS | P2 predicts actions; P1 tracks hidden board states |
| P2 | Opponent policy likelihood | Held-out next-action log loss / actual move prediction | P1 state inference can be held fixed |
| P3 | Legal future contingent policies | Strategy-fusion gap, tactical continuation regret | P4 rewards information; P3 enforces consistency |
| P4 | Information as instrumental action value | Decision-sensitive VOI and opponent revelation | P3 may choose same move without info incentive |
| P5 | Utility of hidden tactical catastrophe | Calibrated event probabilities, hidden material loss, W/D/L | P1 posterior is frozen for this intervention |
| P6 | Mixed game-theoretic re-solving | Toy exploitability / security value + full-game robustness | P2 optimizes prediction/exploitation, not equilibrium |
| P7 | Learned long-horizon value | Held-out residual forecasting and action ranking | P5 handles immediate risk; P7 handles downstream payoff |
| P8 | Selection of computations | Accuracy/strength per CPU second under equal clock | Any planner/value function is held fixed |
| P9 | Restricted endgame winning policy | Sound reachability guarantee on exact endgame sets | Not generic tactical risk or one-ply evaluation |

**No forced additive architecture.** Each project should be evaluated as an alternative or a controlled single-component intervention on a frozen baseline. Only after independent validation should a separately labeled *integration experiment* test combinations.

## E. Experimental protocol and honest reporting

1. **Audit before coding.** Check prior branches and notes, reproduce each existing control, verify B1 parity with frozen v4 by actual move decisions on saved observations, and separate historical teammate work from new work.
2. **Within-project variants.** Use 'experiment/P1-.../v1', etc. in naming/metadata; changes should share one hypothesis and remain individually reversible. The existing CI expects a legacy letter-number ID (A01–F99); until upgraded, map P1–P9 to canonical existing IDs for workflow triggers or update the runner on a dedicated infrastructure branch and validate it *before* research batches. Don't assume the new naming works without testing.
3. **First unit-level gate.** Toy instances and negative controls must pass before spending time on full matches. State estimators must be history-correct; risk labels must be leakage-safe; solvers must converge on tiny games.
4. **Offline gate.** Hold out games/opponents/periods; proper likelihood/calibration metrics where applicable; source files record data provenance. Keep full-board truth offline as labels only.
5. **Short-clock gate.** Even paired-seed, alternating-color 20-game matches are *screening*, not reliable evidence of small improvements. Record W/D/L, uncertainty, CPU limits, Stockfish version, extra/inherited env vars, timeouts, replays and adverse-game examples.
6. **Confirmatory gate.** Freeze method and hyperparameters; use independent opponents/seeds and 180+2 full games where possible. Account for paired games, multiple comparisons, limited N, correlated training/replay states and the prior team's oversubscribed CPU confound.
7. **Archive and update.** Write commit SHA, config, hypothesis, complete raw replays, manifest, per-run machine-readable report, failure codes, uncertainty, and SHA-256 into the existing archival pipeline. A result is complete only after run evidence has been retrieved and verified.
8. **Scientific conclusion.** One of validated benefit, validated negative, inconclusive, infeasible/time-limited, or untested. Do not mark an algorithm 'successful' because it runs or because its loss is lower on selected training data.
9. **Integration only after independence.** Candidate combinations are secondary engineering experiments with explicit single-component ablations and no implied novelty.
10. **Authorization.** User directs when to launch batches. No scheduled task, automatic branch merge to main, or official arena submission.

**Proposed future step, not started here:** lock these nine project definitions as the project taxonomy; design a precise execution DAG and expected artifacts per stage; only then initiate coding or tournaments when requested. This document itself is a research plan, not evidence that any of P1–P9 were implemented.

## F. Legacy idea coverage

The exact crosswalk is machine-readable in 'research/consolidated_crosswalk.json'. Counts: P1=6; P2=4; P3=3; P4=3; P5=9; P6=8; P7=3; P8=5; P9=2; supporting=3. Total **46**. Original descriptions, contributions, and source references remain preserved in the old backlog and registry; do not delete them.
