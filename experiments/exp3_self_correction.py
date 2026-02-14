"""Experiment 3: Self-Correction Loop Convergence (T6)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import json
from models.multi_agent import V_agent, V_multi_agent, AgentVerificationParams, MultiAgentParams
from models.convergence import system_quality_trajectory, contraction_rate, steps_to_convergence

def run():
    ap = AgentVerificationParams()
    mp = MultiAgentParams(n_agents=5, diversity=0.5)

    results = []
    for E_ai in [0.15, 0.10, 0.05, 0.02, 0.01]:
        V_a = V_agent(E_ai, ap)
        V_m = V_multi_agent(V_a, mp.n_agents, mp.diversity)
        traj = system_quality_trajectory(0.5, V_m, r_improve=0.5, n_steps=30)
        c = contraction_rate(V_m)
        k_conv = steps_to_convergence(V_m)

        results.append({
            'E_ai': E_ai, 'V_agent': float(V_a), 'V_multi': float(V_m),
            'contraction_rate': float(c), 'steps_to_converge': int(k_conv),
            'trajectory': traj.tolist(),
        })

        print(f"E_ai={E_ai:.2f}: V_multi={V_m:.4f}, c={c:.4f}, converge in {k_conv} steps")

    os.makedirs('experiments/results', exist_ok=True)
    with open('experiments/results/exp3_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved.")

if __name__ == '__main__':
    run()
