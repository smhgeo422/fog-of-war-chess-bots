## P2. Opponent policy identification and online style adaptation

**Independent question.** Does modeling the *opponent's policy* from allowed histories yield better likelihoods and better best responses than a single fixed one-ply Stockfish proposal?

**Mathematical object.** P_theta(a_t | I_t^{opp}, z_t) where I_t^{opp} is what the opponent could have observed and z_t is a latent style mixture inferred *online* from legal observed actions. A probability floor prevents posterior collapse. The opponent's hidden observation is itself uncertain to us; infer over plausible opponent information, not a literal board with all our unseen pieces removed. Critically, prediction of opponent moves is the objective even with our posterior and our action planner held fixed.

**Algorithmic variants.** (v0) Replicate fixed Stockfish-1-ply plus uniform mixture and the already-rejected blind-board model as controls; (v1) fit/shrink lightweight style experts for capture preference, checking, development, tactical greed and king pressure; (v2) update mixture weights by likelihood on actual observed move consequences; (v3) infer small opponent-view particles where permitted and feasible; (v4) opponent-specific versus identity-agnostic evaluation, depending on whether identity is available under the actual bot protocol.

**Existing work / novelty.** Prior 'APPROACHES.md' measured a crude blind-board proposal as substantially worse than the full-board policy. Simply calling that proposal 'opponent-aware' would repeat a failed experiment. Our independent mechanism is a *history-conditioned predictive model*, validated by proper scoring rules before game play. [L1,L6,L7,L13]

**Experiments.** Split opponents and games temporally. Record observed legal actions, candidate action sets and observation likelihood without giving the model information unavailable at decision time. Compare held-out negative log likelihood, top-k recall, calibration, Bayesian regret against a fixed model, and downstream likelihood assigned to actual transition histories. Then vary only opponent likelihood inside the full bot; compare same CPU/clock games versus B1/B2 and across unseen opponent styles. Include a 'uniform floor' and no-identity ablation.

**Falsification.** If predictive gains disappear on held-out opponents, or slight opponent exploitation leads to serious worst-case regressions, do not claim general improvement. A behavior model can be good for likelihood without being a superior playing strategy.

**Original IDs:** B02, B03, B08, E05. **Cost:** medium-to-large. **First gate:** out-of-sample predictive advantage over the existing one-ply model.

## Deep derivation, implementation contract, and decisive controls

The existing 'bots/eBotI/eBotI/opponent.py' estimates candidate opponent move probabilities using a one-ply Stockfish value and a uniform floor (policy share 0.8, temperature 0.06, policy-time budget 0.5s in the inspected source). These values flow into 'position_set.py' / 'belief.py'. An internal study rejected a naive blind-board model, on 4,783 replayed opponent moves, so simply hiding unseen friendly pieces in Stockfish is not a new approach.

**Distinct estimand.** P2 fits pi_theta(a|I_opponent,z), where I_opponent is that player's own hidden-information history and z is a latent behavioral type (aggressive captures, conservative, attacking king, development, engine-like). We do *not* observe I_opponent exactly. We approximate a distribution over possible opponent information histories conditional on **our** information, then marginalize; if not computationally justified, fit the lower-dimensional public-history style model first. A model may use true opponent action as an **offline supervised label** when reading referee replays but must never access that invisible move during live play unless the bot protocol reveals it.

Start with pi(a|s,h) = epsilon/|A(s)| + (1-epsilon){lambda·pi_SF(a|s) + (1-lambda) Σ_j rho_j,t·pi_j(a|features(s,h))}. The uniform epsilon floor guards against posterior collapse; require sum_{a∈A(s)}pi(a)=1. For a hidden transition producing observable event e, update style weights using likelihood of the *entire event equivalence class*,
  L_j(e|h) = Σ_{s,a: O_our(T(s,a))=e} b(s)·pi_j(a|s,h).
Then rho_j,t+1 ∝ rho_j,t L_j(e|h), with shrinkage to the original global prior. Do not condition on hidden actions that were only recovered retrospectively.

~~~text
after_observed_opponent_event(event):
  for j in styles:
    log_L[j] = logsumexp over compatible (state,opponent_action)
                    [log belief_weight + log style_policy_j]
  log_rho = log_rho + log_L
  rho = shrink(normalize_log_weights(log_rho), global_prior)
for policy_query(hypothetical_board):
  scored = combine(engine_policy, style_experts, rho, uniform_floor)
  assert normalized_including_OTHER_action
  return scored
~~~

**Version path.** v1 logistic/softmax style experts trained on permissioned public histories with game-split validation; keep frozen Stockfish baseline. v2 online mixture with event-level Bayesian updating and opponent-unknown fallback. v3 infer opponent-view particles by **forward-consistent** observation simulation, never by an arbitrary 'blind board'. v4 opponent-shift detection and cautious reset. Any identity-conditioned feature needs proof the actual bot protocol exposes identity. If not, use only history-inferred latent styles.

**Code audit.** Touch 'bots/eBotI/eBotI/opponent.py' (OpponentPolicy.__call__, move_odds and OTHER mass), 'position_set.py' (_after_opponent), 'belief.py' (_after_opponent), 'tools/arena/opp_model_calib.py', 'tests/test_opponent.py', and referee observation logic. Baseline P1 posterior stays fixed for independent policy-likelihood tests.

**Costs.** For A possible moves, F features and J style experts, linear scoring is O(A F J) per hypothesized state, plus ordinary engine evaluation. View particles multiply cost by their number R; impose a strict deadline. Cache style-independent action features and release fallback probabilities on failure.

**Toy/negative tests.** (1) Two hidden opponent moves induce the same visible result: updating style only on event should not distinguish them. (2) One style makes an invisible move very likely; ensure high full-action NLL offline does not trick us into claiming the move was observed online. (3) All legal FoW attempts receive nonzero mass, including castling and king-capture opportunities. (4) Unknown opponent type must shrink toward baseline rather than overfit first two moves. (5) Predictive results must be invariant to random order of held-out games at fixed model. (6) Reproduce baseline POLICY_SHARE and temperature behavior before interpreting gains.

**Preregistration.** Primary = held-out negative log likelihood of actual opponent action, with secondary log likelihood of *observed transition equivalence class*, using game/opponent-blocked validation. Compare fixed Stockfish+uniform, truly uniform, naive blind-board (historical negative control), static style mixture, online mixture, and optional identity-conditioned model. Aggregate NLL at game level and bootstrap opponent/game clusters. Explicitly distinguish good move prediction from good FoW play: even a strong predictive model might overfit exploitable opponents and reduce robust game score. Only a predictive passing result justifies replacing opponent likelihood in the playing bot and then running fixed-clock tournaments.

**Falsification.** No held-out reduction in action/event NLL after opponent-grouped splits; extra compute exceeding policy timeout; online use of unobservable labels; or deterioration on previously unseen opponent styles. These failures are scientific results, not reasons to inflate model capacity without evidence.
