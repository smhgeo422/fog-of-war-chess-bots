# P3 · Findings and closure

**Hypothesis.** Can an observation-consistent continuation reduce root regret under the same search budget? [Specification](proposal.md)

**Prior work and intervention.** The team already implemented eBotI infoset refinement. The v1 kernel checked strategy fusion. The opt-in v2 variant changed one legacy reply slot.

**V1 evidence.** Archived metric `bounded_contingent_strategy_fusion_gap` = 0.5, recorded sample count 2. The catalog pins source `037f595` and preserves the toy or restricted scope.

**Referee or replay outcome.** Stage 4 observed mean regret of 0 versus 0.125 for a fixed blind continuation on eight restricted roots. Stage 5 changed 18 of 32 reply sets but zero of eight root decisions. Both arms had the same mean oracle regret of 0.03389067 across four paired fixture families.

**Verdict.** Fixture mechanism supported. V2 produced no measured decision improvement.

**Full-clock decision.** No confirmation entry for this revision. The tested revision stopped at matched scripted leaf counts. Equal-clock Stockfish depth and naturally occurring threat coverage would need their own checks.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/1e676a21333ab67f37f8961665da802b226ee7b0/research/runs/research-offline-evidence-45076165589-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Stage 5 v2 catalog](../../runs/stage5-P3-v2.json) · [Stage 5 findings](../../STAGE5_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
