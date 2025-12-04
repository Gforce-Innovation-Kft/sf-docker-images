#!/bin/bash

# Test script for sf-ci Docker image
# This script validates that all required CI/CD tools are installed and working

set -e

echo "======================================"
echo "Testing sf-ci Docker image"
echo "======================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run tests
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

# Build the image
echo "Building sf-ci image..."
docker build -t sf-ci:test ./sf-ci
echo ""

# Test 1: Container starts successfully
echo "Test 1: Container starts successfully"
run_test "Container startup" "docker run --rm sf-ci:test echo 'OK'"
echo ""

# Test 2: Node.js is installed
echo "Test 2: Node.js installation"
run_test "Node.js version" "docker run --rm sf-ci:test node --version"
run_test "NPM version" "docker run --rm sf-ci:test npm --version"
echo ""

# Test 3: Java is installed
echo "Test 3: Java installation"
run_test "Java version" "docker run --rm sf-ci:test java -version"
echo ""

# Test 4: Salesforce CLI is installed
echo "Test 4: Salesforce CLI installation"
run_test "SF CLI version" "docker run --rm sf-ci:test sf version"
run_test "SF CLI help" "docker run --rm sf-ci:test sf --help"
echo ""

# Test 5: Essential SF CLI plugin is installed
echo "Test 5: SF CLI plugins"
run_test "sfdx-git-delta plugin" "docker run --rm sf-ci:test sf plugins | grep -q 'sfdx-git-delta'"
echo ""

# Test 6: CI utilities are installed
echo "Test 6: CI utility tools"
run_test "jq" "docker run --rm sf-ci:test jq --version"
run_test "xmlstarlet" "docker run --rm sf-ci:test xmlstarlet --version"
run_test "git" "docker run --rm sf-ci:test git --version"
echo ""

# Test 7: User and permissions
echo "Test 7: User configuration"
run_test "ci user exists" "docker run --rm sf-ci:test id ci"
run_test "ci home directory" "docker run --rm sf-ci:test test -d /home/ci"
echo ""

# Test 8: CI Environment variables
echo "Test 8: CI environment variables"
run_test "SFDX_CONTAINER_MODE" "docker run --rm sf-ci:test bash -c '[[ \$SFDX_CONTAINER_MODE == \"true\" ]]'"
run_test "SF_AUTOUPDATE_DISABLE" "docker run --rm sf-ci:test bash -c '[[ \$SF_AUTOUPDATE_DISABLE == \"true\" ]]'"
run_test "SF_DISABLE_TELEMETRY" "docker run --rm sf-ci:test bash -c '[[ \$SF_DISABLE_TELEMETRY == \"true\" ]]'"
run_test "CI" "docker run --rm sf-ci:test bash -c '[[ \$CI == \"true\" ]]'"
echo ""

# Test 9: Workspace directory
echo "Test 9: Workspace"
run_test "Workspace directory" "docker run --rm sf-ci:test test -d /workspace"
echo ""

# Test 10: Image size check (should be smaller than devcontainer)
echo "Test 10: Image size"
CI_SIZE=$(docker image inspect sf-ci:test --format='{{.Size}}')
echo "Image size: $(numfmt --to=iec-i --suffix=B $CI_SIZE)"
run_test "Image size reasonable" "test $CI_SIZE -lt 2000000000"  # Less than 2GB
echo ""

# Summary
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
