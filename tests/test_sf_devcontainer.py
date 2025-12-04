"""
Pytest-testinfra tests for sf-devcontainer Docker image
Run with: pytest tests/test_sf_devcontainer.py
"""

import pytest
import subprocess
import testinfra
from pathlib import Path


@pytest.fixture(scope="module")
def host():
    """Build the Docker image, start a container, and return a testinfra host"""
    # Build the image
    print("\nBuilding sf-devcontainer image...")
    repo_root = Path(__file__).parent.parent
    subprocess.run(
        ["docker", "build", "-t", "sf-devcontainer:test", "./sf-devcontainer"],
        check=True,
        cwd=repo_root
    )
    
    # Start a container
    container_name = "sf-devcontainer-test"
    subprocess.run(
        ["docker", "run", "-d", "--name", container_name, "--rm", "sf-devcontainer:test", "sleep", "infinity"],
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


def test_vscode_user_exists(host):
    """Test that vscode user exists with correct UID"""
    user = host.user("vscode")
    assert user.exists
    assert user.uid == 1000
    assert user.shell == "/bin/zsh"


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


def test_sf_cli_plugins_installed(host):
    """Test that required SF CLI plugins are installed"""
    plugins = host.run("sf plugins")
    assert plugins.rc == 0
    assert "code-analyzer" in plugins.stdout
    assert "sfdx-git-delta" in plugins.stdout
    assert "sfdx-browserforce-plugin" in plugins.stdout


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


def test_zsh_installed(host):
    """Test that zsh is installed"""
    zsh = host.run("zsh --version")
    assert zsh.rc == 0
    assert "zsh" in zsh.stdout


def test_oh_my_zsh_installed(host):
    """Test that Oh My Zsh is installed"""
    omz_dir = host.file("/home/vscode/.oh-my-zsh")
    assert omz_dir.exists
    assert omz_dir.is_directory


def test_powerlevel10k_theme_installed(host):
    """Test that Powerlevel10k theme is installed"""
    p10k = host.file("/home/vscode/.oh-my-zsh/custom/themes/powerlevel10k")
    assert p10k.exists
    assert p10k.is_directory


def test_zsh_plugins_installed(host):
    """Test that required Zsh plugins are installed"""
    plugins = [
        "/home/vscode/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
        "/home/vscode/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
        "/home/vscode/.oh-my-zsh/custom/plugins/zsh-completions"
    ]
    for plugin in plugins:
        assert host.file(plugin).exists


def test_zshrc_exists(host):
    """Test that .zshrc is configured"""
    zshrc = host.file("/home/vscode/.zshrc")
    assert zshrc.exists
    assert zshrc.user == "vscode"


def test_p10k_config_exists(host):
    """Test that .p10k.zsh is configured"""
    p10k_config = host.file("/home/vscode/.p10k.zsh")
    assert p10k_config.exists
    assert p10k_config.user == "vscode"


def test_sfdx_directories_exist(host):
    """Test that Salesforce CLI directories are created"""
    dirs = [
        "/home/vscode/.sfdx",
        "/home/vscode/.sf",
        "/home/vscode/.config"
    ]
    for directory in dirs:
        d = host.file(directory)
        assert d.exists
        assert d.is_directory


def test_environment_variables(host):
    """Test that required environment variables are set"""
    env_vars = {
        "SFDX_CONTAINER_MODE": "true",
        "SFDX_DISABLE_DNS_CHECK": "true",
        "SF_AUTOUPDATE_DISABLE": "true"
    }
    for var, expected_value in env_vars.items():
        result = host.run(f"echo ${var}")
        assert result.stdout.strip() == expected_value


def test_workspace_directory_exists(host):
    """Test that /workspace directory exists"""
    workspace = host.file("/workspace")
    assert workspace.exists
    assert workspace.is_directory


def test_vim_installed(host):
    """Test that vim is installed"""
    vim = host.run("vim --version")
    assert vim.rc == 0


def test_nano_installed(host):
    """Test that nano is installed"""
    nano = host.run("nano --version")
    assert nano.rc == 0


def test_sudo_available(host):
    """Test that vscode user has sudo privileges"""
    sudo_check = host.run("sudo -n true")
    assert sudo_check.rc == 0
