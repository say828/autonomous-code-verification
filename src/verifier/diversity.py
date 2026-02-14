"""Diversity measurement for multi-agent verification.

Measures how different the detection patterns are across strategies.
High diversity = strategies catch different bugs = higher V_multi.
"""

import numpy as np
from typing import List
from .strategy import VerificationResult


def compute_diversity(results_matrix: np.ndarray) -> float:
    """Compute diversity coefficient from binary detection matrix.

    Args:
        results_matrix: shape (n_instances, n_strategies), 1=detected, 0=missed

    Returns:
        diversity d in [0, 1]. d=0 means identical, d=1 means fully independent.
    """
    n_instances, n_strategies = results_matrix.shape
    if n_strategies < 2 or n_instances < 2:
        return 0.0

    correlations = []
    for i in range(n_strategies):
        for j in range(i + 1, n_strategies):
            if results_matrix[:, i].std() > 0 and results_matrix[:, j].std() > 0:
                corr = np.corrcoef(results_matrix[:, i], results_matrix[:, j])[0, 1]
                correlations.append(corr)

    if not correlations:
        return 0.0

    mean_corr = np.mean(correlations)
    return max(0.0, min(1.0, 1.0 - mean_corr))


def effective_agents(n_agents: int, diversity: float) -> float:
    """n_eff = 1 + (n-1) * d"""
    return 1.0 + (n_agents - 1.0) * diversity


def compute_overlap_matrix(results_matrix: np.ndarray) -> np.ndarray:
    """Compute pairwise overlap between strategies.

    overlap[i][j] = |detected_by_i AND detected_by_j| / |detected_by_i OR detected_by_j|
    """
    n_strategies = results_matrix.shape[1]
    overlap = np.zeros((n_strategies, n_strategies))

    for i in range(n_strategies):
        for j in range(n_strategies):
            union = np.logical_or(results_matrix[:, i], results_matrix[:, j]).sum()
            if union > 0:
                intersection = np.logical_and(results_matrix[:, i], results_matrix[:, j]).sum()
                overlap[i, j] = intersection / union
            else:
                overlap[i, j] = 1.0 if i == j else 0.0

    return overlap


def strategy_independence_test(results_matrix: np.ndarray) -> dict:
    """Test whether strategy detections are independent (chi-squared test)."""
    from scipy import stats
    n_strategies = results_matrix.shape[1]
    p_values = []

    for i in range(n_strategies):
        for j in range(i + 1, n_strategies):
            contingency = np.array([
                [(results_matrix[:, i] == 1) & (results_matrix[:, j] == 1),
                 (results_matrix[:, i] == 1) & (results_matrix[:, j] == 0)],
                [(results_matrix[:, i] == 0) & (results_matrix[:, j] == 1),
                 (results_matrix[:, i] == 0) & (results_matrix[:, j] == 0)]
            ]).sum(axis=-1)

            if contingency.min() > 0:
                _, p, _, _ = stats.chi2_contingency(contingency)
                p_values.append(p)

    return {
        'p_values': p_values,
        'all_independent': all(p > 0.05 for p in p_values) if p_values else True,
        'mean_p': np.mean(p_values) if p_values else 1.0,
    }
