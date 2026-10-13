# Verifier-Guided PDE Agent

**Symbolic verification and feedback-guided reasoning for heat-equation problems**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/) [![AWS Trainium2](https://img.shields.io/badge/Compute-AWS%20Trainium2-232F3E?logo=amazonaws&logoColor=white)](https://aws.amazon.com/ai/machine-learning/trainium/)

**Annapurna Labs Hackathon · NYU Team 126**  
[Original hackathon submission (PR #11)](https://github.com/yahavb/trainium-agent-labs/pull/11)

## Overview

Large language models can generate plausible-looking mathematical solutions that fail a differential equation or its boundary and initial conditions. This project explores a **generate → verify → revise** workflow for one-dimensional heat-equation problems. A Qwen3-8B model proposes candidate expressions; symbolic and numerical checks evaluate them; feedback is used to guide further attempts or to select candidates.

Our team's extensions to the provided heat-rod agent focus on **SymPy-based PDE verification**, **verifier-guided candidate revision**, and **independent candidate selection**. The project includes experiment logs and a Streamlit interface for exploring recorded evidence and optionally running the agent against a reachable model endpoint.

## Architecture

```text
Heat-equation test case
         |
         v
 Qwen3-8B candidate generation
 (vLLM on AWS Trainium2 during hackathon runs)
         |
         v
 PDE + boundary/initial-condition checks
 (pdecheck.py and symbolic_verifier.py)
         |
         +----> Candidate accepted / logged
         |
         +----> Checker feedback -> revised candidates
         |
         +----> Independent candidate selection (separate variant)
```

The verification score reflects whether a proposed expression satisfies the governing equation, boundary conditions, and initial condition. The agent records attempts, feedback, and rewards for later inspection.

## Recorded results

| Experiment | Problems passed | Total tested |
| --- | ---: | ---: |
| Baseline | 4 | 5 |
| Verifier-guided | 5 | 5 |
| Independent candidate selection | 2 | 2 |

**Interpretation:** These are small, recorded tests, **not** evidence of general accuracy or statistical significance. Independent candidate selection was evaluated on a **separate two-case test**, not the same five-case comparison. The verifier-guided revision loop uses checker feedback; it is not a claim that the model solves the problems without assistance. See [`experiment-results/`](experiment-results/) for run artifacts.

## Technology

- **Model/inference:** Qwen3-8B, vLLM, AWS Trainium2 (hackathon environment)
- **Verification and tooling:** Python, SymPy, PDE and boundary-condition checks
- **Experimentation:** JSONL attempt logs, CSV analysis, candidate selection and revision
- **Interface:** Streamlit, pandas, NumPy

## Repository guide

| File | Purpose |
| --- | --- |
| `agent.py` | Base heat-rod agent |
| `agent_verified_success.py` | Verifier-guided candidate revision workflow |
| `agent_independent.py` | Independent candidate-selection variant |
| `symbolic_verifier.py` | Symbolic verification routines |
| `pdecheck.py` | PDE and condition checker |
| `level0_heatrod.py`, `level1_heatrod.py` | Test problems |
| `tool_calc.py` | Symbolic calculator support |
| `analyze_results.py` | Experiment analysis |
| `experiment-results/` | Recorded experiment evidence |
| `webapp.py` | Streamlit demonstration UI |
| `Presentation.pdf` | Hackathon presentation |
| `ORIGINAL_STARTER_README.md` | Original starter-project notes, caveats, and detailed run instructions |

## Getting started

From the repository root, with Python installed:

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
pip install sympy numpy pandas streamlit openai
```

**Check the local test definitions:**

```bash
python level0_heatrod.py --selftest
python level1_heatrod.py --selftest
```

**Open the dashboard:**

```bash
python -m streamlit run webapp.py
```

Select **Saved results** to inspect local experiment evidence without making model calls. The heat-diffusion chart is an analytical illustration, **not** a model prediction.

**Run live inference (requires a model endpoint):**

```bash
python agent_verified_success.py \
  --level 1 --sub 3 --samples 2 --rounds 2 \
  --base http://localhost:8000/v1 \
  --log attempts.jsonl
```

The `localhost` endpoint works only when a compatible Qwen3-8B vLLM server is running on the **same machine** (or a tunnel maps it locally). A local Mac installation of Streamlit **does not automatically connect** to the hackathon's Trainium2 pod. The original environment-specific setup is documented in [`ORIGINAL_STARTER_README.md`](ORIGINAL_STARTER_README.md); its example pod names and paths refer to the starter project and may require adaptation.

## What we learned

- **Checkable intermediate feedback matters.** A candidate can satisfy part of the PDE task while failing other conditions; granular feedback can help identify what to revise.
- **Verifier quality matters.** Revealing target coefficients can make a model appear successful by copying them. The starter documentation explicitly describes this pitfall; our results should be read with that limitation in mind.
- **Tool assistance is distinct from independent reasoning.** A symbolic calculator can evaluate requested integrals, but the model must still formulate appropriate expressions and combine them correctly.
- **Small experiments are a starting point.** Broader benchmarks, independent test sets, and repeated seeds are needed before making general performance claims.

## Team and attribution

Built by **NYU Team 126** at the Annapurna Labs Hackathon:

- Vinay Kumar
- Saishruti Sairam Vedha
- Akhil Vardan Mallipeddu
- Karuna Venkatesh
- Sai Rithwik Amajala

This work extends the hackathon's **Project 1 — Heat-Rod Agent** starter. Credit for the original problem setup and starter workflow belongs to the hackathon organizers; our extensions and experimental artifacts are described above. See the [original submission](https://github.com/yahavb/trainium-agent-labs/pull/11) and [preserved starter notes](ORIGINAL_STARTER_README.md).
