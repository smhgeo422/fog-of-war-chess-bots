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

## Formal causal motivation and a non-redundant algorithm

A legitimate FoW move can change both player observations even if its direct Stockfish score is unchanged. P3 corrects which future actions are **possible given observations**; P4 studies whether **choosing a root move in order to alter those observations** yields game utility. Its scientific object is an intervention on information-flow, not simply another deeper tactical evaluator.

For a fixed root action a and a reference continuation decision u, define expected value of our next observation
  VOI_self(a) = Σ_o Pr(o|h,a) max_u E[U(s,a,u)|h,a,o] - max_u E[U(s,a,u)|h,a].
This is nonnegative under ideal value estimates when the feasible decision set and action-conditioned transition are held fixed; **comparing VOI_self(a) across different root moves does not automatically establish overall action improvement**, because the moves also have different direct payoffs. Separate informational and material effects with a decomposition and matched-action control. When the opponent sees a changed set of squares, define expected opponent-value shift
  Denial(a) = E_{o_opp}[V_opp(best response after seeing o_opp)] - V_opp(with reference observation),
but the opponent may be helped by *our* revelation; a lower opponent continuation value is only useful if material/tactical values are otherwise held comparable.

Two actions with the same number of newly visible squares can have very different VOI: if one reveals the occupancy of the only fork-defense square and the other reveals unimportant empty squares, entropy reduction and square-count are poor objectives. Conversely a reveal that never changes our optimal continuation must have VOI≈0 even if it reduces posterior entropy. This is the key distinction from a generic visibility bonus.

**v1: decision-focused information score.** For each candidate root move a: sample states with the unchanged P1 baseline; simulate legal next actions/replies; partition hypothetical next states by **real observations**; approximate the best conditional continuation with a cheap legal-action evaluator, and subtract a counterfactual with no new observation. Apply an incremental bounded information bonus beta·VOI only where its marginal utility has not already been counted by P3. Initially evaluate an offline *same immediate tactical value* action comparison to isolate information. The P4-playing feature must be allowed with P3 disabled to prove independence.
**v2: opponent-revelation suppression.** Explicitly compute which own piece squares become visible to the opponent under each hypothesized transition. Score their actual feasible subsequent replies under the P2 **frozen** opponent baseline, not a hypothetical all-knowing or blind opponent. Penalize only revelation that predictably improves their action, not all visibility.
**v3: strategic information manipulation.** Investigate deliberate hiding/bluffing under a safety constraint for king-capture risk. Require opposing response likelihood to shift in the predicted direction on held-out observations.

~~~text
for candidate own move a:
  direct = cached_perfect_information_move_value(a)
  observations = grouped_simulated_future_views(a)
  informed = sum_o P(o|a) * max_u E[continuation_utility|o,a,u]
  uninformed = max_u sum_o P(o|a)*E[continuation_utility|o,a,u]
  voi = informed - uninformed
  revealed_to_opponent = legal_opponent_observations_after(a)
  denial = predicted_incremental_opp_decision_change(revealed_to_opponent)
  score[a] = direct + beta * bounded_unpriced(voi) - gamma*denial
~~~

**Important double counting:** If the baseline already uses an observation-consistent P3 continuation, its Q value *already includes* the information benefit. In that case P4 must be tested against a baseline without that lookahead or used as a cheaper **approximation** of an expensive information-value term, not a second additive bonus to the same quantity. The term 'bounded_unpriced' explicitly requires an empirical overlap test, not an unexplained correction.

**Controls and negative examples.** (1) reveal many irrelevant squares with no action changes: predicted VOI zero; (2) reveal one consequential enemy move: VOI positive; (3) enemy reveal that leads to an attack, net negative; (4) bluff that induces no opponent belief response, therefore zero strategic advantage. Compare entropy gain, visible-square count, raw Stockfish score, P3-only, P4-only, and P3+P4 interaction with independent model selection.

**Code:** 'starter/referee.py' observation() and rules; 'bots/eBotI/eBotI/infoset.py' grouping can supply **read-only diagnostic** continuations; 'stockfish_search.py' candidate scoring; 'opponent.py' for opponent-response likelihood (frozen). New feature may share observation generation but not import P3's own optimization as the primary algorithm.

**Resource/correctness:** For K states, M own moves, R replies, and L continuation evaluations, worst-case O(KMRL C_leaf); cache observation groups. The opponent visibility for a state is not identical to the player's visibility. Use only hypothetical states sampled from the actual belief in live evaluation, while true board can label outcomes retrospectively.

**Primary scientific outcome:** held-out predicted vs actual *action-sensitive* value of information, quantified by frequency of changed future best move and its measured continuation value (not number of revealed squares), stratified by tactical context. Secondary: opponent response-likelihood change, CPU, full-game win rate. Stop if the bonus merely tracks material evaluation or the P3 contingent value, if latency is untenable, or if intervention never changes action on held-out positions.
