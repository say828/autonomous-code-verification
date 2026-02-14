"""Run verification benchmark on the bug corpus.

Usage:
    python benchmark/run_benchmark.py [--strategies all|correctness|testing] [--output results/]
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corpus.python_functions import CORPUS
from models.multi_agent import V_multi_agent


def run_offline_benchmark():
    """Run benchmark without LLM (using theoretical model predictions)."""
    results = []

    for item in CORPUS:
        difficulty_to_detection = {'easy': 0.95, 'medium': 0.85, 'hard': 0.70}
        p_detect = difficulty_to_detection.get(item['difficulty'], 0.80)

        results.append({
            'id': item['id'],
            'name': item['name'],
            'difficulty': item['difficulty'],
            'bug_type': item['bug_type'],
            'predicted_detection': p_detect,
        })

    return results


def analyze_results(results):
    """Compute summary statistics."""
    by_difficulty = {}
    by_bug_type = {}

    for r in results:
        d = r['difficulty']
        b = r['bug_type']
        p = r['predicted_detection']

        by_difficulty.setdefault(d, []).append(p)
        by_bug_type.setdefault(b, []).append(p)

    summary = {
        'total': len(results),
        'mean_detection': sum(r['predicted_detection'] for r in results) / max(len(results), 1),
        'by_difficulty': {k: sum(v)/len(v) for k, v in by_difficulty.items()},
        'by_bug_type': {k: sum(v)/len(v) for k, v in by_bug_type.items()},
    }

    V_s = summary['mean_detection']
    for n in [1, 3, 5]:
        for d in [0.3, 0.5, 0.8]:
            V_m = V_multi_agent(V_s, n, d)
            summary[f'V_multi_n{n}_d{d}'] = V_m

    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run verification benchmark")
    parser.add_argument('--output', default='experiments/results',
                       help='Output directory')
    args = parser.parse_args()

    print("Running offline benchmark...")
    results = run_offline_benchmark()
    summary = analyze_results(results)

    print(f"\nResults: {summary['total']} items")
    print(f"Mean detection rate: {summary['mean_detection']:.3f}")
    print(f"\nBy difficulty:")
    for k, v in summary['by_difficulty'].items():
        print(f"  {k}: {v:.3f}")
    print(f"\nBy bug type:")
    for k, v in summary['by_bug_type'].items():
        print(f"  {k}: {v:.3f}")

    os.makedirs(args.output, exist_ok=True)
    with open(os.path.join(args.output, 'benchmark_results.json'), 'w') as f:
        json.dump({'results': results, 'summary': summary}, f, indent=2)
    print(f"\nResults saved to {args.output}/benchmark_results.json")
