# P4 · Findings and closure

**Hypothesis.** Does an observation have value when it enables a better continuation at matched direct payoff? [Specification](proposal.md)

**Prior work and intervention.** The contribution tested a decision-sensitive information term, distinct from prior general information-set reasoning.

**V1 evidence.** Archived metric `instrumental_information_value_matched_action` = 0.5, recorded sample count 2. The catalog pins source `5b7c84d` and preserves the toy or restricted scope.

**Referee or replay outcome.** The informative root was worth 0.5 versus 0 for the irrelevant root, while revealing 8.5 rather than 10 squares on average. Both roots scored zero information value when the same escape worked in both worlds.

**Verdict.** Restricted fixture supports decision-sensitive information value.

**Full-clock decision.** No confirmation entry for this revision. A live comparison needs an action-conditioned observation forecast and a direct-value control to avoid double counting the continuation.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/8f3e528331f7cd2740471f5c51cad6b4e4be648b/research/runs/research-offline-evidence-45076169979-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
