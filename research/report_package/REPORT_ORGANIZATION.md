# Report organization and contribution map

Use one argument across the manuscript. A Fog of War bot must reason about hidden positions, choose an action that remains sensible after its next observation, and pay for that reasoning under a clock. The team built a strong weighted-Stockfish reference. The later experiments tested specific ways to improve belief, decisions, and search allocation. Several mechanisms worked in restricted settings. The eventual playing-strength claims should follow the evidence ledger and the explicit comparison scope.

| Section | Content and strongest evidence |
| --- | --- |
| Introduction and problem | Fog of War as adversarial partial observability. Define observations, hypothetical states, strategy fusion and the compute budget. State the evidence scope up front. |
| Team system and evolution | Starter protocol, Obscuro-style PCFR+ baseline, Stockfish over beliefs, opponent likelihood and C++ position tracking in frozen v4. Then eBotI's risk, infoset and clock variants, and the Greek Gift investigations. Keep historical arena outcomes separate from local controlled results. |
| Methods | Frozen B0 and default B2, B1 parity failure, matched color/seed blocks, observation-only features, separate retrospective labels, archive and compute controls. |
| What information changes decisions | Use P3 and P4 to explain the difference between revealing squares and revealing which move to play. P6 is a small counterexample showing why a mixed policy can matter. Compare fixture effects with game-derived exposure, action changes and regret. |
| Belief and prediction | Put P1, P2 and P5 side by side. Distinguish support, calibration, and adaptation as different outcomes. Include positive-event counts and the synthetic-versus-local-versus-competitive data boundary. |
| Compute and deployment limits | Use the P8 matched-quota figure, P7's adverse residual errors, and P9's soundness/coverage result. Explain the decision to retain v4 as the reference and leave the confirmation slate empty. |
| Limitations, contributions and disclosure | Discuss missing competitive holdouts, small paired samples, fixture scope and case selection. Give a confirmed member-by-member account and describe each AI-assisted phase. Put the full nine-project table, negative results and artifact links in an appendix or supplement as allowed. |

## Prior team work and report attribution

| Evidence-backed workstream | Versioned evidence | Attribution to verify with the group |
| --- | --- | --- |
| Repository scaffold, basic bots, local tournament and packaging, first Obscuro-style belief/subgame/PCFR+ implementation | `5dee721`, `1d967f8`, `50b210b` | Git history credits Ernesto Gomez on these commits. Confirm complementary design, testing or writing contributions. |
| Clock/fallback handling, repetition, UCI engine pool, Stockfish over weighted beliefs, native position helper and frozen versions | `499c100`, `29191d7`, `688d7db`, `30ff52e`, `da71d3e`, `6619d3e`, `1ae23ea` | Git history credits Sammy Krem on these commits. Confirm division of experimental and deployment work. |
| eBotI, native growing-tree search, whole-set tactical risk, prior hazard/risk variants and Greek Gift analyses | `d6cd0cf`, `3937a19`, `5948b7a`, `773a31a`, `2ba2a1b`, `4618e5d`, `5806189` | Git history credits Ernesto Gomez on these commits. Inspect earlier notes for collaboration and confirm who ran or interpreted each historical experiment. |
| New research campaign and follow-up | [Stages 0–7](../STAGE_STATUS.json), [closure](CLOSURE.md), [follow-up](FOLLOWUP_FINDINGS.md) | The user directed the sequence, research goals and follow-up decision. AI substantially assisted design, new code, tests, experiments, analysis and packaging. Attribute human review, interpretation and manuscript writing once performed. |

Git authorship establishes recorded code provenance. It cannot establish every member's design meetings, experimental execution, course proposal, or writing contributions. Confirm individual descriptions with the entire team and fill in activities for members without attributed commits. Do not infer effort from commit counts. [Historical versions](../../docs/versions.md) · [Historical experiments](../../APPROACHES.md) · [Disclosure record](../contributions.md)
