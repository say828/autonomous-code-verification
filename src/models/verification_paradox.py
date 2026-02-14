"""Verification Paradox models — H* -> 0 as E_ai -> 0.

Implements the core theoretical result: as AI error rate decreases,
optimal human verification effort approaches zero.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class VerificationParams:
    V_max: float = 10.0      # max verification speed
    A: float = 1.0           # AI involvement
    lambda_param: float = 0.3 # human bottleneck coefficient
    E_ai: float = 0.35       # base AI error rate
    delta: float = 5.0       # human correction capability


@dataclass
class HumanVerifierParams:
    delta_h0: float = 5.0    # baseline detection capability
    lambda_h: float = 0.3    # review friction
    mu: float = 0.15         # vigilance decay rate (per hour)


def verification_speed(A: float, H: float, V_max: float = 10.0,
                       lambda_param: float = 0.3) -> float:
    """S = (V_max * A) / (1 + lambda * H)"""
    return (V_max * A) / (1 + lambda_param * H)


def verification_accuracy(A: float, H: float, E_ai: float = 0.35,
                          delta: float = 5.0) -> float:
    """Acc = 1 - (E_ai * e^(-delta * H))"""
    return 1 - (E_ai * np.exp(-delta * H))


def verification_efficiency(A: float, H: float, V_max: float = 10.0,
                            lambda_param: float = 0.3, E_ai: float = 0.35,
                            delta: float = 5.0) -> float:
    """E = S * Acc"""
    S = verification_speed(A, H, V_max, lambda_param)
    Acc = verification_accuracy(A, H, E_ai, delta)
    return S * Acc


def optimal_human_effort(E_ai: float, delta: float = 5.0,
                         lambda_param: float = 0.3) -> float:
    """Compute H* — optimal human verification effort.

    H* = (1/delta) * ln(delta*E_ai/lambda) when delta*E_ai > lambda, else 0.
    """
    ratio = delta * E_ai / lambda_param
    if ratio <= 1.0:
        return 0.0
    return np.log(ratio) / delta


def human_verification_effectiveness(E_ai: float,
                                      params: HumanVerifierParams = None) -> float:
    """V_human using Michaelis-Menten + vigilance decay.

    detection = delta_h*E_ai / (delta_h*E_ai + lambda_h)
    vigilance = exp(-mu*(1 + 3*(1-E_ai)^2))
    V_human = detection * vigilance
    """
    if params is None:
        params = HumanVerifierParams()
    detection = params.delta_h0 * E_ai / (params.delta_h0 * E_ai + params.lambda_h)
    rarity_penalty = (1.0 - E_ai) ** 2
    vigilance = np.exp(-params.mu * (1.0 + 3.0 * rarity_penalty))
    return detection * vigilance


def vigilance_decrement(t: float, delta_0: float = 4.0,
                        mu: float = 0.2) -> float:
    """delta(t) = delta_0 * e^(-mu*t) — human capability decay over time."""
    return delta_0 * np.exp(-mu * t)


def vigilance_multi_regime(t, delta_0: float = 4.0, kappa: float = 6.0,
                           mu: float = 0.2):
    """Multi-regime: ramp-up then decay."""
    t = np.asarray(t, dtype=float)
    t_ramp = 3.0 / kappa
    delta_peak = delta_0 * (1 - np.exp(-kappa * t_ramp))
    return np.where(
        t < t_ramp,
        delta_0 * (1 - np.exp(-kappa * t)),
        delta_peak * np.exp(-mu * (t - t_ramp))
    )


def paradox_threshold(delta: float = 5.0, lambda_param: float = 0.3) -> float:
    """E_ai* below which H* = 0 (oversight is worthless)."""
    return lambda_param / (delta + lambda_param)


def complexity_crossover_efficiency(A: float, H: float, C: float,
                                     alpha: float = 5, beta: float = 3,
                                     Acc_ai: float = 0.85,
                                     Acc_human: float = 0.95) -> float:
    """Complexity-dependent efficiency — Model 2."""
    speed = alpha * (A / np.exp(C)) + beta * H * (1 - C)
    numerator = (1 - C) * A * Acc_ai + C * H * Acc_human
    denominator = max(A + H, 1e-10)
    accuracy = numerator / denominator
    return speed * accuracy
