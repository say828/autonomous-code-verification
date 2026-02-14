---
name: benchmark
description: Run verification benchmark on corpus
user_invocable: true
---

/benchmark [--strategies all|correctness|testing] [--corpus python]

Runs the verification benchmark:
1. Load bug corpus (30 Python functions)
2. Run specified strategies on each function
3. Compute detection rates, diversity, V_multi
4. Generate summary report with deployment analysis
