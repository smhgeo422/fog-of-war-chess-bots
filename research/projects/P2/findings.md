# P2 · Findings and closure

**Hypothesis.** Does updating a latent opponent style from visible events improve held-out action likelihood? [Specification](proposal.md)

**Prior work and intervention.** The prior engine likelihood and uniform floor were existing team work. The prototype tested style adaptation over a fixed hypothetical history support.

**V1 evidence.** Archived metric `observable_event_style_model_retrospective_action_nll` = 0.66853622, recorded sample count 180. The catalog pins source `d90ee98` and preserves the toy or restricted scope.

**Referee or replay outcome.** Stage 4 action NLL over 129 early decisions averaged 3.480 versus Stockfish 3.937 in-family, and 3.440 versus 3.967 on shift. Online adaptation was slightly worse than the static mixture in-family. The shifted action contrast versus static was about −0.0023 and its paired interval crossed zero.

**Verdict.** Mixed synthetic result with no consistent adaptation benefit.

**Full-clock decision.** No confirmation entry for this revision. A wider opponent replay sample is needed to distinguish adaptation from the base mixture. A game tournament without that control would combine the two effects.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/fdcfdd750c1435094ab6955deee3b2f07f17f6b0/research/runs/research-offline-evidence-45076160806-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
