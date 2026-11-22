## P7. Learned continuation-value correction, not another heuristic penalty

**Independent question.** Can supervised learning predict *FoW-specific long-run game utility* missed by perfect-information Stockfish, without access to hidden truth at play time? This targets **value-function approximation**, not posterior reconstruction, opponent behavior or immediate capture risk.

**Mathematical object.** V(h,a) ≈ g(V_Stockfish(b,a), f_theta(phi(h,a))), where the correction uses permitted observation/history features, belief uncertainty summaries and perhaps recent search diagnostics. Train on held-out outcomes or carefully defined multi-ply counterfactual targets, with explicit target selection bias and game-level clustering. Constrain the model to be small and fast enough for CPU inference; retain a zero-correction fallback.

**Algorithmic variants.** (v0) Make a legal feature/target audit and partition data by game/opponent/time; (v1) regularized linear or small tree-based residual predictor for 3–10-ply FoW value changes; (v2) rank candidate moves using learned residual at a fixed engine budget; (v3) distill a strong offline observation-consistent search teacher (P3 is only the teacher, not part of the learned model); (v4) consider brief imitation/self-play fine-tuning **only if labels, resources, and independent validation justify it**. Full tabula-rasa deep RL is a separate high-cost *variant of this learned-policy direction*, not a promised achievable experiment.

**Existing work / novelty.** Student of Games, ReBeL and RBC synoptic planning establish broad value/policy-learning precedents. A novel result here would be a precise, leakage-safe small correction that adds predictive quality beyond Stockfish on **this team's** hidden-information failures and has measured playing value. [L6,L10,L11,L13]

**Experiments.** Use time-/opponent-held-out games and features from the same information available to the bot at each decision; avoid distributing correlated positions across train and test. Compare value MSE/calibration, held-out move ranking on matched counterfactual cases, inference latency, and candidate-vs-baseline game score. Negative controls: random labels, history-shuffled features, Stockfish-only, constant bias, and an immediate-risk-only model. Report performance by game phase and opponents. If training targets are biased by the behavior policy, explain counterfactual limits instead of calling the model causal.

**Falsification.** Offline accuracy that doesn't improve chosen decisions or games is not sufficient. Any use of future hidden state as input or leakage through train/test splits invalidates the result.

**Original IDs:** E02, E03, E07. **Cost:** medium pilot, very large full self-play. **First gate:** leakage-safe data and honest held-out predictive gain.

## Precisely what is learned—and what it is not

The existing bot evaluates hypothetical true boards using Stockfish; its perfect-information continuation assumptions can be systematically wrong because future own moves depend on future *observations* and opposing intentions. P7 hypothesizes that an inexpensive learned **long-horizon residual** can correct the prediction of eventual outcome beyond what is already explained by immediate hidden attacks (P5), calibrated posterior mass (P1), and time allocation (P8).

Let h be the legally observed history, a a contemplated action, V_SF(h,a) an aggregate Stockfish value computed with the frozen reference posterior, and φ(h,a) an online-feasible feature map (phase, own piece placement, sampled hidden piece marginals, search disagreement, recent observed captures, repeated information patterns, and clock status). Define V_hat(h,a)=clip[V_SF(h,a)+f_θ(φ(h,a)),-1,1]. The first trained target should be a **specific predictive quantity**, not vaguely 'how good a move is': for example, discounted 4–10-ply material-and-survival value under a specified fixed continuation policy, or full game result under the logged behavior policy. The latter is **not** the counterfactual value of an unplayed action; behavior-policy selection is a serious confound.

**v0 data audit:** serialize observation-derived feature vectors before any future move is known, freeze opponent/game splits and exact source replays, and calculate retrospective target only after features are saved. Train/test split *entire games*, not individual positions. Build a full-truth leakage sentinel (a forbidden full-board feature should raise in the online extraction path).
**v1 regression residual:** regularized linear ridge or small gradient-boosted tree, with target centered on V_SF and a zero-correction fallback; train on training games, select hyperparameters on development, and freeze for test. Use a small size/speed bound so a full batched evaluation is cheaper than an extra Stockfish search.
**v2 action ranking:** learn differences in outcome between candidate actions from **simulation rollouts under the same declared continuation policy**, not using the chosen-action-only future as a ground-truth label for every alternative. If multiple action estimates are noisy, report standard errors by root history and policy; train to predict decision ranking rather than just unconditional outcome.
**v3 distillation:** let a much slower but observation-consistent P3 planner provide targets on a training-only corpus; a model learns a cheap approximation, with its own evaluation independent of the teacher's training positions. That uses P3 as source of training labels but P7's independent hypothesis is learned *generalization* and inference economy.
**v4 optional learned policy/self-play:** only with explicit learning capacity and independent held-out data; not a commitment to implement deep tabula-rasa RL, and not a novel theorem based on ReBeL or Student of Games.

~~~text
for logged own history h and candidate a:
  base = frozen_stockfish_belief_value(h,a)
  x = extract_online_only_features(h,a)
  target = compute_posthoc_rollout_or_actual_outcome(h,a,label_protocol)
  store(x,base,target,game_id,opponent_id,seed,availability_timestamp)
train residual f_theta on train_games
select theta on development_games only
assert no game/seed/opponent leakage into test_games
for each new decision:
  value[a] = base[a] + bounded(f_theta(x[a]))
~~~

**Major bias controls.** If training on the *observed* game outcome after chosen a, estimates reflect logging policy and opponent pool, not an unbiased estimate of Q(h,a) for unplayed alternatives. If training on simulated alternative rollouts, show which policy generates those returns, how many independent rollouts, and sensitivity to that model. If distilling P3, measure approximation fidelity separately from actual game strength. A false claim of causal improvement is worse than an accurate predictive one.

**Code audit targets:** 'bots/eBotI/eBotI/stockfish_search.py' value aggregation; 'engine.py' fast evaluation; 'belief.py' observation-only features; 'starter/referee.py' replay traces; 'tools/experiment.py' replay manifests; 'docs/research/material-leaks.md' historical diagnostic. The previous 'FOW_HANG' penalty is not a learned residual. All learned parameters must be serialized with seed, split IDs, training code version and feature schema, not just hidden in source.

**Complexity.** Linear predictor O(F) per candidate after baseline features; boosted model O(T·depth) per candidate; with a fixed top-M actions, total overhead O(M F) or O(M T depth). Train offline; memory budget must fit the bot's actual packaging/runtime. Include model load/startup time and fallback when artifact absent.

**Experimental specification.** Primary = per-game-clustered held-out proper prediction error on a fixed rollout/continuation target (MSE for bounded value, log loss/Brier for eventual win probability), plus separately an out-of-sample top-action ranking test on matched **simulated counterfactuals**. Controls: Stockfish-only, constant calibration shift, material/phase-only linear residual, immediate-risk-only P5-like feature, randomly permuted labels, shuffled unseen-history features, distilled model if used. Predeclare train/dev/confirmation groups by game and opponent. Only if offline results pass measure actual selected-action change, CPU cost and paired full matches. A model that improves offline MSE but picks worse game actions is a negative strength result.

**Failure/kill conditions.** Any direct post-action hidden board information in online features, train/test overlap through repeated nearly identical positions, model too slow, non-robust gain on unfamiliar opponents, or unverifiable target provenance. Keep a readable coefficient/feature-importance analysis, especially for any apparent learned 'fog advantage' that may just be leakage.
