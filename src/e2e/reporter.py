"""Reporter — generates human-readable reports from fix loop results."""

from .fix_loop import FixLoopResult
from .convergence import measure_contraction_rate, fit_exponential_convergence


def generate_report(result: FixLoopResult) -> str:
    """Generate text report from fix loop result."""
    lines = ["=" * 60]
    lines.append("Fix Loop Report")
    lines.append("=" * 60)

    lines.append(f"Total rounds: {result.total_rounds}")
    lines.append(f"Converged: {result.converged}")
    lines.append(f"Final pass rate: {result.final_pass_rate:.1%}")

    trajectory = result.convergence_trajectory
    if len(trajectory) > 1:
        c = measure_contraction_rate(trajectory)
        lines.append(f"Contraction rate: {c:.4f}")
        lines.append(f"Is contractive: {c < 1.0}")

    lines.append("")
    lines.append("Round-by-round:")
    for attempt in result.attempts:
        tr = attempt.test_result
        lines.append(
            f"  Round {attempt.round}: {tr.n_passed}/{len(tr.results)} passed "
            f"({tr.pass_rate:.1%}) — {attempt.fix_description}"
        )

    if trajectory:
        fit = fit_exponential_convergence(trajectory)
        lines.append(f"\nExponential fit: Q* = {fit['Q_star']:.4f}, "
                     f"c = {fit['c']:.4f}, R² = {fit['R2']:.4f}")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_json_report(result: FixLoopResult) -> dict:
    """Generate structured JSON report."""
    trajectory = result.convergence_trajectory
    fit = fit_exponential_convergence(trajectory) if trajectory else {}

    return {
        'converged': result.converged,
        'total_rounds': result.total_rounds,
        'final_pass_rate': result.final_pass_rate,
        'trajectory': trajectory,
        'contraction_rates': result.contraction_rates,
        'exponential_fit': fit,
        'rounds': [
            {
                'round': a.round,
                'pass_rate': a.test_result.pass_rate,
                'n_passed': a.test_result.n_passed,
                'n_failed': a.test_result.n_failed,
                'fix': a.fix_description,
            }
            for a in result.attempts
        ],
    }
