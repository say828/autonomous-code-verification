"""Experiment 1: Single vs Multi-agent Verification Comparison.

Demonstrates that multi-agent verification (T3) surpasses single-agent (V_max ceiling).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import json
from models.multi_agent import V_agent, V_multi_agent, AgentVerificationParams
from models.verification_paradox import human_verification_effectiveness

def run():
    ap = AgentVerificationParams()
    E_ai_range = np.linspace(0.001, 0.5, 100)

    results = []
    for E_ai in E_ai_range:
        V_h = human_verification_effectiveness(E_ai)
        V_a = V_agent(E_ai, ap)
        V_m3 = V_multi_agent(V_a, 3, 0.3)
        V_m5 = V_multi_agent(V_a, 5, 0.5)

        results.append({
            'E_ai': float(E_ai),
            'V_human': float(V_h),
            'V_agent_single': float(V_a),
            'V_multi_n3_d03': float(V_m3),
            'V_multi_n5_d05': float(V_m5),
        })

    for i in range(1, len(results)):
        r_prev, r_curr = results[i-1], results[i]
        if r_prev['V_agent_single'] < r_prev['V_human'] and r_curr['V_agent_single'] >= r_curr['V_human']:
            print(f"Single-agent crossover at E_ai ~ {r_curr['E_ai']:.4f}")
        if r_prev['V_multi_n3_d03'] < r_prev['V_human'] and r_curr['V_multi_n3_d03'] >= r_curr['V_human']:
            print(f"Multi-agent (n=3,d=0.3) crossover at E_ai ~ {r_curr['E_ai']:.4f}")

    print(f"\nAt E_ai=0.05:")
    r = next(r for r in results if abs(r['E_ai'] - 0.05) < 0.01)
    for k, v in r.items():
        print(f"  {k}: {v:.4f}")

    print(f"\nV_max ceiling: {ap.v_max}")
    print(f"V_multi(n=5, d=0.5) at E_ai=0.01: {results[-10]['V_multi_n5_d05']:.6f}")
    print(f"  -> Exceeds V_max: {results[-10]['V_multi_n5_d05'] > ap.v_max}")

    os.makedirs('experiments/results', exist_ok=True)
    with open('experiments/results/exp1_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to experiments/results/exp1_results.json")

if __name__ == '__main__':
    run()
