---
name: fix-loop
description: Run self-correction loop until tests pass
user_invocable: true
---

/fix-loop [test_path]

Executes the E2E self-correction loop:
1. Run tests
2. Analyze failures
3. Propose fix
4. Apply fix
5. Re-test
6. Repeat until convergence or max rounds

Reports convergence trajectory and contraction rate.
