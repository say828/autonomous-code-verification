"""Multi-agent verification engine -- orchestrates strategies in parallel."""

import json
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .strategy import VerificationStrategy, VerificationResult
from .aggregator import majority_vote, union_vote
from .diversity import compute_diversity
from .metrics import compute_metrics


class VerificationEngine:
    """Orchestrates multi-agent verification with diverse strategies."""

    def __init__(self, strategies: List[VerificationStrategy] = None,
                 voting_method: str = "majority",
                 voting_threshold: float = 0.5,
                 max_workers: int = 5):
        self.strategies = strategies or []
        self.voting_method = voting_method
        self.voting_threshold = voting_threshold
        self.max_workers = max_workers

    def add_strategy(self, strategy: VerificationStrategy):
        self.strategies.append(strategy)

    def verify(self, code: str, spec: str = "",
               context: str = "") -> dict:
        """Run all strategies and aggregate results."""
        results = self._run_strategies(code, spec, context)

        if self.voting_method == "union":
            aggregated = union_vote(results)
        elif self.voting_method == "unanimous":
            from .aggregator import unanimous_vote
            aggregated = unanimous_vote(results)
        else:
            aggregated = majority_vote(results, self.voting_threshold)

        return {
            'aggregated': aggregated,
            'individual_results': results,
            'n_strategies': len(self.strategies),
        }

    def _run_strategies(self, code: str, spec: str,
                        context: str) -> List[VerificationResult]:
        """Run strategies in parallel using thread pool."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(s.verify, code, spec, context): s
                for s in self.strategies
            }
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as e:
                    strategy = futures[future]
                    results.append(VerificationResult(
                        strategy_name=strategy.name,
                        has_bug=False,
                        confidence=0.0,
                        explanation=f"Strategy failed: {e}",
                    ))

        return results

    def verify_batch(self, items: List[dict]) -> List[dict]:
        """Verify a batch of code items.

        Args:
            items: List of dicts with 'code', optional 'spec' and 'context'

        Returns:
            List of verification results
        """
        return [
            self.verify(
                code=item['code'],
                spec=item.get('spec', ''),
                context=item.get('context', ''),
            )
            for item in items
        ]

    @property
    def strategy_names(self) -> List[str]:
        return [s.name for s in self.strategies]
