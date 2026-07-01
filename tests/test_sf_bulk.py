"""
Pytest-testinfra tests for sf-bulk Docker image.
Run with: pytest tests/test_sf_bulk.py
"""

import pytest
import subprocess
import testinfra
from pathlib import Path


@pytest.fixture(scope="module")
def host():
    """Build the Docker image, start a container, and return a testinfra host."""
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["docker", "image", "inspect", "sf-bulk:test"],
        capture_output=True
    )
    if result.returncode != 0:
        print("\nBuilding sf-bulk image...")
        subprocess.run(
            ["docker", "build", "--no-cache", "-t", "sf-bulk:test", "./sf-bulk"],
            check=True,
            cwd=repo_root
        )
    else:
        print("\nUsing existing sf-bulk:test image")

    container_name = "sf-bulk-test"
    subprocess.run(
        ["docker", "run", "-d", "--name", container_name, "--rm", "sf-bulk:test", "sleep", "infinity"],
        check=True
    )

    try:
        yield testinfra.get_host(f"docker://{container_name}")
    finally:
        subprocess.run(["docker", "stop", container_name], check=False)


def test_container_os(host):
    """Alpine-based image."""
    result = host.run("cat /etc/os-release")
    assert result.rc == 0
    assert "Alpine" in result.stdout


def test_ci_user_exists(host):
    """ci user exists with UID 1000."""
    user = host.user("ci")
    assert user.exists
    assert user.uid == 1000
    assert user.shell == "/bin/bash"


def test_nodejs_installed(host):
    """Node.js 20.x is installed."""
    node = host.run("node --version")
    assert node.rc == 0
    assert node.stdout.startswith("v20.")


def test_salesforce_cli_installed(host):
    """SF CLI 2.x is installed."""
    sf = host.run("sf version")
    assert sf.rc == 0
    assert "@salesforce/cli" in sf.stdout


def test_sf_git_delta_plugin_installed(host):
    """sfdx-git-delta plugin is installed."""
    plugins = host.run("sf plugins")
    assert plugins.rc == 0
    assert "sfdx-git-delta" in plugins.stdout


def test_jq_installed(host):
    """jq is installed."""
    jq = host.run("jq --version")
    assert jq.rc == 0
    assert "jq-" in jq.stdout


def test_curl_installed(host):
    """curl is installed."""
    result = host.run("curl --version")
    assert result.rc == 0


def test_git_installed(host):
    """git is installed."""
    result = host.run("git --version")
    assert result.rc == 0
    assert "git version" in result.stdout


def test_bash_installed(host):
    """bash is installed (not just sh)."""
    result = host.run("bash --version")
    assert result.rc == 0
    assert "GNU bash" in result.stdout


def test_java_not_installed(host):
    """Java is NOT installed — this image is intentionally lightweight."""
    result = host.run("java -version")
    assert result.rc != 0


def test_xdg_data_home_env(host):
    """XDG_DATA_HOME is set to /opt/sf-data."""
    result = host.run("echo $XDG_DATA_HOME")
    assert result.stdout.strip() == "/opt/sf-data"


def test_xdg_config_home_env(host):
    """XDG_CONFIG_HOME is set to /opt/sf-config."""
    result = host.run("echo $XDG_CONFIG_HOME")
    assert result.stdout.strip() == "/opt/sf-config"


def test_xdg_dirs_exist_and_writable(host):
    """XDG dirs exist and are world-writable (chmod 777)."""
    for path in ["/opt/sf-data", "/opt/sf-config"]:
        d = host.file(path)
        assert d.exists
        assert d.is_directory
        assert d.mode == 0o777


def test_sf_environment_variables(host):
    """SF CLI container-mode env vars are set."""
    env_vars = {
        "SFDX_CONTAINER_MODE":   "true",
        "SFDX_DISABLE_DNS_CHECK": "true",
        "SF_AUTOUPDATE_DISABLE":  "true",
        "SF_DISABLE_TELEMETRY":   "true",
        "CI":                    "true",
    }
    for var, expected in env_vars.items():
        result = host.run(f"printenv {var}")
        assert result.stdout.strip() == expected, f"{var} mismatch"


def test_workspace_directory_exists(host):
    """/workspace directory exists."""
    workspace = host.file("/workspace")
    assert workspace.exists
    assert workspace.is_directory


def test_runtime_user_is_root(host):
    """Container runs as root at runtime (bypasses ARC dind UID mismatch)."""
    result = host.run("id -u")
    assert result.stdout.strip() == "0"


def test_libc6_compat_installed(host):
    """gcompat (libc6-compat) is installed for glibc compatibility with native npm modules."""
    result = host.run("apk info gcompat")
    assert result.rc == 0


def test_no_java(host):
    """Confirms image is smaller by verifying Java absence."""
    result = host.run("which java")
    assert result.rc != 0


def test_image_is_smaller_than_sf_ci(host):
    """Image size should be meaningfully smaller than sf-ci (no JRE, Alpine base)."""
    result = host.run(
        "du -sb / --exclude=/proc 2>/dev/null | cut -f1"
    )
    size_bytes = int(result.stdout.strip())
    # sf-ci is ~800MB uncompressed; sf-bulk should be well under 500MB
    assert size_bytes < 500 * 1024 * 1024, f"Image too large: {size_bytes / 1024 / 1024:.0f}MB"
