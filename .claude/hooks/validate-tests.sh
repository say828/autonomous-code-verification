#!/bin/bash
# Hook: Validate that all tests pass before proceeding
cd "$(git rev-parse --show-toplevel)" || exit 1
python -m pytest tests/ -q --tb=no 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Tests are failing. Fix tests before proceeding."
    exit 1
fi
