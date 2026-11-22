# Working Report Outline — MIT 6.7980 Fog of War Chess

**Working title:** *Beyond Determinization: Belief-Weighted Chess Evaluation and Information-Aware Decision-Making in Fog of War Chess*

**Status:** living outline, **not** a finished report. Initiated November 22, 2026. Update alongside experiment results. The exact final title and claims depend on evidence.

**Repository:** [team upstream](https://github.com/ernjg/fog-of-war-chess-bots) · [working fork](https://github.com/smhgeo422/fog-of-war-chess-bots) · [research backlog](idea_backlog.md)

**Status legend:** **DONE** = completed and documented in repo; **BUILT/UNVERIFIED** = implemented but effect on play not demonstrated; **IN PROGRESS** = being tested or set up; **PROPOSED** = research idea only; **TBD** = final result/ownership not established. Prior team work must not be represented as a new individual contribution.

> **Provisional thesis:** A standard chess engine is tactically powerful but searches as if the true board and subsequent hidden moves will be visible. We investigate how belief quality, hidden-material exposure, and observation-consistent decision-making affect Fog of War Chess strength under a strict CPU budget. We compare inexpensive targeted corrections against a strong belief-weighted Stockfish baseline and quantify when sophisticated imperfect-information search is worth its computational cost.

## 0. Abstract — write LAST [TBD]

Target ~150–250 words. Include (a) task and challenge; (b) baseline architecture; (c) precise extensions **actually tested**; (d) experimental design, baselines and time controls; (e) strongest quantified result, uncertainty, and at least one informative null result; (f) what the experiments teach about multiagent learning. **Do not insert success claims before data exist.**

Potential non-final opening: “We study decision-making under partial observation in Fog of War Chess. We begin from a belief-state agent that evaluates plausible hidden positions using Stockfish and investigate the mismatch between perfect-information tactical search and observation-constrained future actions. Our experiments examine [features actually completed], holding [compute/time controls] fixed. We find [measured outcomes].”

## 1. Introduction and research questions [DRAFT]

**1.1 Setting.** In FoW chess the players see their own pieces and squares reachable by them rather than the complete board, making the full state and opponents’ future observations uncertain. Winning depends on tactical play, inference, and survival against unseen threats. Explain rules departures from orthodox chess (especially capturable king) and why ordinary Stockfish cannot solve the full problem.

**1.2 Project goal.** Build a robust bot for MIT 6.7980’s two-core, 4 GiB competition runtime and learn which forms of information-aware reasoning produce real gains.

**1.3 Research questions (choose 2–3 for the final paper):**

- **RQ1:** When does belief-weighted perfect-information evaluation make mistakes because it assumes future observations reveal hidden states (strategy fusion)?
- **RQ2:** Can explicit hidden-material-risk prediction prevent delayed tactical losses without making the policy overly passive?
- **RQ3:** How do belief support, posterior weighting, and state-selection policies affect actual decision quality?
- **RQ4 (optional):** Under equal CPU budgets, when is a small imperfect-information subgame preferable to spending the same computation on deeper Stockfish search?

**1.4 Contributions (fill ONLY after implementation):** (i) reproducible analysis of failure modes; (ii) controlled implementations and ablations of [specific algorithms]; (iii) tournament and held-out replay results; (iv) theoretical explanation connecting information sets, counterfactual regrets, and strategy fusion. Mark unfinished items as planned, not contributed.

## 2. Game setting and formalization [DRAFT]

- **2.1 Game mechanics:** the observation string, visibility rule, legal move candidate set, king capture and checks, castling/draw rules, protocol, wall-clock budget and runtime. Reference official starter `starter/README.md` and referee.
- **2.2 Extensive-form / partially observable game:** hidden board state `s_t`, own action `a_t`, observation `o_t`, history `h_t`, information set `I_t`; opposing player receives a *different* observation and has different beliefs.
- **2.3 Belief model:** `b_t(s) = P(s_t=s | h_t)`, updates over legal hidden transitions conditional on visible observations, state support and sampling limits.
- **2.4 Evaluation pitfall:** Stockfish’s perfect-information board score is not the same as FoW’s continuation value. A maximizing player cannot choose a different future action for two states producing the same observation.
- **Optional running example/figure:** two hidden rook placements with the **same** observation to our player but different correct defense; contrast a clairvoyant oracle with an observation-consistent action.

## 3. Related work and design rationale [DRAFT]

- **Obscuro (Zhang & Sandholm, 2026):** KLUSS root selection, information-state search, PCFR+, one-sided growing-tree expansion, Resolve/Maxmargin, leaf evaluation, strategy purification. Distinguish Obscuro’s reported numbers from ours.
- **Subgame solving without common knowledge (Zhang & Sandholm, 2021):** theoretical origin of knowledge-limited resolving.
- **PCFR+, CFR, safe/nested subgame solving, Student of Games:** why strategic consistency, convergence, and computation matter.
- **Information-set MCTS:** strategy-fusion critique and a cheap alternative to large equilibrium search.
- **RBC systems StrangeFish2, Fianchetto, Penumbra:** belief weighting, material hazard, sampling, opponent modeling, and practical heuristics (different sensing rules; not directly transferable).
- **Optional learning:** opponent imitation, value residuals, distillation, PSRO as future or exploratory extensions—not established results.

**Suggested literature table:** method | uncertainty represented? | accounts for opponent’s information? | tactical evaluator | search budget | adaptation in our project.

## 4. Existing team system: architecture and evolution [DONE as historical record; author attribution TBD]

**4.1 Evolution of submitted versions** (historical arena records; different opponents and sample sizes, *not* controlled ablations):

| Version | Main difference | Historical record | Status |
|---|---|---|---|
| v2 (Nov 11) | belief states + depth-2 PCFR+, material/visibility leaves | 210 W / 19 D / 331 L (score 39.2%) | DONE; frozen version |
| v3 (Nov 13) | Stockfish scoring ~64 states, PCFR+ fallback | 32 W / 4 D / 40 L (44.7%) | DONE; frozen version |
| v4 (Nov 14) | weighted beliefs, C++ exact-position-set helper, strong Stockfish path | 158 W / 12 D / 92 L (62.6%), recorded Nov 15 | DONE; frozen version |

**4.2 Current baseline architecture:** observations -> position set (up to ~200,000 states) -> Bayesian-style weights from opponent move quality -> sampled boards -> 2 Stockfish processes/MultiPV -> per-move king survival and conditional mean -> action choice. Discuss search fallback and clock use.

**4.3 Existing experimental branch (`eBotI`):** experimental safe-first rule, exact king risk, hidden-material penalty (`FOW_HANG`), opening book, reserve clock, optional two-ply information-set correction (`FOW_INFOSET=0` by default), other feature toggles. **BUILT/UNVERIFIED** as a combined strength improvement; do not call it an uploaded v5 without confirmation.

**4.4 Prior team engineering:** local tournaments, replay analysis, package scripts, protocol tests, immutable frozen bots; link to repository docs, identify commit authors/ownership before writing personal contribution statements.

## 5. Diagnosis: why do we still lose? [DONE analyses; new independent validation proposed]

- **5.1 King and material failures.** Existing arena replay analyses: unseen king threats; hidden-material losses. In the material-loss study, v4 lost 9.27 pawn-points/game to unseen captures over 150 analyzed games and Greek Gift 7.78 over 179; excessive quiet-move and undefended-piece losses, not uniformly bad captures. These are observational comparisons on different game pools.
- **5.2 Belief quality.** Prior analysis found true state present in ~92% of decisions, but only ~87% at sampled fatal king walks, and some true states receive very low probability. Separate state-support failure, probability failure, value/decision failure.
- **5.3 Prior negative experiments:** wider sampled roots; CVaR/worst-board selection; uniform risk mixing; high king-risk penalty; more engines; blind-board opponent model; large KLUSS/GT-CFR tree. Give exact experiment configuration and uncertainty; do NOT label every short negative trial conclusive.
- **5.4 Interpretation.** The likely bottleneck may be hidden-info *evaluation bias* rather than only sample count or penalty scale. Include examples from actual logged games, with board diagrams and observations once selected.

**Figure candidates:** breakdown of loss causes; material loss by quiet move/capture; posterior support by ply; paired decision under true board versus belief state.

## 6. Our investigated extensions / hypotheses [PROPOSED; turn into subsections only for completed experiments]

### 6.1 Hidden-material-risk correction (C01, C02, C03) [PROPOSED TESTS; C01 functionality already built]

**Question:** Does directly pricing unseen captures for *quiet moves* reduce material losses? Compare current `FOW_HANG` λ sweep with a view-only geometric exposure filter and delayed 2–3-ply hazard evaluation. In the text explain why captures should be treated differently. **Contribution eligibility:** independent controlled implementation/tuning, new tests, analyses and conclusions; prior `hang` code is inherited.

**Planned ablations:** λ = 0/0.25/0.5/1/2; geometric exposure only; combined; 1-ply vs 3-ply hazard. Primary metrics: hidden material lost, game win rate, move quality, passive-play indicators.

### 6.2 Information-consistent continuation (A01, A02) [PROPOSED TESTS; A01 exists in code]

**Question:** Can future-action information-set constraints improve over perfect-information Stockfish evaluations?

Sketch the strategy-fusion gap: `E[max_a Q(s,a)] >= E_o[max_a E(Q(s,a)|o)]`. For each candidate first move, enumerate plausible replies, compute our *next observation*, group states with identical observations, and select one continuation action per observation group. Add observation-correctness tests and possibly selective 3–5-ply extension.

**Planned ablations:** same compute, plain Stockfish vs 2-ply correction vs tactical 3–5-ply correction; states 8/12/24; top actions 3/5/8; cost-benefit of targeting only ambiguous turns. **Contribution eligibility:** validation, correctness fixes, extensions, measured novel tradeoffs; current `infoset.py` belongs to existing work until ownership confirmed.

### 6.3 Better belief and state selection (B01, B02, B05) [PROPOSED]

**Question:** Do better hidden-state distributions or rare-event samples improve move choice? Decompose failures, test opponent-action likelihood/held-out predictive calibration, and compare weighted-root sampling to danger-focused importance sampling with likelihood-ratio correction.

**Planned ablations:** same 64-state/depth budget; uniform vs posterior vs stratified/danger proposal; generic opponent model vs learned proposal; held-out true-state inclusion and final match performance. Verify actual protocol exposes opponent identity before identity-conditional features.

### 6.4 Restricted KLUSS-style tactical subgame (A06) [PROPOSED]

**Question:** Can 3–6 root candidate moves and 8–32 belief states capture the benefit of information-aware game solving while preserving tactical evaluation depth? Construct a small restricted game with consistent information sets; initialize leaves using cached Stockfish. Compare one-sided solver variants, leaf depth, iteration counts, and full tree search under equal compute.

### 6.5 Auxiliary engineering/heuristics (F01, F02, F03, F05, F08) [PLANNED / SOME ALREADY BUILT]

Book, reserve clock, adaptive root count, special FoW endgame logic, and *final* integration. Since some toggles are already present in `eBotI`, treat their controlled validation as new, not their original invention. Do not present a bundle of simultaneous changes as a one-factor causal result.

**Writing decision:** Only keep ~2–4 central methods in the main report, chosen after results. Put remaining variants and unsuccessful trials in an ablation summary/appendix, instead of making a list of 46 disconnected algorithms.

## 7. Experimental methodology [PARTIALLY SET UP / TO VERIFY]

**7.1 Baselines:** frozen `obscuro_v4` (B0), eBotI v4-parity configuration validated against B0 (B1), experimental eBotI default (B2), final selected candidate (B3). Do not assume B1 is perfectly identical without direct tests.

**7.2 Infrastructure:** locked Python dependencies and Stockfish builds; record CPU quota, binaries, git commit, flags, random seeds; separate builds for frozen bots. Existing Codex run reported 227 tests initially, 235 in a subsequent infrastructure run, and 180+2 local smoke games; the infrastructure branch and remote persistence remained under validation as of this outline. **Do not treat a transient Codex task as a merged, deployed CI workflow.**

**7.3 Experimental protocol:** short diagnostic tests, small screening tournaments, then precommitted confirmatory 180+2 matches; alternate colors and listing orders; compare against v4 plus diverse opponent styles; avoid oversubscribing two cores; preserve replay and trace logs; record invalid/failed games separately.

**7.4 Metrics:** score=(wins + draws/2)/games; score-rate uncertainty at game/paired-game level; clock and runtime; crashes; hidden-material losses; king deaths; belief support/probability calibration; info-set continuation error. Do not infer strength from 2-game smoke tests or exploit per-ply pseudo-replication.

**7.5 Threats to validity:** small samples, opponent changes, nonidentical time controls, CPU mismatch, shared code in nominally frozen bots, opening correlations, cherry-picking variants, replay-distribution shift, and overfitting to one strong opponent.

## 8. Results — TABLE AND FIGURES TO FILL [TBD]

**8.1 End-to-end progression**: historical v2/v3/v4 scores clearly separated from controlled head-to-head experiments.

**8.2 Single-factor ablation table:**

| Experiment ID | Candidate vs control | Games / time | Score ± interval | Hidden-material effect | Runtime | Decision |
|---|---|---|---|---|---|---|
| C01 | hang λ vs λ=0, other flags fixed | [ ] | [ ] | [ ] | [ ] | [ ] |
| A01 | info-set correction vs off | [ ] | [ ] | [ ] | [ ] | [ ] |
| B05 | hazard-directed sampler vs standard | [ ] | [ ] | [ ] | [ ] | [ ] |
| A06 | restricted subgame vs compute-matched baseline | [ ] | [ ] | [ ] | [ ] | [ ] |
| F08 | final integration vs best single feature | [ ] | [ ] | [ ] | [ ] | [ ] |

**8.3 Failure-case analysis:** annotate 2–3 concrete games where an algorithm helped, hurt, or failed, with actual observations and posterior alternatives. Avoid hypothetical examples masquerading as empirical matches.

**8.4 Negative findings:** prior and new unsuccessful approaches, exact configurations and plausible explanation; disentangle a theoretical limitation from bad implementation/hardware.

**8.5 Final candidate / arena:** only insert if version uploaded; include submission version, date, tested code SHA, packaging build, arena record and limits of comparison. Do not claim arena upload otherwise.

## 9. Discussion: links to multiagent learning [DRAFT]

- Information sets and strategy fusion as a consequence of hidden actions/observations.
- Bayesian opponent models vs adversarial game-theoretic reasoning; Bayesian misspecification risk.
- CFR/PCFR+ vs exploitation of fixed bot styles; tradeoff between safety and strength.
- Computational allocation as a multiagent planning constraint; when search depth trades off with belief breadth and accurate leaf values.
- Why negative results are informative: equilibrium search can be weaker when tactically inaccurate; pessimism about nature can be different from responding optimally to an opponent.

## 10. Limitations, ethics/reproducibility, and final conclusion [TBD]

- Restricted compute; sampled states miss rare truths; opponent policies may change; training/replay data may not match competition distribution.
- Code/data licensing, no secrets, respect competition arena limits. Clearly disclose AI assistance per syllabus.
- Final conclusion should explain *what was learned*, with quantified evidence and no unvalidated performance promises.

## 11. Individual contribution and AI-use statement [REQUIRED TRACKER; finalize with teammates]

**Not a claim of finished contributions.** Use the evidence ledger below to convert planned work into factual statements. We should be precise about which pre-existing code was extended, which tests/analysis were performed by whom, and what automated tools produced.

**Existing team's completed work (attribute after confirming owners):** original bots and submission infrastructure; belief-state representation; Stockfish integration; C++ position set; prior experimental variants and replay analysis; official submissions. Git history and teammates' input are the ownership evidence, not the fact that we reviewed these files.

**Your plausible independently owned work (only if performed):** (1) controlled hidden-material-risk ablation and diagnostic tooling; (2) information-set continuation correctness and improved solver; (3) importance sampling / belief calibration experiments; (4) tournament infrastructure reproducibility and statistical analysis; (5) theoretical literature interpretation and report sections; (6) integration with thorough ablations.

**Per-experiment evidence ledger:**

| ID | Specific task | Status | Who designed it? | Who wrote/tested code? | Branch/PR/commit | Test/metric artifact | Report paragraphs/figures |
|---|---|---|---|---|---|---|---|
| INFRA | Reproducible build, CI, tournament reports | IN PROGRESS in Codex, not yet verified merged | [ ] | [ ] | [ ] | [ ] | §7 |
| C01 | Controlled hidden-material-risk ablations | PROPOSED | [ ] | [ ] | [ ] | [ ] | §6.1/§8 |
| A01 | Validate/extend pre-existing info-set correction | PROPOSED | [ ] | [ ] | [ ] | [ ] | §6.2/§8 |
| B05 | Danger-aware state sampling | PROPOSED | [ ] | [ ] | [ ] | [ ] | §6.3/§8 |
| A06 | Restricted game-theoretic microsearch | PROPOSED | [ ] | [ ] | [ ] | [ ] | §6.4/§8 |
| F08 | Final integration and confirmation | PROPOSED | [ ] | [ ] | [ ] | [ ] | §8/§10 |

**AI disclosure, template (edit with actual use):** “We used ChatGPT for literature discussion, algorithm brainstorming, research planning, and report organization, and Codex for [actual coding/testing tasks]. All experiments, correctness claims, conclusions, and author contributions were reviewed and verified by the team. The authors take responsibility for the reported methods and results.” Do not claim review/verification that has not happened. The syllabus requires transparency about tools and stages of AI use.

## 12. Figures/tables and evidence checklist [PLANNED]

1. Rule/observation diagram showing two hidden states consistent with one view.
2. Architecture diagram of the v4 baseline and information-aware extensions.
3. Historical v2–v4 progress table (not a causal ablation).
4. King deaths and unseen material losses by move class, with sample sizes.
5. Belief support, posterior calibration, and selected-root hazard recall.
6. Information-set continuation example where perfect-information search fuses strategies.
7. Controlled ablation table with uncertainty intervals and runtime.
8. Cost–strength frontier (engine depth vs #boards vs informed search time).
9. Final performance by opponent class and White/Black.
10. Table of tested negative results including reason for rejection.

**Evidence checklist for each empirical figure:** source replay path/hash, bot commit and flags, data preprocessing script, number of games, opponent distribution, error bars, and one-line interpretation.

## 13. Work queue and update log [LIVE]

**As of 2026-11-22:**
- **DONE:** v2/v3/v4 historical snapshots; weighted-belief and C++/Stockfish baseline; multiple existing eBotI prototypes; extensive opponent replay diagnostics; prior negative experiments (some too small for strong claims).
- **DONE in a reported Codex execution, not yet independently re-run here:** Stockfish binaries/helpers built; initial 227 pytest passing; later infrastructure run reported 235 tests and 180+2 smoke checks.
- **IN PROGRESS / BLOCKED:** cloud infrastructure branch being tested; GitHub write credentials remain linked to `Shad0wSeven` with read-only permissions, not `smhgeo422`, and remote persistence not yet established.
- **PROPOSED:** experiment registry; C01 material hazard, A01 info-set validation, B01 belief diagnostic, A06 restricted subgame, B05 importance sampling, plus wider backlog.
- **NOT DONE:** controlled research ablations or new competitive result attributable to this new research phase; new official arena submission; final individual contribution statement.

**Update convention:** after each experiment, append date, author, experiment ID, hypothesis, code SHA, configuration, result, uncertainties, what it changed in our understanding, and next decision. Promote a planned contribution to DONE only when its code and evidence are available.

**Stage 4 update (2026-11-22):** The restricted replay/referee screens are archived from `effafc6`. Useful report evidence includes the P3/P4 information counterexamples, P6 restricted security, P7's adverse residual result, and P9's zero hidden-world one-turn coverage. P1 lacked positive threat labels. P8 is exploratory and the playing-strength results section remains open. See [findings](STAGE4_FINDINGS.md) and the [run index](runs/stage4-screen-20261122.json).

**Stage 5 update (2026-11-22):** The P3 and P8 v2 ablations are archived. P3 covered more omitted threats with no observed change in root choice. P8 reliability shrinkage gave no ordinary holdout gain at a matched quota. There is no supported variant for confirmatory playing-strength trials. See [Stage 5 findings](STAGE5_FINDINGS.md).

**Stage 6 update (2026-11-22):** The confirmation audit found zero qualifying candidates. Full-clock research comparisons and an integrated research bot are absent from the evidence. Use the [confirmation decision](STAGE6_FINDINGS.md) when describing the final results and their limits.

**Stage 7 update (2026-11-22):** The [report evidence package](report_package/README.md) contains the verified run ledger, all nine conclusions, and reproducible figure data. Use the [closure sheet](report_package/CLOSURE.md) for final scope and the [contribution record](contributions.md) for AI disclosure and teammate attribution.

## References / source links (starter list)

- Official FoW rules and submission instructions: https://www.mit.edu/~6.7980/fow/?tab=rules and https://www.mit.edu/~6.7980/fow/?tab=submit
- Obscuro (2026): https://arxiv.org/abs/2506.01242
- Subgame solving without common knowledge (2021): https://arxiv.org/abs/2106.06068
- PCFR+/Predictive Blackwell: https://arxiv.org/abs/2007.14358
- Information Set MCTS: https://eprints.whiterose.ac.uk/id/eprint/75048/1/CowlingPowleyWhitehouse2012.pdf
- Student of Games: https://pmc.ncbi.nlm.nih.gov/articles/PMC10651118/
- Fianchetto thesis: https://taufeeque9.github.io/assets/pdf/bachelors_thesis.pdf
- Team existing approaches: https://github.com/ernjg/fog-of-war-chess-bots/blob/main/APPROACHES.md
- Version history: https://github.com/ernjg/fog-of-war-chess-bots/blob/main/docs/versions.md
- Material-loss study: https://github.com/ernjg/fog-of-war-chess-bots/blob/main/docs/research/material-leaks.md

**Course context:** MIT 6.7980 Fall 2026 syllabus (local source) states projects are 50% of the grade, assesses depth/quality/understanding and clarity, and requires full disclosure of generative-AI tools and phases of use. Consult the latest Canvas project announcement for any requirements not specified in the syllabus.