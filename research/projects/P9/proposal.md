## P9. Information-state endgame conversion and king pursuit

**Independent question.** In small-piece endgames, can we exploit special properties of Fog of War visibility and capture objectives to use *provable or exhaustive information-state policies*, instead of relying on perfect-information chess's mating heuristics?

**Mathematical object.** A restricted endgame belief-state reachability game: classify actions and observation branches that force king capture under the FoW referee rules versus actions that allow indefinite escape. Depending on which endgame and knowledge assumptions are satisfied, use backward reachability/dynamic programming on small states and certified invariants. Never generalize a restricted guarantee to arbitrary midgames.

**Algorithmic variants.** (v0) Reproduce tiny-rule legality and observation tests using the existing referee; (v1) implement state-space searches for limited king+queen versus king and compare to baseline tactic; (v2) prove/validate small tablebase cases and identify situations where king+rook versus king cannot force conversion; (v3) extend to safe king pursuit under uncertainty when pieces remain, only if correctness permits. Opening repertoire and packaging do not belong to this mathematical contribution.

**Existing work / novelty.** Gehnen & Stannat (FUN 2026) already prove important K+Q, K+R and K+2R distinctions. Reimplementing their theorem is **not** a novel discovery. A credible contribution would be a *sound, efficient endgame policy under our bot's actual observation protocol* and quantified practical impact, clearly attributing the published theory. [L14]

**Experiments.** Enumerate restricted positions and observation-equivalence classes; verify each recommended action against all feasible hidden states. Measure guaranteed-conversion rate when guarantees apply, worst-case number of plies, false guarantees, CPU/memory and score on held-out endgame setups. For whole games, measure endgame frequency and conversion quality after correct material reduction; don't infer broad Elo from an artificially enlarged endgame test set.

**Falsification.** Any wrong 'forced win' certificate is a critical failure. If accessible endgame states are too rare or full-state restrictions too stringent, this can be a rigorous small negative/limited contribution rather than a top-level winning feature.

**Original IDs:** F05, F06. **Cost:** medium-to-large. **First gate:** exact toy/endgame certification with full observation-consistency.

## Exact target and strategy-certification requirements

Fog of War Chess is not orthodox chess with limited input pixels. In the local 'starter/referee.py', 'FowBoard', 'fow_moves', 'observation', and 'outcome' define attempted moves, visibility and king-capture termination. A strategy that exploits textbook checkmate geometry may fail when the defending king is hidden.

The 2026 paper by Gehnen & Stannat, [Endgames in Fog of War Chess](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2026.21), establishes that king+queen can guarantee victory versus lone king, king+rook cannot guarantee victory versus lone king, and king+two rooks restores a guarantee under the paper's rules. These are **the authors' theorems**, not project contributions. The paper's exact move/visibility and starting-position assumptions must be compared against the local referee before transferring a guarantee. Any policy certificate is *restricted to the certified endgame state space*.

Let H be a finite set of belief-support histories/observation-equivalent positions and actions be own legal FoW attempts. Define W_0 as sets where the opponent's king has already been captured. Build W_{k+1} as W_k plus every information state I such that there exists one own action a satisfying, for **every** feasible hidden state s in I and **every** adversarial opponent reply path allowed by the restricted rules, the resulting next information state lies in W_k. This description is a schematic alternating fixpoint; actual game transitions/visibility and any allowable opponent capture/escape may require another alternating layer for the opponent's information. The key requirement is *one action per indistinguishable state* and an existential-own/universal-opponent certificate. It is a reachability game, not a Stockfish centipawn scoring function.

**v0 rule equivalence audit:** implement tiny legal endgames under local referee, enumerate reachable observation states, compare movement, king-capture, clocks, draw rules, repetition and castling assumptions with the cited theorem. If rules differ, only claim a theorem for our reduced game after independently proving it.
**v1 exact restricted K+Q versus K conversion:** enumerate a tractable subset of complete positions and belief sets and run backward reachability with witnesses for forcing a capture. First produce a machine-checkable certificate *on a tiny board or bounded horizon*, then expand to true 8×8 starting configurations only if state-space growth permits.
**v2 K+R impossibility and 2R contrast:** construct counterexamples/adversarial escape schedules on identified restricted sets; distinguish demonstration of a particular failing strategy from a proof that no winning strategy exists. Use paper as theoretical reference, not an excuse to label arbitrary samples certified.
**v3 practical endgame takeover:** when actual observed material and support satisfy a certified domain, use the verified reachability policy; otherwise revert to baseline. Explore safe king pursuit and anti-stall only after proof scope is clearly delineated.

~~~text
winning = set(terminal_king_captured_infosets)
repeat:
  added = empty
  for own_information_state I:
    for legal attempted action a available at I:
      post = all_possible_hidden_successor_observations(I,a,
              including_worst_case_opponent_responses)
      if post is nonempty and subset(post,winning):
        added.add(I, witness_action=a)
        break
  winning |= added
until winning stops growing
return certificates, witness policy, adversarial counterexamples
~~~

**Complexity warning.** Even if 8×8 with K+Q v K has O(64³) *fully observed placements*, belief states are subsets of placements and can number up to 2^(O(64³)), with history constraints. Complete belief-space enumeration is not a realistic daily run. Restrict to carefully proven invariant classes, bounded horizon, or small-board analogues before any claim of completeness. State-space size, memory, number of distinct observation-equivalence classes and proof/counterexample provenance are core outcomes.

**Code:** 'starter/referee.py' is canonical; 'bots/eBotI/eBotI/rules.py', 'belief.py' and 'position_set.py' supply live information state; 'stockfish_search.py' special-case path is feature gated; 'tests/test_protocol.py', 'tests/test_repetition.py' and new endgame toy tests. 'F05' previous existing endgame ideas are proposals, not a certified solver.

**Tests.** (1) hidden king on one of two squares requiring inconsistent naive rook actions: no false certificate; (2) all successor boards obey FoW visibility; (3) zero winning chances under a K+R adversarial counterstrategy in the restricted formulation; (4) K+Q forcing policy witnessed and verified exhaustively for a chosen tractable state class; (5) draw by 50-move/repetition prevents an otherwise endless 'eventual' win; (6) en passant/castling ineligible endgame edge cases; (7) policy never chooses a move that loses our king in any supported state when an alternative guarantee exists.

**Outcome hierarchy.** Primary = soundness (zero false winning certificates on fully enumerated test domain), coverage (fraction of eligible endgame information sets proven winning), worst-case capture plies, runtime and memory. Secondary = conversion success in held-out endgame setups, then natural whole-game incidence and paired clock-matched win score. Artificially selected favorable endgames cannot establish broad bot Elo. Stop if model checking exceeds feasible memory or if referee rules invalidate theorem assumptions; report theorem scope and negative examples accurately.
