"""Result aggregation -- combines multi-agent verification results.

Implements V_multi calculation and majority voting.
"""

import numpy as np
from typing import List
from .strategy import VerificationResult


def majority_vote(results: List[VerificationResult], threshold: float = 0.5) -> dict:
    """Majority voting aggregation.

    Args:
        results: List of VerificationResult from different strategies
        threshold: Fraction needed to declare bug (default: simple majority)

    Returns:
        Aggregated result dict
    """
    n = len(results)
    if n == 0:
        return {'has_bug': False, 'confidence': 0.0, 'n_detected': 0, 'n_total': 0}

    votes_bug = sum(1 for r in results if r.has_bug)
    fraction = votes_bug / n

    confidences = [r.confidence for r in results]
    avg_confidence = np.mean(confidences)

    return {
        'has_bug': fraction >= threshold,
        'confidence': float(avg_confidence),
        'n_detected': votes_bug,
        'n_total': n,
        'fraction': fraction,
        'strategies_detecting': [r.strategy_name for r in results if r.has_bug],
        'strategies_clear': [r.strategy_name for r in results if not r.has_bug],
    }


def union_vote(results: List[VerificationResult]) -> dict:
    """Union voting -- bug if ANY strategy detects it."""
    return majority_vote(results, threshold=1.0 / max(len(results), 1))


def unanimous_vote(results: List[VerificationResult]) -> dict:
    """Unanimous voting -- bug only if ALL strategies detect it."""
    return majority_vote(results, threshold=1.0)


def weighted_vote(results: List[VerificationResult],
                  weights: dict = None) -> dict:
    """Weighted voting with strategy-specific weights."""
    if not results:
        return {'has_bug': False, 'confidence': 0.0, 'weighted_score': 0.0}

    if weights is None:
        weights = {r.strategy_name: 1.0 for r in results}

    total_weight = sum(weights.get(r.strategy_name, 1.0) for r in results)
    weighted_score = sum(
        weights.get(r.strategy_name, 1.0) * (1.0 if r.has_bug else 0.0)
        for r in results
    ) / max(total_weight, 1e-10)

    return {
        'has_bug': weighted_score > 0.5,
        'confidence': float(weighted_score),
        'weighted_score': float(weighted_score),
    }


def compute_V_multi(results_matrix: np.ndarray) -> float:
    """Compute observed V_multi from results matrix.

    V_multi = fraction of instances where AT LEAST ONE strategy detected the bug.
    """
    if results_matrix.size == 0:
        return 0.0
    any_detected = results_matrix.any(axis=1)
    return float(any_detected.mean())
