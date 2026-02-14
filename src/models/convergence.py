"""Convergence models — T2 iterative convergence + T5 dynamic safety + T6 self-improvement.

T2: C(k) converges geometrically to mu_R
T5: mu_R maintains steady state under requirement churn
T6: System quality converges via Banach contraction
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict


def mu_R_dynamic_steady_state(V_a: float, r_d: float = 0.5,
                                r_c: float = 0.05) -> float:
    """Steady-state requirement completeness under dynamic changes.

    mu_R* = V_a*r_d / (r_c + V_a*r_d)
    """
    discovery = V_a * r_d
    if discovery + r_c == 0:
        return 0.0
    return discovery / (r_c + discovery)


def mu_R_dynamic_trajectory(mu_R_0: float, V_a: float, r_d: float = 0.5,
                             r_c: float = 0.05, n_steps: int = 100) -> np.ndarray:
    """Simulate mu_R trajectory under dynamic requirement changes."""
    trajectory = [mu_R_0]
    mu_R = mu_R_0
    for _ in range(n_steps):
        mu_R = mu_R * (1.0 - r_c) + V_a * r_d * (1.0 - mu_R)
        trajectory.append(min(mu_R, 1.0))
    return np.array(trajectory)


def max_change_rate_for_safety(V_a: float, r_d: float,
                                mu_R_min: float) -> float:
    """Maximum requirement change rate maintaining mu_R* > mu_R_min."""
    if mu_R_min >= 1.0:
        return 0.0
    return V_a * r_d * (1.0 - mu_R_min) / mu_R_min


def system_quality_trajectory(Q_0: float, V_multi: float,
                               r_improve: float = 0.5,
                               n_steps: int = 50) -> np.ndarray:
    """Quality trajectory under self-improvement (Banach contraction)."""
    trajectory = [Q_0]
    Q = Q_0
    for _ in range(n_steps):
        gap = 1.0 - Q
        improvement = V_multi * r_improve * gap
        Q = Q + improvement
        trajectory.append(min(Q, 1.0))
    return np.array(trajectory)


def contraction_rate(V_multi: float, r_improve: float = 0.5) -> float:
    """c = 1 - V_multi*r_improve. Must be < 1 for convergence."""
    return 1.0 - V_multi * r_improve


def steps_to_convergence(V_multi: float, r_improve: float = 0.5,
                          tolerance: float = 1e-6) -> int:
    """Number of steps to reach within tolerance of fixed point."""
    c = contraction_rate(V_multi, r_improve)
    if c <= 0:
        return 1
    if c >= 1:
        return float('inf')
    return int(np.ceil(np.log(tolerance) / np.log(c)))


def full_dynamic_system(E_ai: float, V_a: float, V_multi: float,
                         mu_R_0: float = 0.95, r_d: float = 0.5,
                         r_c: float = 0.05, r_improve: float = 0.5,
                         k_verify: int = 10, n_meta_steps: int = 30) -> List[Dict]:
    """Full dynamic autonomous system simulation combining T3+T5+T6."""
    from .multi_agent import compliance_after_k_rounds

    mu_R = mu_R_0
    Q = 0.5
    trajectory = []

    for step in range(n_meta_steps):
        mu_R = mu_R * (1.0 - r_c) + V_a * r_d * (1.0 - mu_R)
        mu_R = min(mu_R, 1.0)
        Q = Q + V_multi * r_improve * (1.0 - Q)
        Q = min(Q, 1.0)
        C = compliance_after_k_rounds(V_multi, k_verify, mu_R)
        P_fail = (1.0 - C) * (1.0 - Q)
        trajectory.append({
            'step': step, 'mu_R': mu_R, 'Q': Q,
            'V_multi': V_multi, 'C': C, 'P_failure': P_fail,
        })
    return trajectory
