# Bibliography and attribution sources

Titles and links point to primary papers or the repository's authoritative course materials where available. The earlier literature review records which materials were inspected as papers or abstracts and the boundaries of each citation.

| Use | Source |
| --- | --- |
| FoW rules and bot protocol | [MIT 6.7980 Fog of War Chess challenge](https://www.mit.edu/~6.7980/fow/) · [Versioned starter kit](../../starter/README.md) |
| Belief sampling and observation planning | Silver and Veness (2010), *Monte-Carlo Planning in Large POMDPs*. [NeurIPS](https://proceedings.neurips.cc/paper/2010/hash/edfbe1afcf9246bb0d40eb4d8027d90f-Abstract.html) |
| History-compatible states | Solinas, Rebstock, Sturtevant and Buro (2023), history filtering in imperfect-information games. [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2023/hash/87ee1bbac4635e7c948f3eea83c1f262-Abstract-Conference.html) |
| Opponent likelihood and comparison game | Gardner et al. (2023), *The Reconnaissance Blind Chess Competition*. Its sensing and move rules differ from FoW chess. [PMLR](https://proceedings.mlr.press/v220/gardner23a.html) |
| Strategy fusion | Cowling, Powley and Whitehouse (2012), *Information Set Monte Carlo Tree Search*. [Author manuscript](https://eprints.whiterose.ac.uk/id/eprint/75048/) |
| Tactical and game-theoretic search | Zhang and Sandholm (2026), Obscuro. [ICLR](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9705eec26e511d7844a591ce10c33a3f-Abstract-Conference.html) |
| Knowledge-limited and safe re-solving | Zhang and Sandholm (2021), knowledge-limited subgame solving. [NeurIPS](https://proceedings.neurips.cc/paper/2021/hash/c96c08f8bb7960e11a1239352a479053-Abstract.html) · Brown and Sandholm (2017), *Safe and Nested Subgame Solving for Imperfect-Information Games*. [NeurIPS](https://papers.nips.cc/paper_files/paper/2017/hash/7fe1f8abaad094e0b5cb1b01d712f708-Abstract.html) |
| Predictive regret | Farina, Kroer and Sandholm (2021), predictive Blackwell approachability. [AAAI record](https://mlanthology.org/aaai/2021/farina2021aaai-faster/) |
| Calibration and proper scoring | Gneiting and Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*. [DOI](https://doi.org/10.1198/016214506000001437) |
| Learned value and search | Brown et al. (2020), ReBeL. [NeurIPS](https://papers.nips.cc/paper/2020/hash/c61f571dbd2fb949d3fe5ae1608dd48b-Abstract.html) · Schmid et al. (2023), *Student of Games*. [DOI](https://doi.org/10.1126/sciadv.adg3256) |
| Computation allocation | Hay, Russell, Tolpin and Shimony (2012), *Selecting Computations: Theory and Applications*. [PMLR](https://proceedings.mlr.press/r10/hay12a.html) |
| Certified endgames | Gehnen and Stannat (2026), FoW endgames. Their theoretical guarantees concern the paper's rules and horizons. [Dagstuhl](https://doi.org/10.4230/LIPIcs.FUN.2026.21) |
| Engine | Verified Stockfish 19 release, pinned source and NNUE. [Release](https://github.com/official-stockfish/Stockfish/releases/tag/sf_19) · [Repository setup](../../tools/setup-experiments.sh) |

For earlier team work, cite the [prior approaches](../../APPROACHES.md), [version history](../../docs/versions.md) and [code attribution record](../contributions.md). The user directed the research questions and stage decisions. AI-assisted implementation, experiments, verification and preparation are tracked in the contribution record; human validation and individual teammate attributions should be confirmed before the course report. [Annotated literature and novelty boundaries](../stage0_literature_review.md)
