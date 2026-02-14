"""Experiment 2: Diversity Scaling -- how n and d affect V_multi."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import json
from models.multi_agent import V_agent, V_multi_agent, AgentVerificationParams

def run():
    ap = AgentVerificationParams()
    V_a = V_agent(0.05, ap)

    results = []
    for n in range(1, 11):
        for d in np.linspace(0.0, 1.0, 21):
            V_m = V_multi_agent(V_a, n, d)
            n_eff = 1.0 + (n - 1) * d
            results.append({
                'n': n, 'd': round(float(d), 2),
                'V_multi': float(V_m), 'n_eff': float(n_eff),
                'exceeds_vmax': bool(V_m > ap.v_max),
            })

    print(f"V_single at E_ai=0.05: {V_a:.4f}")
    print(f"V_max: {ap.v_max}")
    print(f"\nMinimum (n, d) to exceed V_max:")
    for r in results:
        if r['exceeds_vmax'] and r['n'] <= 5:
            print(f"  n={r['n']}, d={r['d']}: V_multi={r['V_multi']:.6f}")
            break

    os.makedirs('experiments/results', exist_ok=True)
    with open('experiments/results/exp2_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved.")

if __name__ == '__main__':
    run()
