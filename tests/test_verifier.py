"""Tests for the verification engine."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest
from verifier.strategy import VerificationResult
from verifier.aggregator import majority_vote, union_vote, compute_V_multi
from verifier.diversity import compute_diversity, effective_agents
from verifier.metrics import compute_metrics, confidence_interval


class TestAggregator:
    def test_majority_vote_bug(self):
        results = [
            VerificationResult("s1", True, 0.9, "bug found"),
            VerificationResult("s2", True, 0.8, "bug found"),
            VerificationResult("s3", False, 0.3, "looks ok"),
        ]
        agg = majority_vote(results)
        assert agg['has_bug'] is True
        assert agg['n_detected'] == 2

    def test_majority_vote_clean(self):
        results = [
            VerificationResult("s1", False, 0.2, "ok"),
            VerificationResult("s2", False, 0.1, "ok"),
            VerificationResult("s3", True, 0.6, "maybe"),
        ]
        agg = majority_vote(results)
        assert agg['has_bug'] is False

    def test_union_vote(self):
        results = [
            VerificationResult("s1", False, 0.1, "ok"),
            VerificationResult("s2", True, 0.9, "bug!"),
            VerificationResult("s3", False, 0.1, "ok"),
        ]
        agg = union_vote(results)
        assert agg['has_bug'] is True

    def test_V_multi_computation(self):
        matrix = np.array([
            [1, 0, 1],
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0],
        ])
        V = compute_V_multi(matrix)
        assert V == 0.75


class TestDiversity:
    def test_identical_strategies(self):
        matrix = np.array([[1, 1], [0, 0], [1, 1], [0, 0]])
        d = compute_diversity(matrix)
        assert d < 0.1

    def test_independent_strategies(self):
        np.random.seed(42)
        s1 = np.random.binomial(1, 0.5, 100)
        s2 = np.random.binomial(1, 0.5, 100)
        matrix = np.column_stack([s1, s2])
        d = compute_diversity(matrix)
        assert d > 0.5

    def test_effective_agents(self):
        assert effective_agents(5, 0.0) == 1.0
        assert effective_agents(5, 1.0) == 5.0
        assert effective_agents(5, 0.5) == 3.0


class TestMetrics:
    def test_perfect_classification(self):
        m = compute_metrics([1, 1, 0, 0], [1, 1, 0, 0])
        assert m['accuracy'] == 1.0
        assert m['tpr'] == 1.0
        assert m['tnr'] == 1.0

    def test_all_positive(self):
        m = compute_metrics([1, 1, 0, 0], [1, 1, 1, 1])
        assert m['tpr'] == 1.0
        assert m['fpr'] == 1.0

    def test_confidence_interval(self):
        lo, hi = confidence_interval(0.9, 100)
        assert lo < 0.9
        assert hi > 0.9
        assert hi <= 1.0
