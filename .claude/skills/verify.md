---
name: verify
description: Run multi-agent verification on specified code
user_invocable: true
---

/verify [file_path]

Runs the 5-strategy multi-agent verification on the specified file:
1. Correctness review
2. Security review
3. Edge case review
4. Type safety review
5. Test-based verification

Reports V_multi, diversity, and per-strategy findings.
