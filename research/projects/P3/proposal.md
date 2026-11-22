## P3. Observation-consistent contingent tactical planning

**Independent question.** Does perfect-information evaluation cause optimistic strategy fusion, and can a shallow *contingent policy* remedy that bias without surrendering deep Stockfish tactical accuracy?

**Mathematical object.** A future policy maps a *future information set* (observation history), not a hidden true board, to a legal action: pi(o_{t+1}) in A(o_{t+1}). For root move a, optimize E_{s,r,o}[U(s,a,r,pi(o))] under the observation-consistency constraint, rather than E_s[max_{a'} U(s,a,r,a')] where different hidden states improperly select different replies. The discrepancy can be estimated on matched tactical cases.

**Algorithmic variants.** (v0) Unit test the existing 'FOW_INFOSET' implementation, especially legality and grouping by exactly the view that will be observed; (v1) two-ply observation-grouped tactical correction with calibrated fallback; (v2) targeted 3–5-ply extensions and repeated observation grouping; (v3) cache subtrees across turns only when observation-history and rights/repetition invariants match. Search remains among a restricted number of moves, states, and opponent replies.

**Existing work / novelty.** The repository already has a two-ply grouping correction; it must be validated and extended, not reintroduced as a new algorithm. Obscuro and ISMCTS already address imperfect-information search in general. The research contribution would be **a budget-matched correction preserving our specific strong deep-evaluator baseline**, not a novel invention of infosets. [L1,L2,L3,L4]

**Experiments.** Construct toy worlds where two true states look identical but favor incompatible continuations; verify the proposed policy chooses one observation-consistent response. Reproduce baseline action rankings on saved observations with and without the correction. Measure strategy-fusion gap, decision reversals, subsequent 2–5-ply material/king losses, number of engine calls, p95 per-move CPU. Compare fixed-depth search and the existing two-ply mode at matched CPU. Only then run paired matches.

**Falsification.** If correction costs more Stockfish depth than the avoided false optimism is worth, or policy grouping is incorrect, abandon that variant. A decrease in offline tactical regret without a matching robust game benefit must be reported as such.

**Original IDs:** A01, A02, A07. **Cost:** medium-to-large. **First gate:** exact toy counterexample plus reliable no-leakage implementation.

## Deep derivation, implementation contract, and decisive controls

The original 'bots/eBotI/eBotI/infoset.py' already implements a small two-ply observation grouping correction controlled by 'FOW_INFOSET' (default off). It takes up to five root actions, twelve heaviest belief states and three likely opponent replies with depth-six leaf evaluations, using up to 50% of the move budget. Stage 0 cannot claim to invent that mechanism; it must **audit it and develop a logically stronger, budget-controlled correction**. In 'APPROACHES.md' previous large GT-CFR degraded playing strength, plausibly because tactical leaf evaluation became weaker.

Formalize two values for action a. Given hidden state s, opponent reply r~pi_opp(r|s,a), next own observation o=O_our(T(T(s,a),r)), and eventual value U:
  Q_cont(a) = max_{mu: observations→legal_attempts} Σ_s b(s) Σ_r pi_opp(r|s,a) U(s,a,r,mu(o)).
  Q_clair(a) = Σ_s b(s) Σ_r pi_opp(r|s,a) max_u U(s,a,r,u).
For a shared feasible action set Q_cont ≤ Q_clair. The gap is the **unrealizable advantage** from planning different future actions in hidden states that remain observationally indistinguishable. For approximate leaf utilities this is a diagnostic, not proof that a particular move is winning.

A future action must respect Fog of War referee semantics (possible attempt legality and special castling) rather than requiring orthodox legality on all hidden boards. Two trajectories with same 64-square view but distinct public/action histories may carry different information and may need different keys. Test whether the current grouping by observation alone is a sufficient statistic in the proposed horizon.

~~~text
for root_action a in shortlisted_actions:
  buckets = map observation_history_key → weighted continuation states
  for sampled hidden state s with belief mass b_s:
    s1 = local_fow_referee_transition(s,a)
    if terminal(s1): record terminal utility; continue
    for opponent_reply r with probability pi(r|s1):
      s2 = local_fow_referee_transition(s1,r)
      if terminal(s2): record terminal utility; continue
      buckets[next_actual_observation_key(s2)].append((s2,b_s*pi))
  for bucket:
    select ONE next own action maximizing total weighted utility in bucket
  estimate Q_cont[a] as weighted aggregate of bucket values and terminals
choose root a maximizing Q_cont[a], with safe fallback on budget expiry
~~~

**Versions.** v0 correctness proof obligations and toy aliasing fixture. v1 repair/validate existing two-ply algorithm, legal action mapping and observation grouping, with exact same Stockfish budget. v2 selective depth-three/five search on king-hunt, loose pieces and forcing tactical motifs, with observation grouping at every own information set. v3 persistent policy/search reuse keyed by full legal history state, only after no-stale-cache tests. These are successive improvements of **one** algorithmic contribution.

**Grounded code targets:** 'infoset.py' 'refine'; 'stockfish_search.py' 'stockfish_search' and 'gather'; 'engine.py' leaf scoring; 'rules.py' and 'starter/referee.py' legality; 'tests/test_stockfish_search.py'; 'tests/test_obscuro_bot.py'. Do not edit 'obscuro_v4'. P6 owns strategic minimax/regret-solvers; P3 is an expected-value contingent planner.

**Complexity.** With K sampled boards, M root actions, R opponent replies, L continuation actions and C_SF leaf cost, naive depth two costs O(KMRLC_SF), then multiplies branching with each extra ply. Evaluate only top-M moves, use an explicit finite leaf cache with correct en-passant/castling/repetition keys, and cap CPU. A decision-time increase can erase all value by shallower Stockfish depth; test depth-only control at identical allocated seconds.

**Mandatory tests.** (a) Two hidden states identical observation and opposite best next moves: original clairvoyant max overvalues root, contingent planner cannot take both. (b) States have distinct future observations: two actions are permitted. (c) Opponent can capture king immediately; (d) special FoW castling and illegal-attempt semantics; (e) one sampled board with duplicate weight; (f) observed future board key differs only in historical publicly known rights; (g) opponent replies ignored by top-R include strategically fatal action; (h) timeout returns baseline choice without protocol failure.

**Primary offline outcome:** paired difference in action-regret against a high-budget **observation-consistent** policy oracle on fixed tactical fixtures, plus the estimated strategy-fusion gap and subsequent true 2–5-ply losses as retrospective diagnostics. A clairvoyant oracle is a theoretical upper bound, not the control. Hold out games and motifs. For tournament screens compare baseline, current INFOSET v0, fixed-budget corrected v1, equal-cost Stockfish deeper search, more roots without grouping, and selective-depth variants. Paired seeds/colors and game-level CIs; never infer effectiveness from 20 games.

**Stop rule:** no action reversals in measured ambiguous tactical cases, or extra search cost reduces depth enough to lose at equal CPU, or observation grouping unsound. An offline action-regret gain without actual game strength gains must be described as a partial result only.
