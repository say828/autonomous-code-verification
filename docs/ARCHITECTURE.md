# Architecture

## System Overview

```
+-----------------------------------------------------------+
|                    Verification Engine                      |
|  +----------+ +----------+ +----------+ +----------+      |
|  |Correctness| | Security | |Edge Cases| | Testing  |      |
|  +-----+----+ +-----+----+ +-----+----+ +-----+----+      |
|        +------+------+------+------+------+----+           |
|               |  Aggregator (V_multi)   |                  |
|               +----------+--------------+                  |
|                          |                                 |
|  +---------------------------------------------------+    |
|  |         SDD Framework                              |    |
|  |  Spec Parser -> Compliance Checker -> Gap Discovery|    |
|  +------------------------+---------------------------+    |
|                          |                                 |
|  +---------------------------------------------------+    |
|  |         E2E Self-Correction Loop                   |    |
|  |  Test -> Verify -> Fix -> Re-test -> Converge      |    |
|  +---------------------------------------------------+    |
+-----------------------------------------------------------+
```

## Key Design Decisions

1. **Strategy Pattern for Verifiers**: Each verification dimension (correctness, security, etc.) is an independent strategy with its own LLM prompt
2. **Parallel Execution**: Strategies run in ThreadPoolExecutor for wall-clock efficiency
3. **Pluggable LLM Backend**: Strategies accept any client with a `complete(prompt)` method
4. **Theory-Practice Bridge**: src/models/ implements exact paper equations; src/verifier/ implements practical system
