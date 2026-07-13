#!/usr/bin/env bash
# Authenticate the container's SF CLI to an org from $SF_AUTH_URL.
# Works identically in sf-ci, sf-bulk, and sf-devcontainer — and in CI,
# where SF_AUTH_URL comes from a pipeline secret instead of .env.
set -euo pipefail

: "${SF_AUTH_URL:?SF_AUTH_URL is not set — see examples/.env.example}"

echo "$SF_AUTH_URL" | sf org login sfdx-url --sfdx-url-stdin --alias target-org --set-default
sf org display --target-org target-org
