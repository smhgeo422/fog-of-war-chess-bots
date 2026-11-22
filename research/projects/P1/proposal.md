## P1. History-consistent belief reconstruction and posterior calibration

**Independent question.** Is the dominant error that the true state is absent from, underweighted in, or poorly represented by the bot's belief set, even when its decision rule is unchanged?

**Mathematical object.** A posterior over hidden legal histories or boards, b_t(s)=P(s_t=s | own observation/action history). Formally, after an observed opponent transition o, b_{t+1}(s') is proportional to the observation likelihood times the sum over prior states and plausible opponent actions that legally transition to s'. State support and probability weight are distinct; a calibrated hazard marginal need not imply calibrated full-board probabilities. Proposed weighted sampling q(s) may deliberately overrepresent threatening states, but action expectations must use importance weights b(s)/q(s), with reported effective sample size.

**Substantial algorithmic variants.** (v0) Reconstruct the current team's weighted beliefs on held-out game histories, quantify actual state inclusion and posterior rank; (v1) capped, history-consistent stratified particles, with move-sequence legality and evidence-preserving rejuvenation; (v2) threat-stratified proposals corrected for sampling probability; (v3) learn compact piece-location proposal distributions that still pass legality/history filters; (v4) robust posterior-temperature ensemble only if a concrete calibration deficiency remains. Do not independently sample squares and pretend the resulting board is legal.

**Existing work / novelty.** The team already has position enumeration and a Stockfish-based likelihood; general particle filtering is not novel. Our possible contribution would be a *tested, history-consistent, decision-relevant proposal/repair mechanism* that is measurably better at detecting threats while keeping inference overhead fixed. [L4,L5,L6,L7,L13]

**Experiments.** Hold out full referee-truth replays by game and opponent; replay only legal bot observations to construct b. Measure full-state inclusion, weighted rank, ESS, enemy-square Brier/log score where a proper probability is available, hidden-attack recall in sampled roots, errors by phase and position cap, and per-turn wall/CPU. Test against exact small-support enumerations. At fixed Stockfish evaluation count, compare altered posterior versus baseline without changing the action selection function. Use next-turn unseen-material and game score as downstream checks, not as substitutes for posterior metrics.

**Falsification / failure.** If truth is usually retained and properly weighted yet losing actions persist, or if importance weights have unusably low ESS, posterior repair is not an empirically useful primary lever. Illegal states or full-board leak invalidate the method.

**Original IDs:** B01, B04, B05, B06, B07, E04. **Cost:** medium-to-large. **First gate:** an error-decomposition table, not a 20-game headline.

## Deep derivation, implementation contract, and decisive controls

Define the player's information history H_t as the sequence of own views, our actions, public clock/context, and observable consequences. Let S_t be a complete legal referee state, including pieces, side to move, castling, en-passant, and repetition-related information. Existing position keys must be audited before declaring any two states equivalent.

The Bayesian filtering target is b_t(s)=P(S_t=s|H_t). After an opponent transition, the update for a possible successor s' is proportional to 1[O_our(s')=o_new] times the sum over predecessor state s and an opponent action a with T(s,a)=s' of b_previous(s) times pi_opp(a|s,opponent-information). The exact opponent information is inaccessible; for this project **freeze the existing policy model**. An approximate belief must not silently be called exact simply because every state in the current container matches the latest view.

Separate four failure events: (F1) truth not in capped support; (F2) truth in support but weight is wrong; (F3) truth/risk correctly weighted but sampled roots miss a rare important event; (F4) truth-risk captured but action evaluation still bad. P1 is about F1–F3. This decomposition prevents claiming a posterior fix solved evaluator error.

**Version 1 algorithm: explicit mixture sampling on the existing legal support.** Let p_i≥0 sum to 1 be normalized weights over a set of K_old states. Define a threat-score d_i from king/material attack geometry; form r_i ∝ positive bounded priority(d_i); and proposal q_i=(1-alpha)p_i+alpha r_i with alpha strictly below 1. Draw k indices from q. For any event f, estimate E_p[f] by sum_j [p_index/q_index · f(state_index)] / sum_j [p_index/q_index]. This self-normalized importance estimate is not exactly unbiased, but is consistent when proposal support covers p. Record proposal and weight before aggregation; never set q_i=0 for a state with p_i>0. Weight degeneracy can make the variance worse; report ESS=(Σw)^2/Σw².

**Version 2: cap repair.** Create cap-aware weighted reservoir or history-consistent rejuvenation. History validity means **there exists a legal predecessor action sequence compatible with every prior observation**, not merely a final board that matches today's visible squares. If computing such a history becomes intractable, v2 is an honest feasibility finding. Do not repair by placing missing pieces arbitrarily into fog and calling the position reachable.

~~~text
proposal(states,weights,k,alpha):
  p = normalize(nonnegative(weights))
  threat = score_hidden_attacks_without_truth(states)
  r = normalize(epsilon + bounded_priority(threat))
  q = (1-alpha)*p + alpha*r
  I = seeded_categorical_sample(q,k)
  w = [p[i]/q[i] for i in I]
  return states[I], w, effective_size(w)
~~~

**Concrete repository integration.** Audit 'bots/eBotI/eBotI/position_set.py' (PositionSet.observe, _fetch, repair and effective_size), 'belief.py' (Belief.observe, _cut, replenish and fit_to_view), 'stockfish_search.py' (64-root draw and full-set king risk), 'bots/eBotI/positions.cpp', and 'tools/arena/truth_in_set.py' / 'tools/arena/belief_calibration.py'. New feature must be reversible and distinguish **full support** metrics from sampled-root metrics. Do not change the frozen baseline.

**Complexity.** For M existing candidate support states, computing priorities and mixture costs O(M·g) where g is per-state threat evaluation; subsequent categorical sampling O(M+k) with alias sampling or O(k log M) using a prefix tree, and memory O(M+k). Full history-reconstruction complexity may grow exponentially in the number of unseen transitions; report acceptance rate and CPU cap.

**Toy tests.** (1) Two hidden worlds with unequal priors and opposite hidden king attacks; confirm estimated probability against exact enumeration. (2) One rare dangerous state with b=0.001; verify no zero-proposal and compare error/variance over many fixed seeds. (3) History that fits current view but violates a previous view must be rejected. (4) Castling/en-passant, repeated positions, opposite colors, capped state set, helper fallback, invalid weight values and empty survivors. (5) The public game observation must be the only online source; full referee truth is withheld until offline labels are computed.

**Preregistered outcomes.** Primary: per-game-averaged held-out Brier score for the probability that an *unseen piece attacks our king or selected high-value piece after a prospective action*, computed at the information available before the action. Secondary: support inclusion, actual-state rank, root threat recall at fixed root count, p95 CPU, ESS, and game score. Split whole games and opponent families, cluster uncertainty by game. Compare alpha=0, alpha>0 tuned on development only, more uniform samples, and baseline p-weighted sampling at equal number of Stockfish calls and clock settings. If P1 improves root recall but worsens proper probability calibration, do not call it a successful posterior-calibration method.

**Scientific stop/advance rule.** v1 passes only with valid sampling math, no information leakage, and out-of-sample gain on preselected probability metric at tolerable CPU. A failure caused by truth absent from support motivates v2; a failure caused by evaluation despite correct risk does not justify further posterior tuning. Preserve original-vs-new source attribution.
