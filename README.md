# Analysing Condorcet's Jury Theorem using ABMs

An honours thesis research project for PE4401P investigating the robustness of **Condorcet's Jury Theorem (CJT)** when voters communicate, share evidence, and develop informationally dependent judgments.

> **Project status:** Research and prototype development. The scientific simulation and experimental results described below are planned; they are not yet validated findings.

## Research question

**How do different mechanisms of information sharing affect the epistemic reliability of majority voting when the classical independence assumption is relaxed?**

The project compares independent voting with two stylised forms of evidence exchange: agents that count repeated messages as new evidence and agents that track evidence provenance to avoid double-counting.

## Background

In the classical CJT, an odd-sized jury makes a binary decision with one objectively correct answer. If each voter is independently correct with the same probability (p > 0.5), the probability of a correct majority approaches 1 as the jury grows.

However, real-world judgments may not be independent: people encounter common sources, share evidence, and influence one another. This project uses an agent-based model to examine the consequences of such mechanisms **within a specified simulated environment**, rather than claiming to prove or disprove CJT or to predict real elections.

## Research objectives

1. **Verify the implementation:** reproduce classical CJT probabilities under homogeneous, conditionally independent voting.
2. **Relax independence:** allow agents to communicate through a social network.
3. **Compare information-processing rules:** independent voting, naive evidence sharing, and source-aware evidence sharing.
4. **Evaluate epistemic performance:** measure majority accuracy, individual accuracy, error correlations, and belief confidence.
5. **Test robustness:** vary population size, signal reliability, communication rounds, and network configuration.

## Proposed model

Each simulated election will:

1. Sample a hidden binary state of the world.
2. Initialise agents with priors, private-signal reliability, and network connections.
3. Generate conditionally independent private signals with unique evidence identifiers.
4. Update agents' beliefs using Bayesian log-odds.
5. Optionally run synchronous communication rounds, according to the selected evidence-sharing rule.
6. Convert final credences into binary votes and apply simple majority rule.
7. Record accuracy and dependence measures.
8. Repeat across Monte Carlo trials and parameter configurations.

For a symmetric binary signal (s in {0,1}) with reliability (q), a Bayesian log-odds update is

$$ L_i(t+1) = L_i(t) + (2s-1)\log\frac{q}{1-q} $$

Adding multiple signal contributions in this form assumes the relevant conditional-independence structure. The proposed experiments specifically examine the consequences of violating that assumption through repeated evidence.

### Experimental conditions

| Condition | Communication | Evidence handling |
| --- | --- | --- |
| Independent baseline | None | Private signals only |
| Naive sharing | Network-based | Repeated transmissions may be counted again |
| Source-aware sharing | Network-based | Previously seen evidence identifiers are not counted again |

### Planned metrics

- **Collective accuracy:** fraction of simulated elections in which the majority matches the true state.
- **Individual accuracy:** fraction of agent votes that match the true state, measured before and after communication.
- **Error correlations:** dependence between agents' mistakes, estimated across repeated elections.
- **Belief confidence and calibration:** how certainty relates to correctness.
- **Evidence redundancy:** how often information is retransmitted without introducing a distinct source.

## Proposed repository layout

```text
condorcet-jury-theorem-abm/
├── README.md
├── LICENSE.md
├── .gitignore
├── requirements.txt          # add when dependencies are finalised
├── src/
│   └── condorcet_abm/
│       ├── agents.py
│       ├── evidence.py
│       ├── networks.py
│       ├── model.py
│       └── metrics.py
├── experiments/
├── tests/
├── docs/
├── prototypes/
└── results/                  # generated outputs; generally not committed
```

The directories above are **proposed**, not files already included in this starter repository.

## Getting started (once the model is implemented)

```bash
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

When `requirements.txt` is added:

```bash
python -m pip install -r requirements.txt
```

Simulation commands and reproducibility instructions will be added after the model's command-line interface is implemented. **This repository does not yet contain a runnable scientific simulation.**

## Reproducibility plan

Experimental runs should record model version, parameter settings, random seeds, number of Monte Carlo replications, and summary statistics. The independent-voter baseline should be checked against the analytical binomial benchmark before interpreting extensions.

## Selected references

- Condorcet, M. de. (1785). *Essai sur l'application de l'analyse à la probabilité des décisions rendues à la pluralité des voix*.
- Wallick, R. R. (2012). *Agent-Based Models in Public Choice* (doctoral dissertation), Chapter 3.
- Hahn, U., von Sydow, M., & Merdes, C. (2019). How communication can make voters choose less well. *Topics in Cognitive Science, 11*(1), 194–206. https://doi.org/10.1111/tops.12401
- DeMarzo, P. M., Vayanos, D., & Zwiebel, J. (2003). Persuasion bias, social influence, and unidimensional opinions. *The Quarterly Journal of Economics, 118*(3), 909–968. https://doi.org/10.1162/00335530360698469
- Zollman, K. J. S. (2007). The communication structure of epistemic communities. *Philosophy of Science, 74*(5), 574–587. https://doi.org/10.1086/525605

## License

The proposed code license is MIT; see [LICENSE.md](LICENSE.md). This license does not grant rights to third-party research papers or datasets. Review the license choice and fill in the copyright holder before publishing.
