"""Tests for theoretical models."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest
from models.verification_paradox import (
    verification_speed, verification_accuracy, verification_efficiency,
    optimal_human_effort, human_verification_effectiveness,
    paradox_threshold, vigilance_multi_regime,
)
from models.multi_agent import (
    V_agent, V_multi_agent, compliance_after_k_rounds,
    find_crossover, P_failure, AgentVerificationParams,
)
from models.convergence import (
    mu_R_dynamic_steady_state, system_quality_trajectory,
    contraction_rate, steps_to_convergence,
)
from models.deployment import (
    deployment_inequality, requirement_floor, deployment_summary,
)


class TestVerificationParadox:
    def test_speed_decreases_with_human(self):
        s0 = verification_speed(1.0, 0.0)
        s1 = verification_speed(1.0, 1.0)
        assert s0 > s1

    def test_accuracy_increases_with_human(self):
        a0 = verification_accuracy(1.0, 0.0)
        a1 = verification_accuracy(1.0, 1.0)
        assert a1 > a0

    def test_optimal_H_positive_when_condition_met(self):
        H = optimal_human_effort(0.35, delta=5.0, lambda_param=0.3)
        assert H > 0

    def test_optimal_H_zero_below_threshold(self):
        threshold = paradox_threshold(5.0, 0.3)
        H = optimal_human_effort(threshold * 0.5, delta=5.0, lambda_param=0.3)
        assert H == 0.0

    def test_human_verification_decreases_with_low_E_ai(self):
        V_high = human_verification_effectiveness(0.3)
        V_low = human_verification_effectiveness(0.01)
        assert V_high > V_low

    def test_vigilance_ramp_then_decay(self):
        t = np.linspace(0, 4, 100)
        v = vigilance_multi_regime(t)
        peak_idx = np.argmax(v)
        assert peak_idx > 0
        assert peak_idx < len(t) - 1


class TestMultiAgent:
    def test_V_agent_improves_with_AI(self):
        V_weak = V_agent(0.3)
        V_strong = V_agent(0.01)
        assert V_strong > V_weak

    def test_V_agent_bounded_by_Vmax(self):
        ap = AgentVerificationParams(v_max=0.85)
        V = V_agent(0.001, ap)
        assert V <= ap.v_max + 1e-6

    def test_V_multi_exceeds_single(self):
        V_s = 0.8
        V_m = V_multi_agent(V_s, 3, 0.5)
        assert V_m > V_s

    def test_V_multi_no_benefit_zero_diversity(self):
        V_s = 0.8
        V_m = V_multi_agent(V_s, 5, 0.0)
        assert abs(V_m - V_s) < 1e-6

    def test_compliance_increases_with_rounds(self):
        C1 = compliance_after_k_rounds(0.8, 1, 0.95)
        C3 = compliance_after_k_rounds(0.8, 3, 0.95)
        assert C3 > C1

    def test_compliance_bounded_by_mu_R(self):
        C = compliance_after_k_rounds(0.99, 100, 0.95)
        assert C <= 0.95 + 1e-6

    def test_crossover_exists(self):
        from models.verification_paradox import human_verification_effectiveness
        E = np.linspace(0.001, 0.5, 1000)
        V_h = np.array([human_verification_effectiveness(e) for e in E])
        V_a = np.array([V_agent(e) for e in E])
        xover = find_crossover(E, V_h, V_a)
        assert xover is not None
        assert 0 < xover < 0.5

    def test_P_failure_decreases_with_agents(self):
        P1 = P_failure(0.8, 1, 0.5, 3, 0.95)
        P5 = P_failure(0.8, 5, 0.5, 3, 0.95)
        assert P5 < P1


class TestConvergence:
    def test_steady_state_positive(self):
        ss = mu_R_dynamic_steady_state(0.8, r_d=0.5, r_c=0.05)
        assert 0 < ss < 1

    def test_quality_trajectory_increases(self):
        traj = system_quality_trajectory(0.5, 0.9, r_improve=0.5, n_steps=20)
        assert traj[-1] > traj[0]
        assert traj[-1] > 0.99

    def test_contraction_rate_valid(self):
        c = contraction_rate(0.9, 0.5)
        assert 0 < c < 1

    def test_convergence_steps_finite(self):
        k = steps_to_convergence(0.9, 0.5)
        assert k > 0
        assert k < 100


class TestDeployment:
    def test_deployment_inequality_with_strong_system(self):
        assert deployment_inequality(0.9, 5, 0.5, 3, 0.999, 0.01)

    def test_deployment_inequality_fails_with_low_mu_R(self):
        assert not deployment_inequality(0.9, 5, 0.5, 3, 0.5, 0.01)

    def test_requirement_floor(self):
        assert requirement_floor(0.95) == pytest.approx(0.05)

    def test_deployment_summary_keys(self):
        s = deployment_summary(0.8, 5, 0.5, 3, 0.95)
        assert 'V_multi' in s
        assert 'P_failure' in s
        assert 'compliance' in s
