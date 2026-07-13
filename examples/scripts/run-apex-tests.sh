#!/usr/bin/env bash
# Run local Apex tests against the default org (run auth-org.sh first).
# Example of a pipeline step you can test locally via the ci service:
#   docker compose run --rm ci bash scripts/run-apex-tests.sh
set -euo pipefail

sf apex run test --test-level RunLocalTests --code-coverage --result-format human --wait 30
