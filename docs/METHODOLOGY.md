# Methodology

## Theoretical Foundation

### The Verification Paradox
As AI error rate E_ai -> 0, optimal human oversight H* -> 0.
This is a structural result, not a parameter artifact.

### Multi-Agent Diversity
V_multi = 1 - (1-V_single)^n_eff overcomes V_max ceiling.
Different strategies have different blind spots -> complementary coverage.

### Self-Correction Convergence (Banach)
Quality trajectory Q(k+1) = Q(k) + V_multi * r * (1-Q(k))
Contraction rate c = 1 - V_multi * r < 1 guarantees convergence.

## Experimental Design

### Exp 1: Single vs Multi-Agent
Compare V_single, V_multi(n=3), V_multi(n=5) across E_ai range.

### Exp 2: Diversity Scaling
Sweep (n, d) parameter space. Find minimum for V_multi > V_max.

### Exp 3: Self-Correction
Measure convergence trajectory and contraction rate.

### Exp 4: Specification Impact
Reproduce 69pp TPR gap (spec vs no-spec).

### Exp 5: Cross-Provider
Analyze diversity benefits from different LLM providers.
