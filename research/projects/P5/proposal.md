## P5. Calibrated catastrophic risk and hidden-material preservation

**Independent question.** Does the scoring rule systematically misprice immediate king loss and future hidden-material catastrophe, so that better *utility calibration* wins more games even with the same posterior and search?

**Mathematical object.** Calibrate P(KingCaptured | b,a), P(UnseenMaterialLost_{1:3} | b,a), and P(eventual win | h,a) separately. A playing utility could use E[terminal game reward | h,a] with calibrated imminent failure probabilities, instead of mixing a raw king-risk probability and tanh-scaled centipawn values with an arbitrary scalar. We must avoid treating any one heuristic coefficient as the actual probability of loss.

**Algorithmic variants.** (v0) Reproduce existing 'FOW_HANG', 'FOW_SAFE_FIRST', 'FOW_FOG_TAX', exact risk and risk-lambda experiments under clean controls; (v1) predict quiet-move undefended material loss separately from favorable fog captures; (v2) two- or three-ply exposure/capture-propensity model; (v3) calibrated win-probability conversion for king threats, including losing-material-but-live-king cases; (v4) conditional anti-hunt/king-hunt policies driven by confirmed risk estimates. A trained immediate hazard predictor belongs here, rather than inventing another contribution called 'ML hazard'.

**Existing work / novelty.** The internal 'material-leaks.md' describes a 9.27 vs 7.78 pawn-points/game loss gap and says the excess is concentrated in quiet exposed or standing undefended pieces. Several defensive heuristics already exist, including failed global risk multipliers. Our contribution requires **new calibrated, selective hazards and causal ablations**, not another constant penalty. Proper probability validation and the correct terminal game objective matter. [L7,L13,L14]

**Experiments.** Build an offline hazard-label dataset from refereed replays: observations at decision time are features, later full-board outcomes are labels only. Split by game/opponent; report reliability curves/Brier score, discrimination and error by material class, quiet/capture split, and game phase. Construct situations where a fog capture has positive expected recapture trade, so an indiscriminate 'avoid fog' rule should fail. In controlled games record hidden-material losses, king captures, active-play reduction, W/D/L, and interaction with safe-first. For every claimed change, show what portion of measured improvement is driven by fewer true catastrophic decisions rather than mere passivity.

**Falsification.** If offline calibration improves but game score falls or clock cost dominates, report a calibration improvement without claiming strength. Prior penalties may already saturate the useful effect.

**Original IDs:** C01–C08, E01. **Cost:** medium. **First gate:** calibrated hidden-material-risk model on held-out games, stratified by move type.

## Causal diagnostic and probability-calibrated utility

Historical 'docs/research/material-leaks.md' compares 150 v4 and 179 Greek Gift replays: 9.27 vs 7.78 pawn-points lost per game to unseen captures, with much of the excess arising when *quiet moves* leave valuable pieces exposed. It also notes fog captures can be materially profitable. These are **observational comparisons against different bots and opponent distributions**, not a controlled estimate that a new hazard penalty saves 1.49 points/game. The team already implemented 'FOW_HANG', 'FOW_SAFE_FIRST', 'FOW_FOG_TAX', exact king-risk scans and variations of king-risk weights. A new contribution must change *model or decision semantics* and be evaluated against each existing variant.

The baseline value in 'stockfish_search.py' takes the shape value = -risk + (1-risk)·mean, where risk reflects near-term king loss and mean a nonlinear Stockfish centipawn transform. Those two quantities are not automatically on the same payoff scale. A fatal event has terminal value -1 in an illustrative [-1,1] utility scale, whereas a rook disadvantage on a perfectly seen board can be survivable under fog. Multiplying risk by an arbitrary lambda does not resolve the mismatch.

**Formal risk decomposition.** For action a at history h, estimate p_K(a)=P(king lost immediately | h,a), p_M(a)=P(unseen valuable material loss within next k plies | h,a, survives), and E[V_game | h,a, no catastrophe]. A calibrated estimate of eventual game utility is
  U_hat(h,a) = p_K(a)*(-1) + (1-p_K(a))*E[V_game | h,a, king survives],
where the continuation model itself handles material-risk events and avoids counting p_M twice. If instead a material hazard penalty λ_M E[loss] is applied, it is an empirical utility approximation and **not** a probability. P5 develops a selective, calibrated event forecast that can be attached to either utility formulation, while P7 owns the remaining long-horizon continuation value.

**v1 targeted hidden-material hazard.** For each quiet candidate move, compute probability and pawn-equivalent loss due to unseen attackers *against moved piece and own standing valuable pieces*, using belief states. Subtract the expected net exposure only after modeling recapture opportunity. Do not automatically tax tactical captures that predictably gain material. Calibrate the event propensity with held-out replays; a geometric threat from fog is not equivalent to an actual capture.
**v2 multi-ply capture propensity.** Estimate conditional p_M for 2–3-ply windows using opponent-reply proposals frozen from P2 baseline. Track a dangerous attack that is not acted on separately from a realized loss; correlation is causal-consequence dependent.
**v3 calibrated terminal utility.** Fit a low-parameter mapping from material/phase/king threat/uncertainty to eventual game win probability, with game-grouped train/holdout; test instead of raw tanh(cp/600) and constant king multiplier. If new utility is learned long-horizon, explicitly separate it from P7 by keeping the P5 mapping restricted to immediate terminal loss.
**v4 anti-hunt/hunt state machine.** Only if data show distinct offensive vs defensive situations, introduce conditional threatened-king escape and tactical pursuit as versions of calibrated risk. Pure tactical policy hand-tuning is not independent evidence.

~~~text
for candidate move a:
  king_loss_prob = belief_weighted_immediate_terminal_check(a)
  material_event = estimate_hidden_loss_quiet_moves_only(a)
  if a is capture:
    do not apply generic visibility-based penalty
  expected_continuation = calibrated_or_baseline_nonterminal_value(a)
  score[a] = -king_loss_prob + (1-king_loss_prob)*expected_continuation
             - optional_utility_scaled_extra_hidden_material_loss(a)
select action; report each component separately
~~~

**Double-counting test:** engine expected continuation may already incorporate material losses on sampled boards; if the new risk term duplicates these, compare its incremental predictive value on **residual** lost events after controlling for engine score. No outcome labels may be used at play time. A model trained on full board in replay must use only view/belief-derived features when deployed.

**Grounding:** 'stockfish_search.py' (HANG_LAMBDA, SAFE_FIRST, FOG_TAX, RISK_LAMBDA, 'king_capturable_after', 'free_to_unseen', 'weigh'); 'hazard.py'; 'tools/arena/material' (unseen_losses.py, calib.py, rule.py); 'tools/arena/hazard.py'; 'APPROACHES.md'; 'tests/test_stockfish_search.py'.

**Evaluation labels.** For a decision at ply t, evaluate prospective action on the *actual board* retrospectively to label king/capture exposure, but do not mistake this counterfactual for an outcome under the opponent's observed behavior. Predictive labels from played actions are on-policy, so alternative unplayed actions require the referee simulator and an explicitly specified opponent policy. Produce separate results for moved-in quiet, left-standing, and captures; classify defended/undefended and recapture profit. Use held-out games, opponent/phase stratification and Brier/reliability for event probabilities.

**Controls:** B1 (v4-equivalent), B2 eBotI default, FOW_HANG=0/1, SAFE_FIRST on/off, a global risk multiplier previously negative, our v1 selective model, geometry-only view penalty, event-only vs calibrated utility. At identical CPU, record hidden material lost per full game, king-capture reasons, tactical captures foregone, number of zero-risk options, win/draw/loss and clock forfeits.

**Falsification:** no calibration gain; lower hidden losses but disproportionate decline in attack/win rate; the new penalty duplicates Stockfish continuation; or improvement disappears under a clean clock-matched ablation. Mark any apparent 'points saved' from observational replay as descriptive, not causal.
