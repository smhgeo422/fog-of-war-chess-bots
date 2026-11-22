# Execution protocol: nine research contributions, no report writing

**Planning document only — no implementations or tournaments authorized by this file.**
**Research taxonomy:** 'research/consolidated_contributions.md' (P1–P9). Crosswalk: 'research/consolidated_crosswalk.json' (all 46 old items). This protocol is initiated **only** when the user explicitly requests a research batch; there is no calendar schedule, no autonomous recurrence, no automatic merge to main, no official MIT arena submission.

## Definition of the finish line

The project is *research-complete* only when each of the **nine** projects has (a) a legitimate code-level or algorithmic intervention, or a documented feasibility blocker supported by an attempted minimal implementation; (b) a frozen question and primary outcome; (c) unit/toy validation; (d) controlled offline analysis or match evidence appropriate to the claim; (e) an evidence-linked scientific verdict; (f) a GitHub branch, immutable source SHA, configuration, and archival record. Winning variants may be integrated into a separately tested final bot. This is not a promise that every project can have positive full-clock results within one day.

Do **not** count a 244-test green suite as evidence that a new research algorithm is strong. Do **not** count the 46 source sketches as 46 contributions. Do **not** count a source code implementation without any causal experiment as a validated algorithm. Never convert a negative result or infeasibility into fabricated positive evidence.

## Phase 0 — Lock scientific hypotheses (one large planning batch)

**Inputs:** prior team work 'APPROACHES.md', 'docs/research/', current bot source, old 46-item backlog and original code switches, validated reference literature.

**Actions:**
1. Confirm P1–P9 genuinely differ in manipulated variable, outcome and counterexample. Check all source overlaps and classify what is already a teammate contribution.
2. For each project freeze: hypothesis, null, primary and secondary outcomes, data requirements, v1 smallest viable intervention, ablations/controls, and explicit stop criteria.
3. Validate original-to-new ID crosswalk (46 exact once). Preserve original backlog without deletion or rewritten provenance.
4. Inspect course rules and dataset permissions before using public replay data or an opponent identity feature.
5. Create 'research/projects/P1' through 'P9' documentation stubs with a project-specific evidence ledger. Do not imply implementations exist.

**Deliverable:** taxonomy, 9 implementation specifications, 46-ID crosswalk, dependency map, 9 falsification-ready experimental cards. **Gate:** user may review before expensive coding; changes to the nine projects require explicit reason and approval.

## Phase 1 — Upgrade reproducibility infrastructure for project IDs (one engineering batch)

**Why required:** current action workflow derives 'A01..F99' from 'experiment/<legacy-ID>-...' branches, and the archiver only accepts those IDs. It will **not** automatically run 'experiment/P1-...' correctly without a tested schema change. The old runner also expects a specific bot directory and tracked config. We must not claim nine-project automation is ready until this is fixed.

**Actions:**
1. Extend the archiver identifier, CI branch parser and experiment config naming to P1..P9, while retaining backward compatibility with all old records and the existing 'Infra' smoke.
2. Define branch pattern 'experiment/P1-v1-<short-description>', similarly for P2..P9. An experiment config 'experiments/configs/P1.json' is **committed on that branch** with unique run ID and experiment metadata; repeat on each branch. For multiple versions, each has its own branch and config, and immutable manifest records the exact version/commit.
3. Add machine-readable 'research/projects.json' with one P1..P9 entry, including status, hypotheses, branches, run IDs, evidence links, and verdict. Leave 'research/experiment_registry.jsonl' as legacy proposal provenance, not the sole current scoreboard.
4. Record complete environment variables, binary digests, CPU quota and Stockfish version; verify validation branch parity before tests.
5. Prevent CI explosion: group source commits and push only finalized test candidates; exact '[run experiment]' token is required before expensive games. Use per-branch concurrency and avoid CPU oversubscription.
6. Add CLI/script for verifying downloaded draft-release tar.gz assets, SHA-256, and replay counts. Ensure a failed match records its failure. Verify release-indexing with one new P1-format two-game **smoke** experiment (not strength evidence).
7. Save an independently reproducible experimental instructions page. Do not merge into main; workflow branch-push triggering remains sufficient.

**Deliverable:** branch naming and metadata system supporting P1..P9, machine-readable state registry, passing code/unit tests, and verified permanent archive smoke. **Gate:** no algorithm batch until this experiment identity and evidence loop passes.

## Phase 2 — Freeze controls and build the offline evaluation corpus (one large measurement batch)

**Actions:**
1. Define B0 = untouched frozen obscuro_v4, B1 = eBotI set to v4 parity, B2 = current eBotI defaults. Verify actual decision parity on recorded observation histories, not merely equality of flags. Identify exact non-equivalences.
2. Assign controlled opening/color/seed blocks, allow-listed opponent pools, consistent Stockfish network and CPU/core limits, baseline time policy, and immutable run configs. Separate *screening* clocks from 180+2 confirmation.
3. Validate event/observation reconstruction from the real local referee rules, including legal moves, castling, en passant, king capture, clocks and fog visibility. Truth board from saved replay may be a **retrospective label**, never a model input that the live bot couldn't see.
4. Partition games into training / model-development / *untouched* confirmation by entire game, opponent and (where meaningful) time; never scatter positions from the same replay into train and test.
5. Precompute source-linked diagnostic labels: hidden attack, unseen-material capture, immediate king catastrophe, opponent move likelihood, future observations, game outcome, and compute cost, all with explicit feature availability times.
6. Re-run a small clean baseline/control smoke, then targeted full-length baseline matches if budget permits. Preserve errors and all full replay records.

**Deliverable:** immutable baseline manifest, parity test and failure list, data lineage, offline label validation suite, prior result reconciliation, first control tables. **Gate:** trust no cross-method win-rate comparison until controls pass.

## Phase 3 — Implement nine minimal independent first versions (separate code batches within one implementation stage)

Use a separate branch for every project and its subsequent versions. Each must start with correctness tests and an offline experiment; don't launch a tournament just because it compiles. Implementations should be orthogonal. No shared player module should be edited without showing how the feature is disabled for parity controls.

**P1 belief reconstruction:** exact tiny-state oracle, history-valid particle repair or importance-corrected threat sampling; primary: truth support and held-out hazard calibration.

**P2 opponent behavior:** style-conditioned likelihood estimator and shrinkage/floor, with no unauthorized opponent private observation; primary: held-out move negative log likelihood.

**P3 contingent search:** correct existing two-ply infoset grouping plus selective deepening; primary: action consistency and regret on partial-observation toy tactical cases.

**P4 information incentives:** decision-value VOI based on future choice changes plus a matched reveal/denial control; primary: predicted versus realized consequential observations.

**P5 catastrophic risk:** selective quiet-piece/hunt hazard or correctly scaled terminal utility, beyond current FOW_HANG and safe-first toggles; primary: held-out risk calibration and avoidable hidden losses.

**P6 bounded strategic re-solving:** toy game with known equilibrium, then restricted deep-leaf solver; primary: toy exploitability/security and CPU cost, not presumptive win-rate gain.

**P7 learned continuation value:** leakage-safe low-capacity residual predictor; primary: held-out post-move value forecast and action-ranking improvement.

**P8 adaptive compute:** action-margin/uncertainty-based value-of-computation controller; primary: decision quality per CPU/clock at fixed aggregate compute.

**P9 endgame policy:** exact small-state FoW reachability/pursuit implementation; primary: endgame correctness/guarantee and conversion, not artificially inflated whole-game Elo.

**Deliverable per P:** branch+commit, tested implementation, enabled/disabled parity, mathematical derivation and pseudocode, small offline result, experimental config, traceable AI and human contribution attribution. **Gate:** an untestable v1 is marked blocked with attempted code and failure evidence; no invented scores.

## Phase 4 — Independent screening batches (one or several tournament-launch batches)

1. For each validated v1, freeze its variant settings and exact baseline. Run even numbers of color-balanced matches and predeclared seeds, with CPU quota and no concurrent oversubscription. A reasonable initial 20-game match is *exploratory*, not evidence of small performance differences.
2. For some projects, an offline metric is the primary evaluation (P1 posterior calibration, P2 policy likelihood, P6 toy exploitability, P7 forecast quality, P8 matched-budget quality, P9 exact endgame tests); do not shoehorn every method into just 20 games.
3. Save all replays and failures, verify archived release assets and SHA-256, write per-run catalog into branch plus central aggregation index. Record opponent, board sample policy, time control, W/D/L, paired interval, CPU, p95 latency, hardware, and whether the experiment was exploratory.
4. Separate screening candidate changes from baseline/book/clock confounds. Save selection criteria *before* looking at tournament results; flag post-hoc hypothesis changes.
5. Do not mark a 20-game near-even result 'winner'. Report exact score, wide uncertainty, and any terminations.

**Deliverable:** 9-project screening dashboard, downloadable checksummed evidence, negative controls, metric tables, completed-run registry, and initial go/no-go decisions.

## Phase 5 — Guided iterations inside projects (targeted implementation + retest batches)

1. Use the evidence to pick the most causally informative failure mode *within each fixed project*, not to invent an unrelated tenth contribution.
2. Make v2/v3 branches with one motivated change (e.g., P1 proposal repair versus sampling; P3 2-ply versus 4-ply; P5 capture-aware risk; P8 learned stopping).
3. Preserve earlier versions, prove correctness, and repeat offline controls then screen with independent seeds.
4. For unsuccessful or computationally infeasible research, close it with an evidence-based negative/inconclusive verdict rather than endless tuning.
5. Compare to old team versions before crediting novelty. Record which changes are improvements made in the current campaign and which were authored earlier.

**Deliverable:** per-project version tree, variant comparisons, reasons for retained/rejected modifications, updated hypothesis-specific results, checked contribution records. **Gate:** stop when further variants lack motivation or compute justification.

## Phase 6 — Independent confirmation / robust final candidate (one or several expensive batches)

1. Pre-register final candidates and untouched opponents/seeds; run 180+2 full games with complete observations and identical clock/hardware constraints. Use matched color blocks and appropriate paired confidence intervals.
2. If matches require longer than the ~350-minute workflow job cap, split into smaller immutable game shards and then aggregate only complete/shard-consistent results. Never silently remove stopped games.
3. Control multiple selection across nine projects and variants: distinguish exploratory screening from confirmatory holdout and avoid choosing hyperparameters on the same holdout games.
4. Measure worst-opponent and average score, hidden-material and king-risk proxies, timeouts, and compute efficiency. Report uncertainty; small win-rate differences may remain inconclusive.
5. **Integration is supporting engineering, not a tenth scientific idea.** Combine only independently validated mechanisms, create integrated-candidate branch, measure single-feature ablations and pairwise interactions; the integrated candidate might underperform its parts.
6. Keep a verified, immutable candidate bot branch and clean replay evidence. Do not merge into main or submit to the MIT arena.

**Deliverable:** confirmed results where sample size permits; accurate confidence intervals, holdout/game-level tables and example replays; best candidate branch if evidence supports one; negative evidence where it doesn't.

## Phase 7 — Archive, audit and prepare report inputs (one evidence-consolidation batch; NOT report writing)

1. Validate all P1..P9 project IDs and statuses; every claimed result must have an existing GitHub commit, baseline config, completed matched experiment report, and a verified archive asset.
2. Rebuild machine-readable 'research/combined_results.json' and 'research/combined_results.csv' solely from archived per-run catalogs. Include full uncertainty, not just win percentages. Keep exact metric definitions.
3. For each project write 'research/projects/Px/findings.md': hypothesis; novelty relative to team/prior literature; implementation versions; best/rejected options; key tables; fail cases; evidence links; limitations; status.
4. Update 'research/results_index.md', 'research/contributions.md', and 'research/report_outline.md' to point to verified runs and correctly attribute original teammate implementations, new agent-written code, user-directed research design, and any later human review.
5. Compile 'research/report_package/': bibliography and papers, figures/tables data and generation code, representative replay pointers, methodology, candidate summary and explicit limitations. **Do not draft the final class report unless requested.**
6. Produce project closure sheet showing nine verdicts and whether further full-clock compute would materially change a conclusion.

**Deliverable:** a complete, GitHub-resident, report-ready reproducibility bundle plus original code and archives. Do not claim project completion if any result lacks provenance; label unfinished work.

## Branch and artifact conventions

- Canonical research projects: P1..P9. Legacy A01..F08 IDs are historical idea references in the preserved crosswalk, never silently deleted.
- Dedicated v1 branches: 'experiment/P1-v1-...', 'experiment/P2-v1-...', etc.; new v2/v3 branches for substantive revisions. The Phase 1 schema migration MUST happen first.
- Each branch carries exactly one hypothesis and a tracked experiment config. A run ID embeds project/variant/seed block plus GitHub run identifier; no overwrites.
- Source of truth: Git SHA + tracked config + run's manifest/report/replays + checksummed, draft GitHub Release archive + permanent 'research/runs/' catalog.
- Per-project files: 'research/projects/Px/{proposal.md,variants.jsonl,findings.md}'. Cross-project dashboard derived from verified catalogs.
- Stable working bot branch and optional integrated final candidate are *distinct* from frozen baseline and main.
- Never run an experiment with an uncommitted or unverified candidate; never modify a frozen bot to make it 'win'.

## Why step-specific batches are required

The six causal dependencies are: **hypotheses → reproducibility → baselines/datasets → code → results → evidence-guided revisions → confirmation → report package**. Source code for all nine can be developed in separate sub-batches, and multiple experiments can be launched together once variants are frozen; however, an agent should not choose a second round of algorithm revisions before seeing the first round's data.

A single prompt can perform substantial *one-stage* work, but it cannot promise a fixed-time completion of all nine algorithms and all full-clock chess games. Existing GitHub Actions runs may finish asynchronously after triggering; the agent must explicitly retrieve their outcomes when requested. No scheduled research continuation is authorized.

**User-controlled stage gates:** the user chooses when to initiate each major batch; no recurring tasks or silent research schedules. A detailed batch completion report should include exactly which GitHub artifacts exist, which CI run IDs passed, the scientific conclusions supported so far, and what remains blocked or underpowered.
