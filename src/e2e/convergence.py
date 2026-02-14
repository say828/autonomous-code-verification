"""Convergence analysis — measures Banach contraction properties."""

import numpy as np
from typing import List, Optional


def measure_contraction_rate(trajectory: List[float]) -> float:
    """Estimate contraction rate from quality trajectory.

    c = median(gap[k+1] / gap[k]) for consecutive rounds.
    """
    rates = []
    for i in range(1, len(trajectory)):
        gap_before = 1.0 - trajectory[i - 1]
        gap_after = 1.0 - trajectory[i]
        if gap_before > 1e-10:
            rates.append(gap_after / gap_before)

    if not rates:
        return 1.0
    return float(np.median(rates))


def is_contractive(trajectory: List[float], threshold: float = 1.0) -> bool:
    """Check if the trajectory shows contractive behavior (c < threshold)."""
    c = measure_contraction_rate(trajectory)
    return c < threshold


def predicted_convergence_steps(c: float, current_gap: float,
                                 tolerance: float = 0.01) -> int:
    """Predict steps to convergence given contraction rate.

    gap(k) = c^k * gap(0)
    c^k * gap(0) < tolerance
    k > log(tolerance/gap(0)) / log(c)
    """
    if c <= 0 or c >= 1:
        return -1 if c >= 1 else 1
    if current_gap <= tolerance:
        return 0
    return int(np.ceil(np.log(tolerance / current_gap) / np.log(c)))


def fit_exponential_convergence(trajectory: List[float]) -> dict:
    """Fit Q(k) = Q* - (Q* - Q0) * c^k to trajectory."""
    if len(trajectory) < 3:
        return {'Q_star': trajectory[-1] if trajectory else 0.0, 'c': 1.0, 'R2': 0.0}

    k = np.arange(len(trajectory))
    Q = np.array(trajectory)
    Q_star = max(Q[-1], Q.max())

    gaps = Q_star - Q
    gaps = np.maximum(gaps, 1e-15)

    # Linear fit in log space: log(gap) = log(gap0) + k*log(c)
    valid = gaps > 1e-10
    if valid.sum() < 2:
        return {'Q_star': Q_star, 'c': 0.0, 'R2': 1.0}

    log_gaps = np.log(gaps[valid])
    k_valid = k[valid]

    if len(k_valid) >= 2:
        coeffs = np.polyfit(k_valid, log_gaps, 1)
        c = np.exp(coeffs[0])

        # R-squared
        predicted = coeffs[0] * k_valid + coeffs[1]
        ss_res = ((log_gaps - predicted) ** 2).sum()
        ss_tot = ((log_gaps - log_gaps.mean()) ** 2).sum()
        R2 = 1.0 - ss_res / max(ss_tot, 1e-15)
    else:
        c = 0.5
        R2 = 0.0

    return {'Q_star': Q_star, 'c': float(c), 'R2': float(R2)}
