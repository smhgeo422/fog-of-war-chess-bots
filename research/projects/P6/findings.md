# P6 · Findings and closure

**Hypothesis.** Does a mixed restricted-game policy improve security over a greedy choice? [Specification](proposal.md)

**Prior work and intervention.** The team previously explored growing-tree game solving. This kernel is a bounded matrix-game experiment with exact best responses.

**V1 evidence.** Archived metric `restricted_game_exploitability_gap` = 0, recorded sample count 6000. The catalog pins source `a23eca1` and preserves the toy or restricted scope.

**Referee or replay outcome.** In the incompatible-escape referee matrix, mixed worst-case utility was −0.5043 versus −1 for greedy, with duality gap about 0.0113. When the same action was safe in both worlds, the two controls had equal security.

**Verdict.** Restricted-game mechanism supported.

**Full-clock decision.** No confirmation entry for this revision. A full-clock comparison would need a separable extensive-form policy, a blueprint safety argument and comparable engine leaf costs.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/f219ea4757a74b229b7450fb411e69ea6861b2a5/research/runs/research-offline-evidence-45076458586-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
