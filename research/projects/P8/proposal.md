## P8. Rational metareasoning under a hard chess clock

**Independent question.** Given a fixed information-state evaluation algorithm, can the bot learn *when another Stockfish call or information-aware search is worth its time*? This is a different objective: allocate computation, rather than change the posterior or evaluation function.

**Mathematical object.** At a decision, estimate value-of-computation VOC(c) = E[max_a estimated U_after computation c] - max_a estimated U_now - lambda·time(c) - opportunity cost of future moves. Computations include one more root sample, deeper engine evaluation, more tactical replies, or more CFR iterations. A stopping policy should approximate positive marginal improvement under a fixed clock. Estimate VOC without looking at withheld true-board state during play.

**Algorithmic variants.** (v0) Reproduce constant 64-root depth/clock controls and prior breadth-vs-depth loss; (v1) instrument value stability and near-tie action margins over incremental Stockfish calls; (v2) choose roots versus depth based on ESS, king danger and action disagreement; (v3) move-specific, game-phase-dependent clock allocation with reserve against flagging; (v4) amortize search across turns only with correct cache state, if doing so measurably reduces work.

**Existing work / novelty.** The team already has a reserve clock and tested crude uncertainty/time heuristics; generic rational metareasoning is a long-established area. Our empirical contribution would be a *trained or calibrated marginal-computation allocation rule* that lowers decision regret or increases strength **at exactly the same total compute and time-forfeit risk**. [L10,L12]

**Experiments.** Replay budget curves on held-out observations: decision ranking and marginal value as a function of extra computations. Include a matched-total-CPU and matched-clock comparison; use p95 wall time, per-move timeouts, total Stockfish nodes, action-choice stability and score. Randomly assign fixed-budget controls to avoid confounding hard positions with increased compute. Always include a rule that stops before the referee limit.

**Falsification.** If apparent gains come from giving a variant more compute or selectively omitting flag losses, they don't count. Predictors should show incremental benefit over a simple reserve rule, not only over an intentionally weak clock.

**Original IDs:** A05, F02, F03, F04, E06. **Cost:** medium. **First gate:** action-stability/VOC curves and equal-budget improvement.

## Meta-level optimization rather than another search method

The baseline 'bots/eBotI/eBotI/stockfish_search.py' has explicit MAX_ROOTS≈64, scan states≈256, maximum depth≈12 and per-slice limits. 'bots/eBotI/eBotI/search.py' has a reserve-clock rule. The team tried broader 384-root search and uncertainty/time tweaks with poor or inconclusive results; this suggests that a new budget rule must optimize *decision quality per cost* rather than rely on 'more thinking on scary positions'.

At time t, the bot has a posterior over action utilities U(a) estimated from finite sampled roots/Stockfish calls. A computation c—one additional state evaluation, deeper search at promising action, an extra tactical reply, or one solver pass—changes the posterior over U. Ideal metalevel value of computation is
  VOC(c | D_t) = E_{y~P(y|D_t,c)}[max_a m_a(D_t,y)] - max_a m_a(D_t) - λ·cost(c), where m_a(D)=E[U(a)|D].
The expectation is over possible results of the computation itself, *not* the hidden referee truth. λ reflects lost future clock opportunity. This is distinct from P4's **value of game observations**. P4 changes what the player will see on the board; P8 decides which computations to execute before choosing the current move.

**v0 instrumentation:** replay a held-out fixed decision dataset, incrementally grow baseline Stockfish calls one slice at a time; log each intermediate candidate ranking, action margin, approximate uncertainty, time and eventual high-budget reference action. This establishes actual marginal returns as a function of budget and whether early stopping is justified. Need one action stability trace per root and seed.
**v1 probabilistic stopping:** derive a conservative upper bound on expected improvement in choosing another action (e.g., posterior probability top-2 action ranking reverses times estimated utility gap). If below cost threshold/clock safety, stop and play current best; otherwise choose which computation targets maximum predicted VOC.
**v2 adaptive roots vs depth:** compare marginal benefit of another posterior particle versus one more Stockfish depth iteration on current top actions. Use ESS, hidden king exposure, action-value disagreement and phase *only as features of the VOC predictor*, not as arbitrary extra computation triggers.
**v3 game-level clock allocator:** account for remaining moves, increment and reserve in an approximate stochastic scheduling problem. Any per-move extra time must be compensated elsewhere; no total-cost advantage may come from using double the CPU.
**v4 optional carryover cache:** with exact FEN/repetition/observation-history keys, reuse expensive evaluations across consecutive turns; report cache hit rate and corruption tests. This is P8 only when the research question is marginal value of computation, not a claim that caching itself is new.

~~~text
while remaining_think_budget > safety_margin:
    actions = current_value_estimates()
    for possible computation c:
        expected_decision_gain[c] = estimate_value_of_computation(c,history)
        net[c] = expected_decision_gain[c] - clock_shadow_price*predicted_cost[c]
    c_star = argmax(net)
    if net[c_star] <= 0: break
    execute c_star with hard deadline
return best_available_action_with_protocol_buffer()
~~~

**Grounded code:** 'stockfish_search.py' root sampling/scan/engine slices, 'search.py' move_budget, 'engine.py' stockfish pool and deadlines, 'tools/experiment.py' CPU/time manifest, 'tests/test_engine.py' and 'tests/test_stockfish_search.py'. Use own clock and not hidden referee state for online decisions. Important: runner's 350-minute CI job timeout is *not* the per-move chess time budget.

**Complexity and self-referential cost.** If there are C candidate computations and F features, model scoring O(CF) per decision step; if predicting VOC itself takes as long as the next Stockfish call, the controller fails. Maintain an overhead cap (<5% of initial research budget as a provisional engineering test), and compare actual spent seconds including the controller.

**Experimental design.** Primary = held-out reduction in decision regret versus a high-budget reference at fixed *total CPU time over a game* and *same base/increment*, with game-clustered uncertainty. A high-budget reference's action is imperfect, so also report fixed-move eventual material/king outcomes and actual game score. Controls: default reserve clock, constant roots, fixed depth, uniform more-time policy, ESS-only heuristic, margin-only heuristic and randomized computation allocation, all equalized for CPU and clock forfeits. Track p50/p95/p99 decision latency, total engine nodes, late-game reserve, timeouts/forfeits, action stability, and overrun by phase.

**Sanity counterexample:** in one position the top move is already decisively better and extra compute has zero action value; in another two moves are nearly tied and a targeted calculation can flip the choice. A good controller should spend **less** on the former, not blindly more whenever entropy is high.

**Falsification.** No prediction of marginal decision benefit on held-out positions, matched CPU gain disappears, model overhead/clock losses outweigh changes, or apparent gain stems from a different opening/policy. Keep fixed player policy to preserve independence from P3/P5/P7.
