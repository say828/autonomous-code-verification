"""Multi-agent verification model — V_multi overcomes V_max ceiling.

Core theorems:
  T1. Verification Crossover: exists E_ai* where V_agent > V_human
  T2. Iterative Convergence: C(k) -> mu_R * V_eff_ceiling
  T3. Multi-Agent Amplification: diverse agents overcome V_max
  T4. Safe Autonomy: P(failure) < epsilon achievable
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentVerificationParams:
    v_a0: float = 0.15       # baseline agent verification accuracy
    v_max: float = 0.85      # structural ceiling (blind spots)
    alpha: float = 3.0       # capability scaling exponent


@dataclass
class MultiAgentParams:
    n_agents: int = 3
    diversity: float = 0.3   # 0=identical, 1=fully independent


@dataclass
class RequirementParams:
    n_requirements: int = 20
    mu_R: float = 0.95       # requirement specification completeness


def V_agent(E_ai: float, params: AgentVerificationParams = None) -> float:
    """Agent verification: improves as AI improves, saturates at V_max.

    V_a = v_a0 + (V_max - v_a0) * (1 - E_ai)^alpha
    """
    if params is None:
        params = AgentVerificationParams()
    return params.v_a0 + (params.v_max - params.v_a0) * (1.0 - E_ai) ** params.alpha


def V_multi_agent(V_single: float, n_agents: int, diversity: float) -> float:
    """Multi-agent verification with diversity.

    n_eff = 1 + (n-1) * diversity
    V_multi = 1 - (1-V_single)^n_eff
    """
    n_eff = 1.0 + (n_agents - 1.0) * diversity
    return 1.0 - (1.0 - V_single) ** n_eff


def compliance_after_k_rounds(V_a: float, k: int, mu_R: float = 1.0) -> float:
    """Requirement compliance after k verification rounds.

    C(k) = mu_R * [1 - (1-V_a)^k]
    """
    error_remaining = (1.0 - V_a) ** k
    return mu_R * (1.0 - error_remaining)


def V_multi_agent_iterated(V_single: float, n_agents: int, diversity: float,
                            k_rounds: int, mu_R: float = 1.0) -> float:
    """Multi-agent verification over k rounds."""
    V_round = V_multi_agent(V_single, n_agents, diversity)
    return compliance_after_k_rounds(V_round, k_rounds, mu_R)


def find_crossover(E_ai_arr, V_h_arr, V_a_arr) -> Optional[float]:
    """Find E_ai where V_agent first exceeds V_human."""
    diff = V_a_arr - V_h_arr
    crossings = np.where(np.diff(np.sign(diff)))[0]
    if len(crossings) > 0:
        idx = crossings[-1]
        x1, x2 = E_ai_arr[idx], E_ai_arr[idx + 1]
        y1, y2 = diff[idx], diff[idx + 1]
        if y2 != y1:
            return x1 - y1 * (x2 - x1) / (y2 - y1)
    if (diff >= 0).all():
        return E_ai_arr[-1]
    return None


def P_failure(V_a: float, n_agents: int, diversity: float,
              k_rounds: int, mu_R: float) -> float:
    """P(failure) = 1 - C(k) for multi-agent iterated verification."""
    C = V_multi_agent_iterated(V_a, n_agents, diversity, k_rounds, mu_R)
    return 1.0 - C


def min_capability_for_safety(epsilon: float, n_agents: int, diversity: float,
                               k_rounds: int, mu_R: float) -> Optional[float]:
    """Binary search for minimum V_a such that P(failure) < epsilon."""
    target = 1.0 - epsilon
    if target >= mu_R:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        V_round = V_multi_agent(mid, n_agents, diversity)
        C = compliance_after_k_rounds(V_round, k_rounds, mu_R)
        if C >= target:
            hi = mid
        else:
            lo = mid
    return hi


def mu_R_with_agent(mu_R_base: float, V_a: float,
                     n_iterations: int = 3, discovery_rate: float = 0.5) -> float:
    """Agent-augmented requirement completeness via iterative discovery."""
    mu_R = mu_R_base
    for _ in range(n_iterations):
        gap = 1.0 - mu_R
        discovered = V_a * discovery_rate * gap
        mu_R = mu_R + discovered
    return min(mu_R, 1.0)


def effective_n(n_agents: int, diversity: float) -> float:
    """Effective number of independent agents."""
    return 1.0 + (n_agents - 1.0) * diversity
