# Autonomous Code Verification

## What This Is
Multi-agent code verification system with formal safety guarantees.
Implements the theory from "From the Verification Paradox to Multi-Agent Self-Verification."

## Commands
```bash
python -m pytest tests/ -v
python experiments/exp1_single_vs_multi.py
python benchmark/run_benchmark.py
```

## Architecture
- src/models/ -- Theoretical models (verification paradox, multi-agent, convergence, deployment)
- src/verifier/ -- Multi-agent verification engine (5 strategies + aggregator)
- src/sdd/ -- Spec-Driven Development (parser, compliance checker, gap discovery)
- src/e2e/ -- End-to-end self-correction loop (test runner, fix loop, convergence)

## Key Conventions
- All theory code matches paper equations exactly
- LLM strategies use JSON response format
- Tests run without API keys (model-based)
