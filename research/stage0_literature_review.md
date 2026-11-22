# Stage 0 — Annotated literature, prior-team evidence, and novelty audit

**Prepared 2026-11-22.** Scope: check central primary sources and team files to justify the **nine** fixed hypotheses P1–P9. The research directions are not claimed to be novel inventions merely because they have new code names. This is an annotated technical synthesis, not a claim that every theoretical proof from every reference was formally reconstructed.

## 1. What the team implementation actually does

Source-tree review on planning branch 'research/nine-independent-directions':

| Actual file/function | What it currently implements | Consequence for research |
|---|---|---|
| 'bots/eBotI/eBotI/position_set.py' PositionSet.observe/_after_opponent/_fetch/repair | Compiled helper backed weighted support of consistent boards; 200,000 cap, Python fallback and top-up mechanisms | P1 must discriminate full-support loss from errors introduced by sampling |
| 'bots/eBotI/eBotI/belief.py' Belief.observe/_cut/replenish | Python belief fallback capped at smaller number with history and view-based repair | Final-view consistency alone need not imply correct full-history posterior; test reachable histories |
| 'bots/eBotI/eBotI/opponent.py' OpponentPolicy | One-ply engine likelihood, softmax-temperature and uniform floor (0.8/0.2 split by default) | P2's new hypothesis is history-adaptive likelihood, not simply installing an opponent model |
| 'bots/eBotI/eBotI/stockfish_search.py' gather/weigh/stockfish_search | Deep multi-board move evaluation and exact/sampled king risk, plus existing FOW_HANG, SAFE_FIRST, FOG_TAX, RISK_LAMBDA, roots/depth controls | P5 requires new calibrated event model; P8 needs equal-budget metareasoning |
| 'bots/eBotI/eBotI/infoset.py' refine | Two-ply observation-conditioned continuation search, disabled by default; up to 5 moves, 12 states, 3 replies, depth 6 | P3 starts with rigorous audit and extension; cannot claim to invent 2-ply grouping |
| 'bots/eBotI/eBotI/gametree.py' GameTree and 'tree_search.py' TreeSearch | Growing-tree regret/search logic, root and carryover machinery | P6 is a bounded cost-controlled new experiment, not first GT-CFR coding |
| 'bots/eBotI/eBotI/search.py' move_budget | Existing reserve-clock policy | P8 must beat reserve clock at equal total computation |
| 'starter/referee.py' FowBoard, fow_moves, observation, outcome | Canonical local rules, full referee truth and replay | Every project needs a no-oracle live feature path and precise legal/observation tests |
| 'tools/experiment.py', 'experiment_report.py', 'archive_research_run.py' | Reproducible match execution, metrics and integrity archives | Stage 1 must extend project ID handling, then preserve evidence |
| 'APPROACHES.md' and 'docs/research/material-leaks.md' | Internal prior tests and descriptive material-loss analysis | Any new causal claim must address historical negative findings and CPU confounds |

A central distinction: existing code *enabled*, existing code *tested*, and existing code *causally improved score* are three different statements. The repo contains significant experimental code that may have been checked in but not validated under clean comparable matches. The current planning branch does not change that evidence status.

### Existing internal evidence and its interpretation

- Previous Obscuro-like large GT-CFR attempts with deep search sacrificed Stockfish depth; short matches against v4 were poor. This is evidence for trying **small deep-leaf** rather than full tree search; it is not a no-go theorem for CFR or evidence that a new small solver will work.
- Previous 384-root settings often underperformed the 64-root deep engine. The explanation 'posterior bias dominates sample variance' is plausible but **not experimentally isolated**. P1 tests threat representation and P8 tests allocation separately.
- CVaR over boards, uniform risk-weight mixing, a global king-risk multiplier, a crude blind-board opponent predictor, and a variety of existing safe-first/hazard variants have been tested with limited or negative outcomes. P2 and P5 must provide mechanisms different from these rather than sweep the same parameter again.
- The team's 'material-leaks.md' found 9.27 pawn-equivalents/game of unseen captures in 150 v4 sample games versus 7.78 over 179 Greek Gift games. The 1.49 difference was concentrated in quiet moved/standing undefended material; fog captures also often led to positive exchanges. Opponent mix and selection differ. This motivates a selective hazard model but does not identify the causal effect of using it.
- 'APPROACHES.md' explicitly notes some past tournaments oversubscribed CPUs because workers survived canceled jobs; a clean single-worker control is mandatory before treating older short-match win rates as reliable.

## 2. Primary literature, claims and adaptation gaps

### R1 — Zhang and Sandholm (2026), Obscuro

**Source:** [ICLR 2026 conference paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9705eec26e511d7844a591ce10c33a3f-Abstract-Conference.html); [full paper](https://proceedings.iclr.cc/paper_files/paper/2026/file/9705eec26e511d7844a591ce10c33a3f-Paper-Conference.pdf).  
**Read/verified:** publication and paper introduction; KLUSS explanation (§3), equilibrium computation and one-sided tree growth. The paper introduces knowledge-limited *unfrozen* subgame solving, a game-tree search with predictive CFR+, single-sided expansion, and strategy purification; its authors report strong FoW performance. The paper explicitly notes KLSS and KLUSS are not always game-theoretically sound in general because cut-off portions of the game may be strategically relevant. Predictive CFR+ has theoretical support for *average strategies*, while Obscuro elects to use a last-iterate strategy for practical reasons.  
**Gap for us:** the team's deep belief-weighted Stockfish approach differs materially in what it pays for: expensive tactical leaf evaluations versus wide strategic search. P3 and P6 therefore must be budget-matched and not promise to reproduce Obscuro's performance or theory. P4's information incentives are known in general; its proposed novelty is affordability and incremental value on this baseline.

### R2 — Zhang and Sandholm (2021), knowledge-limited subgame solving

**Source:** [NeurIPS 2021 paper](https://proceedings.neurips.cc/paper/2021/hash/c96c08f8bb7960e11a1239352a479053-Abstract.html).  
**Verified claim:** common-knowledge closure may be intractably large; lower-order knowledge-limited subgames can be constructed without it, but unrestricted replacement of the blueprint can increase exploitability. Paper develops conditions under which safety can be preserved.  
**Gap:** P6 cannot call a local result 'safe' without blueprint/counterfactual constraints or a verified restricted-game guarantee. P3 needs only realizable future actions, not a claim to solve an equilibrium.

### R3 — Brown and Sandholm (2017), safe and nested subgame solving

**Source:** [NeurIPS 2017 paper](https://papers.nips.cc/paper_files/paper/2017/hash/7fe1f8abaad094e0b5cb1b01d712f708-Abstract.html).  
**Verified claim:** optimal subgame strategy can depend on unreached parts of the whole game, so local solves are not independent without the appropriate blueprint/alternate values.  
**Gap:** P6's v1 tests a restricted game only; v2 requires a correctly implemented blueprint to discuss robust integration. Do not claim global exploitability bounds from toy-game convergence.

### R4 — Cowling, Powley and Whitehouse (2012), information-set MCTS

**Source:** [preprint](https://eprints.whiterose.ac.uk/id/eprint/75048/1/CowlingPowleyWhitehouse2012.pdf).  
**Core mechanism:** information-set tree search addresses pathologies of naïve determinization, particularly allowing a planner to select impossible state-conditioned actions.  
**Gap:** P3's core question is not whether strategy fusion exists abstractly; it is whether a *bounded correction using deep tactical leaves* increases our bot's decision quality. Compare with a clairvoyant planning relaxation and with actual observation-consistent policy.

### R5 — Silver and Veness (2010), Monte-Carlo planning in large POMDPs

**Source:** [NeurIPS 2010](https://proceedings.neurips.cc/paper/2010/hash/edfbe1afcf9246bb0d40eb4d8027d90f-Abstract.html).  
**Core contribution:** planning using sampled particles in belief space rather than full state enumeration.  
**Gap:** that framework is single-agent partially observable control; Fog of War has an adversarial opponent whose beliefs and strategic incentives differ from environment stochasticity. P1/P3 can adapt particle and observation-action ideas but not silently transplant POMDP guarantees.

### R6 — Solinas, Rebstock, Sturtevant and Buro (2023), history filtering

**Source:** [NeurIPS 2023 proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/87ee1bbac4635e7c948f3eea83c1f262-Abstract-Conference.html).  
**Verified claim:** efficiently producing histories compatible with imperfect-information subgame constraints is generally difficult; paper analyzes tractability and supplies an MCMC method for a card game.  
**Gap:** P1's proposed state 'rejuvenation' is research-scale unless it can prove compatibility with our own view history and can control acceptance cost. No claim of general polynomial-time repair.

### R7 — RBC StrangeFish2 / Fianchetto precedent

**Sources:** [Gardner et al., Reconnaissance Blind Chess competition](https://proceedings.mlr.press/v220/gardner23a/gardner23a.pdf); [StrangeFish2 code](https://github.com/ginoperrotta/reconchess-strangefish2); [Fianchetto thesis](https://taufeeque9.github.io/assets/pdf/bachelors_thesis.pdf).  
**Supported observation:** RBC bots emphasize posterior maintenance, prioritized samples, opponent modeling, and heuristic safety. StrangeFish2's reported 2022 improvements included prioritization and board-value heuristics.  
**Critical caveat:** RBC has a separate sensing move and different move rules. No experimental result there automatically transfers to FoW. P1/P2/P5 need FoW-specific evidence.

### R8 — Farina, Kroer and Sandholm (2021), predictive Blackwell approachability

**Source:** [AAAI 2021](https://mlanthology.org/aaai/2021/farina2021aaai-faster/).  
**Supported mechanism:** predictive regret matching (PCFR+) improves solver convergence in benchmark extensive-form games; its convergence is an average-strategy property.  
**Gap:** P6 must verify its own regret updates, reach weights and exploitability before chess experiments. The benchmark literature does not guarantee that a tiny solved subgame has better game outcomes than a deeper heuristic evaluator.

### R9 — Schmid et al. (2023), Student of Games

**Source:** [Science Advances / PubMed](https://pubmed.ncbi.nlm.nih.gov/37967182/), DOI 10.1126/sciadv.adg3256.  
**Verified claim:** guided game-tree search can be combined with trained value/policy models and game-theoretic reasoning in large perfect/imperfect-information games.  
**Gap:** P7's lightweight residual and P6's bounded solver are scaled-down experiments, not reimplementations of the full distributed learning system. Keep the compute assumptions explicit.

### R10 — Brown et al. (2020), ReBeL

**Source:** [NeurIPS 2020](https://papers.nips.cc/paper/2020/hash/c61f571dbd2fb949d3fe5ae1608dd48b-Abstract.html).  
**Verified claim:** public-belief representations and search can be combined with learned value/policy functions.  
**Gap:** it is easy to train a model on later true hidden-board features by accident; P7 must use strict observation-time feature cutoffs and entire-game splits.

### R11 — Gneiting and Raftery (2007), proper scoring rules

**Source:** [JASA DOI](https://doi.org/10.1198/016214506000001437).  
**Principle:** a proper scoring rule measures probabilistic calibration/sharpness rather than arbitrary accuracy against a threshold.  
**Gap:** posterior calibration (P1), next-move likelihood (P2), hazard probabilities (P5), and learned outcome probabilities (P7) are **separate targets**. A good score on one is not proof of good game play. Report Brier/log score only for a well-defined event with aligned feature availability.

### R12 — Hay, Russell, Tolpin and Shimony (2012), selection of computations

**Source:** [UAI 2012 / PMLR](https://proceedings.mlr.press/r10/hay12a.html).  
**Verified claim:** metalevel computation selection formalizes expected improvement in action quality; naive rules to allocate more samples to uncertain alternatives can be suboptimal.  
**Gap:** P8 must deduct the computation controller's own CPU cost and compare at matched total clock, not just run more engine iterations on critical moves.

### R13 — Gehnen and Stannat (2026), FoW endgames

**Source:** [FUN 2026 open paper](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2026.21); [full HTML](https://drops.dagstuhl.de/storage/00lipics/lipics-vol366-fun2026/html/LIPIcs.FUN.2026.21/LIPIcs.FUN.2026.21.html), DOI 10.4230/LIPIcs.FUN.2026.21.  
**Verified theorem-level summary:** king+queen vs lone king guarantees victory; king+rook vs lone king does not guarantee victory; adding a second rook restores a guarantee under their assumptions.  
**Gap:** P9 needs exact rule compatibility and constructive algorithm verification. This is a compelling *algorithmic verification and deployment project*, not a claim to rediscover their theorem.

## 3. Nine-project novelty boundaries and independent falsification

| Project | Our independent intervention | Strongest prior-art/teammate caveat | Primary measurement |
|---|---|---|---|
| P1 | History-valid belief sampling/repair and calibrated threat posterior | Existing capped weighted belief and generic particle filters | Held-out hidden-threat Brier, support coverage |
| P2 | Latent-style/history-conditioned opponent likelihood | One-ply model already exists; blind-board previously failed | Held-out move and observable-event NLL |
| P3 | Corrected and budgeted observation-consistent tactical policy | Existing two-ply INFOSET; Obscuro general search | Observation-consistent policy regret, CPU |
| P4 | Decision-sensitive value of future information / denial | Obscuro already reasons about information | Changed continuation decisions and their measured value |
| P5 | Selective calibrated hidden-material/king danger utility | HANG, SAFE_FIRST, FOG_TAX already exist | Held-out risk calibration; clean matched games |
| P6 | Small, strong-leaf local mixed-strategy resolver | Large previous GT-CFR lost; safety nontrivial | Exact toy exploitability + robust full-game tests |
| P7 | Learn legal-history-based long-horizon residual value | ReBeL and SoG establish learning/search paradigm | Holdout residual error and action ranking |
| P8 | Value-of-computation controller at fixed CPU | Existing clock and root/depth heuristics | Decision quality per CPU and time-forfeit rate |
| P9 | Constructive certified restricted FoW endgame policy | FUN 2026 already proves core endgame distinction | Sound certificates, endgame conversion |

## 4. Observed limitations of this review

- Some relevant works were read through their official conference abstracts and prior detailed repository notes; the Obscuro primary PDF and FoW endgame open HTML were inspected directly for substantive details. This is **not** proof verification for all 13 papers, and we must cite authors rather than claim original theorem discoveries.
- No external comparison result (RBC Elo, Obscuro tournament record, Greek Gift arena score) is directly interchangeable with our frozen v4 local match score. Opponents, datasets, rules and hardware differ.
- The prior team repository contains historical claims and results from separate settings. They are background hypotheses until the Stage 2 baseline audit reproduces their interpretations with trustworthy provenance.
- Before any code or dataset use, confirm the course's rules regarding public data, opponent identity, AI authorship, and official arena access; Stage 0 does **not** grant permission to bypass any of them.

**Readiness for Stage 1:** Nine separate hypotheses are intellectually motivated and novelty-confined. Their empirical validity is wholly untested here; the next stage is an engineering infrastructure stage, not additional literature expansion.
