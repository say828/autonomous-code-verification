"""Experiment 5: Cross-Provider Verification (GPT/Gemini/Claude)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import numpy as np
from models.multi_agent import V_multi_agent
from models.verification_paradox import human_verification_effectiveness

def run():
    """Analyze cross-provider diversity benefits.

    Theoretical analysis using published benchmark data for different LLM providers.
    """
    providers = {
        'claude': {'V_agent': 0.90, 'model': 'Claude Sonnet 4.5'},
        'gpt': {'V_agent': 0.85, 'model': 'GPT-4o'},
        'gemini': {'V_agent': 0.82, 'model': 'Gemini 1.5 Pro'},
    }

    print("Cross-Provider Verification Analysis")
    print("=" * 50)

    for name, info in providers.items():
        print(f"  {name}: V_agent = {info['V_agent']:.2f}")

    V_avg = np.mean([p['V_agent'] for p in providers.values()])

    results = {'providers': providers, 'analysis': {}}

    for d in [0.3, 0.5, 0.8, 1.0]:
        V_m = V_multi_agent(V_avg, 3, d)
        results['analysis'][f'd={d}'] = {'V_multi': float(V_m), 'n_eff': 1 + 2*d}
        print(f"\n  d={d}: V_multi = {V_m:.6f} (n_eff = {1+2*d:.1f})")

    for E_ai in [0.15, 0.05, 0.01]:
        V_h = human_verification_effectiveness(E_ai)
        V_m = V_multi_agent(V_avg, 3, 0.8)
        results['analysis'][f'E_ai={E_ai}'] = {
            'V_human': float(V_h), 'V_multi': float(V_m),
            'agent_advantage': float(V_m - V_h),
        }

    os.makedirs('experiments/results', exist_ok=True)
    with open('experiments/results/exp5_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved.")

if __name__ == '__main__':
    run()
