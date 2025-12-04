#!/bin/bash

# Master test runner - runs all test suites

set -e

echo "========================================"
echo "Salesforce Docker Images - Test Suite"
echo "========================================"
echo ""

# Make test scripts executable
chmod +x tests/test-sf-devcontainer.sh
chmod +x tests/test-sf-ci.sh

# Run sf-devcontainer tests
echo "Running sf-devcontainer tests..."
./tests/test-sf-devcontainer.sh
echo ""

# Run sf-ci tests
echo "Running sf-ci tests..."
./tests/test-sf-ci.sh
echo ""

echo "========================================"
echo "All test suites completed successfully!"
echo "========================================"
