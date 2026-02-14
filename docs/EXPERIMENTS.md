# Experiment Protocols

## Running Experiments

All experiments can be run without API keys (using theoretical models):

```bash
python experiments/exp1_single_vs_multi.py
python experiments/exp2_diversity_scaling.py
python experiments/exp3_self_correction.py
python experiments/exp4_spec_impact.py
python experiments/exp5_cross_provider.py
```

Results are saved to `experiments/results/`.

## With LLM API Keys

Set environment variables:
```bash
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key
```

Then run the benchmark with live verification:
```bash
python benchmark/run_benchmark.py --strategies all
```
