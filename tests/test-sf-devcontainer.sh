#!/bin/bash

# Test script for sf-devcontainer Docker image
# This script validates that all required tools are installed and working

set -e

echo "======================================"
echo "Testing sf-devcontainer Docker image"
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
echo "Building sf-devcontainer image..."
docker build -t sf-devcontainer:test ./sf-devcontainer
echo ""

# Test 1: Container starts successfully
echo "Test 1: Container starts successfully"
run_test "Container startup" "docker run --rm sf-devcontainer:test echo 'OK'"
echo ""

# Test 2: Node.js is installed
echo "Test 2: Node.js installation"
run_test "Node.js version" "docker run --rm sf-devcontainer:test node --version"
run_test "NPM version" "docker run --rm sf-devcontainer:test npm --version"
echo ""

# Test 3: Java is installed
echo "Test 3: Java installation"
run_test "Java version" "docker run --rm sf-devcontainer:test java -version"
echo ""

# Test 4: Salesforce CLI is installed
echo "Test 4: Salesforce CLI installation"
run_test "SF CLI version" "docker run --rm sf-devcontainer:test sf version"
run_test "SF CLI help" "docker run --rm sf-devcontainer:test sf --help"
echo ""

# Test 5: SF CLI plugins are installed
echo "Test 5: SF CLI plugins"
run_test "code-analyzer plugin" "docker run --rm sf-devcontainer:test sf plugins | grep -q 'code-analyzer'"
run_test "sfdx-git-delta plugin" "docker run --rm sf-devcontainer:test sf plugins | grep -q 'sfdx-git-delta'"
run_test "sfdx-browserforce-plugin" "docker run --rm sf-devcontainer:test sf plugins | grep -q 'sfdx-browserforce-plugin'"
echo ""

# Test 6: Utilities are installed
echo "Test 6: Utility tools"
run_test "jq" "docker run --rm sf-devcontainer:test jq --version"
run_test "xmlstarlet" "docker run --rm sf-devcontainer:test xmlstarlet --version"
run_test "git" "docker run --rm sf-devcontainer:test git --version"
echo ""

# Test 7: Zsh and Oh My Zsh
echo "Test 7: Shell configuration"
run_test "Zsh" "docker run --rm sf-devcontainer:test zsh --version"
run_test "Oh My Zsh" "docker run --rm sf-devcontainer:test test -d /home/vscode/.oh-my-zsh"
run_test "Powerlevel10k theme" "docker run --rm sf-devcontainer:test test -d /home/vscode/.oh-my-zsh/custom/themes/powerlevel10k"
echo ""

# Test 8: User and permissions
echo "Test 8: User configuration"
run_test "vscode user exists" "docker run --rm sf-devcontainer:test id vscode"
run_test "vscode home directory" "docker run --rm sf-devcontainer:test test -d /home/vscode"
echo ""

# Test 9: Environment variables
echo "Test 9: Environment variables"
run_test "SFDX_CONTAINER_MODE" "docker run --rm sf-devcontainer:test bash -c '[[ \$SFDX_CONTAINER_MODE == \"true\" ]]'"
run_test "SF_AUTOUPDATE_DISABLE" "docker run --rm sf-devcontainer:test bash -c '[[ \$SF_AUTOUPDATE_DISABLE == \"true\" ]]'"
echo ""

# Test 10: Workspace directory
echo "Test 10: Workspace"
run_test "Workspace directory" "docker run --rm sf-devcontainer:test test -d /workspace"
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
