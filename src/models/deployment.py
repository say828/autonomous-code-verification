"""Deployment inequality — T4 safe autonomy conditions.

Provides minimum requirements for deploying autonomous verification:
- Minimum V_a for target P(failure)
- Minimum diversity for given agent count
- Requirement floor constraints
"""

import numpy as np
from typing import Optional
from .multi_agent import V_multi_agent, compliance_after_k_rounds


def deployment_inequality(V_s: float, n: int, d: float, k_v: int,
                          mu_R: float, epsilon: float) -> bool:
    """Check if deployment inequality P(failure) < epsilon is satisfied."""
    V_multi = V_multi_agent(V_s, n, d)
    C = compliance_after_k_rounds(V_multi, k_v, mu_R)
    return (1.0 - C) < epsilon


def min_diversity_for_safety(V_s: float, n: int, k_v: int, mu_R: float,
                              epsilon: float) -> Optional[float]:
    """Minimum diversity d such that P(failure) < epsilon."""
    if mu_R < 1.0 - epsilon:
        return None  # requirement floor violation
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if deployment_inequality(V_s, n, mid, k_v, mu_R, epsilon):
            hi = mid
        else:
            lo = mid
    return hi if deployment_inequality(V_s, n, hi, k_v, mu_R, epsilon) else None


def min_agents_for_safety(V_s: float, d: float, k_v: int, mu_R: float,
                           epsilon: float, max_n: int = 20) -> Optional[int]:
    """Minimum number of agents for target safety level."""
    for n in range(1, max_n + 1):
        if deployment_inequality(V_s, n, d, k_v, mu_R, epsilon):
            return n
    return None


def requirement_floor(mu_R: float) -> float:
    """Irreducible failure probability from specification gaps.

    Even with perfect verification, P(failure) >= 1 - mu_R.
    """
    return 1.0 - mu_R


def floor_iterations_needed(mu_R_base: float, target_mu_R: float,
                             V_a: float, p_d: float = 0.1) -> int:
    """Number of requirement discovery iterations to reach target mu_R."""
    if mu_R_base >= target_mu_R:
        return 0
    mu_R = mu_R_base
    for k in range(1, 10000):
        gap = 1.0 - mu_R
        mu_R = mu_R + V_a * p_d * gap
        if mu_R >= target_mu_R:
            return k
    return -1  # did not converge


def deployment_summary(V_s: float, n: int, d: float, k_v: int,
                        mu_R: float) -> dict:
    """Complete deployment analysis."""
    V_multi = V_multi_agent(V_s, n, d)
    C = compliance_after_k_rounds(V_multi, k_v, mu_R)
    P_fail = 1.0 - C
    n_eff = 1.0 + (n - 1.0) * d
    req_floor = requirement_floor(mu_R)
    return {
        'V_single': V_s,
        'V_multi': V_multi,
        'n_eff': n_eff,
        'compliance': C,
        'P_failure': P_fail,
        'requirement_floor': req_floor,
        'floor_binding': P_fail <= req_floor * 1.01,
    }
