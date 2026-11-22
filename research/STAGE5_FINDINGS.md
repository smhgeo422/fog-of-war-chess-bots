# Stage 5 · Guided revisions and ablations

Two Stage 4 leads received isolated v2 revisions and frozen experimental protocols. Both experiments completed, and neither revision advanced to playing-strength confirmation. Earlier variants and negative results remain available on their original branches. The eBotI experiment is confined to its P3 branch and defaults to legacy behavior there.

## P8 · Extra-root allocation reliability

The Stage 4 result depended on eight decisions and a reference that reused evaluation roots. The P8 v2 revision subtracts leave-one-root jackknife uncertainty from the plug-in value of an extra root and clips the result at zero. It was compared with v1's threshold under the same quota, raw VOC ranking, margin ranking, and sixteen seeded random allocations. The frozen engine evaluated a shared shortlist of four legal candidates. Per decision, six to sixteen reference worlds were disjoint from the four initial and one optional evaluated worlds.

- The ordinary split scored 83 of 278 offered decisions across 24 paired blocks. Mean reference regret was **0.00564945 against 0.00543927 for v1**, a difference of **+0.00021017** with exploratory paired interval **[0, +0.00063052]**. Twenty-three blocks tied and one worsened. Both arms evaluated 351 roots. Their measured Stockfish work was 359,848 and 359,828 nodes.
- The shifted split scored 73 of 287 offered decisions across 24 paired blocks. Mean difference was **−0.00001124** with interval **[−0.00003371, 0]**. Twenty-three blocks tied and one improved. Both arms evaluated 308 roots.
- Most excluded decisions lacked exact prefixes at the configured cap. Of the selected v2 slots, 16 of 19 ordinary and 11 of 16 shifted slots had a zero adjusted forecast. Only 7 ordinary and 5 shifted decisions changed action when the extra work was available. Eighteen observation histories recurred across the two splits despite independent corpus seeds. Disjointness applies to the reference and evaluation worlds within each decision.

**Disposition:** leave v2 unpromoted. This test provides no ordinary holdout improvement over v1 and no robust benefit on shift. It puts a bound on the usefulness of this reliability adjustment in synthetic opening histories under a matched call quota. Live time limits, reserve policy, and breadth versus depth remain outside this comparison.

The source, full decision traces, and four audited corpora are in the [P8 v2 run index](runs/stage5-P8-v2.json).

## P3 · Reserve one reply slot for an unseen king threat

The existing eBotI infoset refinement ranks opponent replies by their modeled probability. The experimental `FOW_INFOSET_HIDDEN_REPLY=1` flag searches for a modeled reply that creates an unseen attack on our king. It can replace the last selected reply if the legacy selection contains no such threat. Both arms retain the same reply count and renormalize the same reply probabilities over their selected sets. The opt-in scan shares a bounded subdeadline and falls back to the legacy set if it runs out of time.

The referee screen covered knight-fork, bishop-diagonal, rook-file and remote-knight control fixtures. Each family included its color mirror. Both arms used the same scripted reply scores and local terminal/static utility table. The oracle considered all legal replies and a single common legal move per future observation. Both arms had matched nonterminal leaf slots on all four families.

- The selector changed the retained reply set in **18 of 32** root/world cases. The remote-knight negative control had zero changes.
- All eight color-specific scenarios selected the **same root move** under both arms. Mean oracle regret was **0.03389067** for each, a difference of **0** across the four paired families.
- Single-call selector timing was roughly 238 μs median for the opt-in selector versus 6 μs for legacy in this run. These local timings do not represent live search cost at a fixed clock.
- A deterministic engine-stub test verified that feature-off `refine()` preserved the legacy score array and UCI job sequence. Enabled wiring, elapsed selection budget and matched job counts were also tested.

**Disposition:** preserve the prototype on its branch and stop this revision. It covered omitted threats without changing the root decision on the declared fixtures. The scripted study leaves equal-clock Stockfish depth and playing strength unmeasured.

[Experimental source and controls](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P3-v2-hidden-reply-slot/tools/stage5/tactics.py) · [P3 v2 run index](runs/stage5-P3-v2.json)

## Decisions for the other seven directions

| Project | Stage 5 decision | Evidence or prerequisite |
| --- | --- | --- |
| P1 | Defer calibration work | Stage 4 had zero threat events and 40 capped histories. Freeze a wider legal-history reconstruction and a threat-bearing replay evaluation before changing sampling or repair. |
| P2 | Preserve the existing controls | The adaptive mixture gave no consistent advantage over the static mixture. Competitive or wider independent opponent histories are needed to isolate adaptation. |
| P4 | Preserve the matched-value fixture | The fixture isolates instrumental information value. Live evaluation requires action-conditioned observations and a utility control that avoids double counting P3 search gains. |
| P5 | Stop tuning the current categorical model | Only six ordinary and four shifted noncapture events were available. The ordinary effect was inconclusive and the shift went in the wrong direction. |
| P6 | Keep the restricted-game result | A referee matrix with adversarial hidden-world choice does not supply the opponent policy, blueprint, and comparable engine leaves needed for extensive-form re-solving. |
| P7 | Retire the tested residual | It lost to the fixed evaluator and simpler controls on both splits. A valid alternative-action teacher is needed before training another variant. |
| P9 | Close the declared one-turn study | Zero hidden-world certificates means no live conversion coverage in the tested domain. Extending the horizon would require a newly declared exhaustive belief domain. |

The public competitive replay endpoint returned a proxy 403 during this stage. Fresh synthetic histories were available for P8. No approved competitive replay corpus was available for the blocked endpoints above.

## Stage 6 handoff

No Stage 5 candidate has evidence supporting a 180+2 confirmatory trial or integration. The tracker advances to the confirmation decision with an empty eligible candidate set. The Stage 4 and Stage 5 findings, source commits, replay manifests and archives support an evidence-based conclusion on whether confirmation is warranted. Keep that decision separate from any further research on new data.

## Validation and reproduction

All 357 regression tests passed with real Stockfish enabled on the P3 source commit, which includes both revisions' tests. The suite reported one upstream python-chess deprecation warning. Both archives passed the offline evidence verifier.

From a clean checkout of the corresponding experiment branch, run the tracked config with the locked environment. P8 requires the native components built by `tools/setup-experiments.sh`.

```sh
.venv/bin/python tools/run_offline_experiment.py experiments/offline/P8.json --run data/research/stage5/P8-rerun
.venv/bin/python tools/run_offline_experiment.py experiments/offline/P3.json --run data/research/stage5/P3-rerun
```
