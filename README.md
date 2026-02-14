# Autonomous Code Verification

Multi-agent autonomous code verification system with formal safety guarantees.

## Overview

This repository implements the theoretical framework and empirical experiments from "Autonomous Code Verification: From the Verification Paradox to Multi-Agent Self-Verification."

**Key results:**
- **Verification Paradox**: H* -> 0 as E_ai -> 0 (human oversight becomes worthless as AI improves)
- **Crossover**: Agent verification surpasses human at E_ai* ~ 0.2053
- **V_max ceiling**: Single-agent self-verification capped at ~85% (blind spots)
- **Multi-agent diversity**: Overcomes V_max via complementary blind spots
- **P(failure)**: ~ 10^-6 with honest bounds (n=5, d=0.5, k=10)

## Installation

```bash
pip install -e ".[dev,llm]"
```

## Quick Start

```python
from models.multi_agent import V_agent, V_multi_agent, AgentVerificationParams
from models.verification_paradox import human_verification_effectiveness

# Compare human vs agent verification at E_ai=0.05
V_h = human_verification_effectiveness(0.05)
V_a = V_agent(0.05)
V_m = V_multi_agent(V_a, n_agents=5, diversity=0.5)

print(f"Human: {V_h:.4f}, Agent: {V_a:.4f}, Multi-agent: {V_m:.4f}")
```

## Structure

```
src/
  models/          # Theoretical models (Paper 1+2)
  verifier/        # Multi-agent verification engine
  sdd/             # Spec-Driven Development framework
  e2e/             # End-to-end self-correction loop

benchmark/           # Test corpus and benchmarks
experiments/         # Reproducible experiments
tests/               # Unit + integration tests
docs/                # Architecture and methodology
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Running Experiments

```bash
# Experiment 1: Single vs multi-agent comparison
python experiments/exp1_single_vs_multi.py

# Experiment 2: Diversity scaling
python experiments/exp2_diversity_scaling.py
```

## License

MIT
