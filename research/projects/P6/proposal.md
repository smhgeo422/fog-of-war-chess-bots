## P6. Bounded game-theoretic re-solving and robust mixed strategies

**Independent question.** When the opponent may strategically exploit a predictable policy, can a small imperfect-information *mixed strategy* be more robust than any greedy best-response heuristic? Unlike P2 this optimizes **robustness/exploitability**, not the prediction of a specific opponent's next move; unlike P3 it explicitly solves a local strategic game.

**Mathematical object.** A restricted zero-sum extensive-form game with action-observation infosets, credible prior-reach/opponent-root distributions and continuation values. Regret matching / predictive CFR+ approximates a mixed strategy; compare approximate exploitability, security value and equilibrium gap on small known games. Blueprint preservation and alternate values constrain unsafe local deviations; do not assert a theoretical safety guarantee for an unverified approximation.

**Algorithmic variants.** (v0) Reproduce internal C++/Python GT-CFR failed settings under controlled CPU; isolate impact of shallow leaf evaluations; (v1) solve exact tiny toy imperfect-information games with known solutions; (v2) 3–6 root actions, 8–32 belief states, deep cached Stockfish leaf values and bounded regret iterations; (v3) blueprint-aware Resolve vs Maxmargin ablations and root-prior mixtures; (v4) controlled purification versus mixed play; (v5) opponent population stress tests / PSRO-lite **inside this same strategic robustness contribution**, not an additional idea.

**Existing work / novelty.** The team attempted large GT-CFR and lost small matches, probably because evaluator depth and solver budget traded off badly. Obscuro, knowledge-limited solving, safe re-solving and PCFR+ are published methods. The contribution is an empirical/theoretical case for or against **small, evaluator-preserving game-theoretic corrections** on this course hardware. [L1,L2,L8,L9,L10]

**Experiments.** Check equilibrium/regret convergence on Kuhn-poker-like toy games, a constructed small fog tactical game, and adversarial policy-matching cases. Hold leaf evaluation quality fixed while varying CFR iterations, root count, expansion asymmetry, blueprint, and mixing/purification. Compare average score *and* worst-opponent/population score under matched CPU, with uncertainty estimates and deterministic seeded controls. If solver exploitability improves on toy games but full FoW win rate degrades, explain why.

**Falsification.** Solver with unresolved regret, incorrect counterfactual reach weights, or weaker Stockfish leaf quality is not an interpretable test. If no feasible subgame budget passes all toy checks, stop after a documented negative result; do not pretend this is ready for the final bot.

**Original IDs:** A06, A08, D02–D07. **Cost:** large / exploratory. **First gate:** exact small-game correctness and actual runtime feasibility.

## Detailed game-theoretic target and computational safety

This is explicitly *not* a proposal to port the full Obscuro implementation again. 'APPROACHES.md' documents earlier Python/C++ growing-tree GT-CFR with weak shallow leaves losing short matches to v4, while 'bots/eBotI/eBotI/gametree.py' and 'tree_search.py' already contain extensive regret/tree logic. Our hypothesis is **a tiny robust game with strong cached tactical leaves** might avoid the unfavorable compute tradeoff; this is uncertain.

Model a restricted two-player zero-sum extensive-form game G on a small set of plausible root histories. Players' decisions are grouped by **their own** observation histories and legal FoW actions. Let x_i be player i's behavioral strategy, u_i(x_1,x_2) expected payoff under reach probabilities (including true belief/root priors). A Nash-type robust target is min_{x_opp} u_our(x_our,x_opp), or equivalently minimize exploitability of a candidate strategy in the restricted game. This differs from P2, which predicts one opponent and optimizes against that empirical policy; if empirical best response is excellent against one style but vulnerable to another, P6's security objective can prefer mixing.

For regret matching, per infoset I and action a accumulate counterfactual regret
  R_T(I,a)=Σ_t [v_i(σ_t with action a at I) - v_i(σ_t)].
A regret-matching-plus variant uses nonnegative cumulative regrets with predictive updates as justified by [Farina, Kroer & Sandholm 2021](https://ojs.aaai.org/index.php/AAAI/article/view/16676). The average strategy—not necessarily last iterate—has standard CFR convergence interpretation; if implementing last-iterate purification, test the exact algorithmic conditions before claiming theoretical safety. In an externally truncated subgame, **opponent counterfactual values / blueprint constraints** are needed for robust resolve; a random deep leaf value does not establish safe re-solving [Brown & Sandholm 2017](https://papers.nips.cc/paper_files/paper/2017/hash/7fe1f8abaad094e0b5cb1b01d712f708-Abstract.html).

**v0 solver oracle:** two-player matching pennies, Kuhn-poker-like imperfect-information toy with known equilibrium, a two-board observation-alias game, and full CFR exploitability/duality checks. Measure exploitability of the average policy against an exact restricted best-response oracle, not win rate only.
**v1 deep-leaf bounded local game:** choose ≤6 own root actions, 8–32 plausible true boards, limited opponent information partitions and 2–4-ply response horizon. Evaluate leaf continuations via cached deep Stockfish under unchanged CPU budget, with correct terminal king-loss handling and normalized reach. Compare pure greedy, exact small restricted security solution, and regret solver. The number of infosets, opponent view ambiguity and leaf errors are logged.
**v2 KLUSS/blueprint:** only after v1 works, carry the previous-turn blueprint and alternate values. Compare Resolve versus Maxmargin with valid counterfactual reach root distributions and the paper's prior/uniform root mixture where appropriate. Measure whether strategy is safe against restricted best response, not just policy diversity.
**v3 policy refinement:** bounded predictive CFR+, root prior ablations, action pruning, final-iterate purification when mathematically supported, and a small opponent population cross-play matrix as a *robustness diagnostic*, not a tenth contribution. Full PSRO/self-play is a research-scale variant, not a prerequisite.

~~~text
generate restricted histories and legal-information-set action tables
precompute Stockfish continuation payoffs at equal per-root budget
verify state reach and opponent observation partitions
initialize blueprint/security priors if available
for t=1..iteration_limit:
    traverse game, compute opponent-reach-weighted counterfactual values
    update CFR+ regrets at each infoset
    accumulate strategy average
compute exploitability or restricted best response gap on toy game
select policy only if correctness and deadline budget pass
~~~

**Complexity and feasibility.** Each CFR iteration visits O(E) game edges for a fixed tree; T iterations O(TE), storage O(sum_I |A(I)| + E). Tree generation can scale exponentially in depth, and deep Stockfish leaf evaluation adds L·C_SF. A stated 8–32 roots by 3–6 actions and high leaf depth can still exceed the course two-core clock. Gate by p95 time, total nodes, solver iterations, exploitability convergence, and whether tactical leaf depth is held constant to the baseline.

**Existing modules:** 'gametree.py' GameTree, _counterfactual, iterate, carry_over; 'tree_search.py' TreeSearch, root support and solver parameters; 'regret.py', 'solver.py', 'obscuro_search.py', and 'tests/test_ebotI_gametree.py', 'tests/test_solver.py'. Reuse testable components but treat previous team authorship explicitly.

**Controls:** small game exact minmax/known equilibrium, uniform root policy, same deep evaluator greedy root, earlier C++/Python GT-CFR settings, one-sided vs two-sided expansion, pure vs average strategy, blueprint vs none, same-CPU depth-only Stockfish, worst-opponent security score. Stratify opponents to reveal nontransitivity rather than using a single v4 matchup as proof.

**Kill criterion:** failure to solve toy equilibrium within tolerance, incorrect chance reach weights, no valid counterfactual/blueprint conservation, or a meaningful drop in leaf depth under matched CPU. It is acceptable for P6 to produce a credible negative result explaining the earlier failure. Never claim game-theoretic global safety from a restricted game.
