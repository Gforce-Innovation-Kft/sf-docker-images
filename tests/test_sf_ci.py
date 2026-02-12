"""
Pytest-testinfra tests for sf-ci Docker image
Run with: pytest tests/test_sf_ci.py
"""

import pytest
import subprocess
import testinfra
from pathlib import Path


@pytest.fixture(scope="module")
def host():
    """Build the Docker image, start a container, and return a testinfra host"""
    # Build the image only if not already present (CI pre-builds it)
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["docker", "image", "inspect", "sf-ci:test"],
        capture_output=True
    )
    if result.returncode != 0:
        print("\nBuilding sf-ci image...")
        subprocess.run(
            ["docker", "build", "-t", "sf-ci:test", "./sf-ci"],
            check=True,
            cwd=repo_root
        )
    else:
        print("\nUsing existing sf-ci:test image")
    
    # Start a container
    container_name = "sf-ci-test"
    subprocess.run(
        ["docker", "run", "-d", "--name", container_name, "--rm", "sf-ci:test", "sleep", "infinity"],
        check=True
    )
    
    # Return testinfra host
    try:
        yield testinfra.get_host(f"docker://{container_name}")
    finally:
        # Cleanup: stop the container
        subprocess.run(["docker", "stop", container_name], check=False)


def test_container_os(host):
    """Test that the container is running Ubuntu 22.04"""
    assert host.system_info.distribution == "ubuntu"
    assert host.system_info.release.startswith("22.")


def test_ci_user_exists(host):
    """Test that ci user exists with correct UID"""
    user = host.user("ci")
    assert user.exists
    assert user.uid == 1000
    assert user.shell == "/bin/bash"


def test_nodejs_installed(host):
    """Test that Node.js 20.x is installed"""
    node = host.run("node --version")
    assert node.rc == 0
    assert node.stdout.startswith("v20.")


def test_npm_installed(host):
    """Test that npm is installed"""
    npm = host.run("npm --version")
    assert npm.rc == 0
    assert npm.stdout.strip()


def test_java_installed(host):
    """Test that Java 17 is installed"""
    java = host.run("java -version")
    assert java.rc == 0
    assert "openjdk version \"17." in java.stderr or "openjdk 17." in java.stderr


def test_salesforce_cli_installed(host):
    """Test that Salesforce CLI is installed"""
    sf = host.run("sf version")
    assert sf.rc == 0
    assert "@salesforce/cli" in sf.stdout


def test_sf_git_delta_plugin_installed(host):
    """Test that sfdx-git-delta plugin is installed"""
    plugins = host.run("sf plugins")
    assert plugins.rc == 0
    assert "sfdx-git-delta" in plugins.stdout


def test_git_installed(host):
    """Test that git is installed"""
    git = host.run("git --version")
    assert git.rc == 0
    assert "git version" in git.stdout


def test_jq_installed(host):
    """Test that jq is installed"""
    jq = host.run("jq --version")
    assert jq.rc == 0
    assert "jq-" in jq.stdout


def test_xmlstarlet_installed(host):
    """Test that xmlstarlet is installed"""
    xml = host.run("xmlstarlet --version")
    assert xml.rc == 0


def test_sfdx_directories_exist(host):
    """Test that Salesforce CLI directories are created"""
    dirs = [
        "/home/ci/.sfdx",
        "/home/ci/.sf",
        "/home/ci/.config"
    ]
    for directory in dirs:
        d = host.file(directory)
        assert d.exists
        assert d.is_directory


def test_ci_environment_variables(host):
    """Test that CI environment variables are set"""
    env_vars = {
        "SFDX_CONTAINER_MODE": "true",
        "SFDX_DISABLE_DNS_CHECK": "true",
        "SF_AUTOUPDATE_DISABLE": "true",
        "SF_DISABLE_TELEMETRY": "true",
        "CI": "true"
    }
    for var, expected_value in env_vars.items():
        result = host.run(f"echo ${var}")
        assert result.stdout.strip() == expected_value


def test_workspace_directory_exists(host):
    """Test that /workspace directory exists"""
    workspace = host.file("/workspace")
    assert workspace.exists
    assert workspace.is_directory


def test_no_interactive_tools(host):
    """Test that interactive tools are not installed (lightweight image)"""
    # vim and nano should not be installed in CI image
    vim = host.run("which vim")
    assert vim.rc != 0
    
    nano = host.run("which nano")
    assert nano.rc != 0


def test_minimal_footprint(host):
    """Test that zsh and Oh My Zsh are not installed (lightweight image)"""
    zsh = host.run("which zsh")
    assert zsh.rc != 0
    
    omz = host.file("/home/ci/.oh-my-zsh")
    assert not omz.exists
