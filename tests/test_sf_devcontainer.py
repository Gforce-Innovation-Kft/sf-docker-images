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
    # Build the image only if not already present (CI pre-builds it)
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["docker", "image", "inspect", "sf-devcontainer:test"],
        capture_output=True
    )
    if result.returncode != 0:
        print("\nBuilding sf-devcontainer image...")
        subprocess.run(
            ["docker", "build", "-t", "sf-devcontainer:test", "./sf-devcontainer"],
            check=True,
            cwd=repo_root
        )
    else:
        print("\nUsing existing sf-devcontainer:test image")
    
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
    """Test that the container is running Ubuntu 24.04"""
    assert host.system_info.distribution == "ubuntu"
    assert host.system_info.release.startswith("24.")


def test_default_ubuntu_user_removed(host):
    """Test that noble's default ubuntu user (UID 1000) was replaced by vscode"""
    assert not host.user("ubuntu").exists


def test_vscode_user_exists(host):
    """Test that vscode user exists with correct UID"""
    user = host.user("vscode")
    assert user.exists
    assert user.uid == 1000
    assert user.shell == "/bin/zsh"


def test_nodejs_installed(host):
    """Test that Node.js 24.x is installed"""
    node = host.run("node --version")
    assert node.rc == 0
    assert node.stdout.startswith("v24.")


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
        "SF_AUTOUPDATE_DISABLE": "true",
        "SF_DISABLE_TELEMETRY": "true"
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


def test_modern_cli_tools_installed(host):
    """Test that the baked-in CLI productivity tools are installed"""
    for tool in ["fzf", "zoxide", "eza", "delta", "lazygit", "gh", "rg"]:
        result = host.run(f"{tool} --version")
        assert result.rc == 0, f"{tool} is missing or broken"


def test_bat_and_fd_symlinks(host):
    """Test that bat/fd resolve despite Ubuntu's batcat/fdfind naming"""
    for tool in ["bat", "fd"]:
        result = host.run(f"{tool} --version")
        assert result.rc == 0, f"{tool} symlink is missing or broken"


def test_npm_global_dev_tools(host):
    """Test that prettier (+ apex plugin) and eslint are installed globally"""
    assert host.run("prettier --version").rc == 0
    assert host.run("eslint --version").rc == 0
    plugin = host.run("npm ls -g prettier-plugin-apex")
    assert plugin.rc == 0


def test_git_delta_is_system_pager(host):
    """Test that delta is configured as the system-wide git pager"""
    pager = host.run("git config --system core.pager")
    assert pager.stdout.strip() == "delta"


def test_zshrc_personalization(host):
    """Test that .zshrc wires up fzf/zoxide, SF aliases, and the per-dev overlay hook"""
    zshrc = host.file("/home/vscode/.zshrc").content_string
    for token in ["fzf --zsh", "zoxide", "alias sfl=", "sfhelp", ".zshrc.local"]:
        assert token in zshrc, f"expected '{token}' in .zshrc"
