"""Analyze benchmark results and generate summary statistics.

Usage:
    python benchmark/analyze_benchmark.py experiments/results/benchmark_results.json
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.multi_agent import V_multi_agent, V_agent, AgentVerificationParams
from models.deployment import deployment_summary


def analyze(results_path: str):
    with open(results_path) as f:
        data = json.load(f)

    results = data['results']

    print("=" * 60)
    print("Benchmark Analysis")
    print("=" * 60)

    detections = [r['predicted_detection'] for r in results]
    print(f"\nDetection rate: {np.mean(detections):.3f} +/- {np.std(detections):.3f}")

    V_s = np.mean(detections)
    print(f"\nMulti-agent projections (V_single={V_s:.3f}):")
    print(f"{'n':>4} {'d':>6} {'V_multi':>8} {'P(miss)':>10}")
    for n in [1, 3, 5, 7]:
        for d in [0.3, 0.5, 0.8]:
            V_m = V_multi_agent(V_s, n, d)
            print(f"{n:4d} {d:6.2f} {V_m:8.6f} {1-V_m:10.2e}")

    print(f"\nDeployment analysis (n=5, d=0.5, k_v=3, mu_R=0.95):")
    ds = deployment_summary(V_s, n=5, d=0.5, k_v=3, mu_R=0.95)
    for k, v in ds.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'experiments/results/benchmark_results.json'
    analyze(path)
