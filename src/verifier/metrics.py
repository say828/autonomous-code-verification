"""Verification metrics -- TPR, FPR, accuracy, F1."""

import numpy as np
from typing import List


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute standard binary classification metrics.

    Args:
        y_true: Ground truth (1=buggy, 0=clean)
        y_pred: Predictions (1=flagged as buggy, 0=flagged as clean)
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    tp = ((y_true == 1) & (y_pred == 1)).sum()
    tn = ((y_true == 0) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    fn = ((y_true == 1) & (y_pred == 0)).sum()

    tpr = tp / max(tp + fn, 1)  # sensitivity / recall
    tnr = tn / max(tn + fp, 1)  # specificity
    fpr = fp / max(fp + tn, 1)  # false positive rate
    fnr = fn / max(fn + tp, 1)  # false negative rate
    precision = tp / max(tp + fp, 1)
    accuracy = (tp + tn) / max(tp + tn + fp + fn, 1)
    f1 = 2 * precision * tpr / max(precision + tpr, 1e-10)

    return {
        'tp': int(tp), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn),
        'tpr': float(tpr), 'tnr': float(tnr),
        'fpr': float(fpr), 'fnr': float(fnr),
        'precision': float(precision),
        'accuracy': float(accuracy),
        'f1': float(f1),
    }


def confidence_interval(p: float, n: int, z: float = 1.96) -> tuple:
    """Wilson score confidence interval for proportion."""
    if n == 0:
        return (0.0, 1.0)
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    return (max(0.0, center - margin), min(1.0, center + margin))


def per_strategy_metrics(results_matrix: np.ndarray,
                          strategy_names: List[str]) -> dict:
    """Compute per-strategy detection rates."""
    metrics = {}
    for i, name in enumerate(strategy_names):
        detected = results_matrix[:, i].sum()
        total = results_matrix.shape[0]
        rate = detected / max(total, 1)
        ci_lo, ci_hi = confidence_interval(rate, total)
        metrics[name] = {
            'detected': int(detected),
            'total': int(total),
            'rate': float(rate),
            'ci_lower': float(ci_lo),
            'ci_upper': float(ci_hi),
        }
    return metrics
