"""
Pytest-testinfra tests for sf-devcontainer Docker image
Run with: pytest tests/test_sf_devcontainer.py
"""

import json
import os
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


def test_openssh_client_installed(host):
    """git clone/push over ssh:// or git@ needs the ssh binary — it's not part
    of the `git` package. Without it: 'error: cannot run ssh: No such file or
    directory'. HTTPS remotes work either way; this covers SSH remotes too."""
    ssh = host.run("ssh -V")
    combined = ssh.stdout + ssh.stderr
    assert "OpenSSH" in combined, combined


def test_ssh_accepts_new_host_keys_noninteractively(host):
    """A container shell has nothing to answer the interactive 'are you sure
    you want to continue connecting (yes/no)?' prompt on the first connection
    to any new SSH host, so it would otherwise hang forever. Ubuntu's
    ssh_config Includes /etc/ssh/ssh_config.d/*.conf, so a drop-in file here
    is picked up ahead of any later Host block in the base config."""
    cfg = host.file("/etc/ssh/ssh_config.d/99-devcontainer.conf")
    assert cfg.exists
    assert "StrictHostKeyChecking accept-new" in cfg.content_string


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


def test_starship_installed(host):
    """Starship replaced Powerlevel10k as the prompt."""
    result = host.run("starship --version")
    assert result.rc == 0
    assert "starship" in result.stdout


def test_starship_config_present(host):
    """The prompt config (including the target-org module) is baked in."""
    cfg = host.file("/home/vscode/.config/starship.toml")
    assert cfg.exists
    assert cfg.user == "vscode"
    assert "sf_org" in cfg.content_string


def test_oh_my_zsh_absent(host):
    """OMZ was removed — the host migrated off it for a 22x startup win."""
    assert not host.file("/home/vscode/.oh-my-zsh").exists
    assert not host.file("/home/vscode/.p10k.zsh").exists


def test_zsh_plugins_installed(host):
    """Plugins come from apt now, not git clones under OMZ."""
    plugins = [
        "/usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh",
        "/usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh",
    ]
    for plugin in plugins:
        assert host.file(plugin).exists, f"{plugin} missing"


def test_zshrc_sources_plugins_in_order(host):
    """zsh-syntax-highlighting must be sourced last or it silently no-ops."""
    zshrc = host.file("/home/vscode/.zshrc").content_string
    autosuggest = zshrc.index("zsh-autosuggestions.zsh")
    highlight = zshrc.index("zsh-syntax-highlighting.zsh")
    assert autosuggest < highlight


def test_prompt_does_not_shell_out_to_sf(host):
    """A `sf` call in the prompt would add ~500ms of Node startup per prompt."""
    cfg = host.file("/home/vscode/.config/starship.toml").content_string
    assert "sf config" not in cfg
    assert "jq" in cfg


def test_zshrc_exists(host):
    """Test that .zshrc is configured"""
    zshrc = host.file("/home/vscode/.zshrc")
    assert zshrc.exists
    assert zshrc.user == "vscode"


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
    for token in ["fzf --zsh", "zoxide", "alias sfl=", "sfhelp", "devhelp", ".zshrc.local"]:
        assert token in zshrc, f"expected '{token}' in .zshrc"


def test_cheatsheet_baked_in(host):
    """Test that the devhelp cheatsheet is baked into the image"""
    cheatsheet = host.file("/usr/local/share/sf-devcontainer/cheatsheet.md")
    assert cheatsheet.exists
    assert "fzf" in cheatsheet.content_string


def test_zsh_starts_clean(host):
    """Test that an interactive zsh emits no Oh My Zsh plugin warnings
    (guards against plugins= entries that OMZ removed upstream, e.g. fd/ripgrep)"""
    result = host.run("zsh -ic true")
    combined = result.stdout + result.stderr
    assert "[oh-my-zsh] plugin" not in combined, combined


# ---------------------------------------------------------------------------
# Live org-auth tests
#
# Everything above uses the `host` fixture: one container, built once, kept
# running for the whole module. These tests are different on purpose — they
# start their own short-lived containers so they can exercise the thing the
# `host` fixture can't: what happens to SF CLI's encrypted org auth when the
# *container is thrown away and a new one is started against the same
# volumes* — exactly what a VS Code "Dev Containers: Rebuild" or a fresh
# `docker compose run` does.
#
# `sf org list` failing with `AuthDecryptError` on an otherwise-healthy
# container almost always means the auth JSON under ~/.sf / ~/.sfdx was
# encrypted with a key the current container can't reproduce — classically
# because those files were copied/bind-mounted in from the host (a different
# OS, a different keychain) instead of being produced by an `sf org login`
# run *inside* a container. That failure mode doesn't need real org
# credentials to guard against: test_auth_dirs_not_host_mounted below is a
# static config check for the mistake itself, and passes with no secrets in
# every CI run. The end-to-end round-trip below it needs a real (or scratch)
# org and is skipped unless SF_AUTH_URL is set — see
# examples/.env.example for how to obtain one. Run locally with:
#   SF_AUTH_URL="$(sf org display --target-org <alias> --verbose --json | jq -r .result.sfdxAuthUrl)" \
#     pytest tests/test_sf_devcontainer.py -k auth -v
# ---------------------------------------------------------------------------

requires_live_org = pytest.mark.skipif(
    not os.environ.get("SF_AUTH_URL"),
    reason="set SF_AUTH_URL to a real org's auth URL to run the live auth round-trip "
    "(see examples/.env.example) — this is a live-credential test, not part of the "
    "default suite",
)


def test_auth_dirs_not_host_mounted():
    """Guard against the most common cause of a fresh AuthDecryptError report:
    someone adding a bind mount of their *host* ~/.sf or ~/.sfdx into the
    devcontainer so they don't have to re-auth. That copies in auth JSON
    encrypted with the host OS's keychain, which the container can't read —
    hence AuthDecryptError on first `sf org list`. The supported way to get
    org auth into any of these images is `sf org login` *inside* the
    container (see examples/scripts/auth-org.sh and SF_AUTH_URL), optionally
    backed by a named Docker volume (examples/docker-compose.yml) so it
    survives a rebuild without ever touching host-encrypted files.

    SCOPE: this only scans THIS repo's config. It cannot see consumer repos,
    which is where the mistake was actually made once (sf-develop-demo, 2026-08-06)
    — so a green run here does not mean no consumer is bind-mounting host auth.
    Verified empirically on 2026-08-06: bind-mounting a macOS host's ~/.sf and
    ~/.sfdx into this image makes every org report AuthDecryptError."""
    repo_root = Path(__file__).parent.parent
    devcontainer_json = (repo_root / ".devcontainer" / "devcontainer.json").read_text()
    compose_yml = (repo_root / "examples" / "docker-compose.yml").read_text()

    for label, text in [(".devcontainer/devcontainer.json", devcontainer_json), ("examples/docker-compose.yml", compose_yml)]:
        assert "${localEnv:HOME}/.sf" not in text, f"{label} bind-mounts the host's ~/.sf — this causes AuthDecryptError"
        assert "${HOME}/.sf" not in text, f"{label} bind-mounts the host's ~/.sf — this causes AuthDecryptError"
        assert "${localEnv:HOME}/.sfdx" not in text, f"{label} bind-mounts the host's ~/.sfdx — this causes AuthDecryptError"
        assert "${HOME}/.sfdx" not in text, f"{label} bind-mounts the host's ~/.sfdx — this causes AuthDecryptError"

    # The compose recipe's own persistence story must use named volumes
    # (docker-managed storage, created fresh by/for the container) rather
    # than a host path, for exactly the same reason.
    assert "sf-config:/home/vscode/.sf" in compose_yml
    assert "sfdx-config:/home/vscode/.sfdx" in compose_yml


@requires_live_org
def test_org_auth_survives_container_recreate():
    """End-to-end regression test for AuthDecryptError: authenticate inside
    one throwaway container with org auth persisted to named Docker volumes,
    then read it back from a *second, freshly-started* container reusing
    those same volumes (no state carried over except the volumes) — the
    same shape as a VS Code Dev Containers rebuild or a repeat
    `docker compose run`. If the container's own auth flow is used (never a
    host bind mount), this must succeed with no AuthDecryptError."""
    sf_auth_url = os.environ["SF_AUTH_URL"]
    image = "sf-devcontainer:test"
    vol_sf = "pytest-auth-sf-config"
    vol_sfdx = "pytest-auth-sfdx-config"

    def run_in_fresh_container(cmd, **extra_env):
        env_args = []
        for key, value in extra_env.items():
            env_args += ["-e", f"{key}={value}"]
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                *env_args,
                "-v", f"{vol_sf}:/home/vscode/.sf",
                "-v", f"{vol_sfdx}:/home/vscode/.sfdx",
                image, "bash", "-lc", cmd,
            ],
            capture_output=True,
            text=True,
        )
        return result

    subprocess.run(["docker", "volume", "rm", "-f", vol_sf, vol_sfdx], check=False)
    try:
        login = run_in_fresh_container(
            'echo "$SF_AUTH_URL" | sf org login sfdx-url --sfdx-url-stdin '
            "--alias pytest-auth-org --set-default",
            SF_AUTH_URL=sf_auth_url,
        )
        assert login.returncode == 0, f"login failed:\n{login.stdout}\n{login.stderr}"

        # Fresh container, same volumes, no SF_AUTH_URL passed this time —
        # only what's on disk in ~/.sf / ~/.sfdx is available to decrypt.
        listing = run_in_fresh_container("sf org list --json")
        assert listing.returncode == 0, f"org list failed:\n{listing.stdout}\n{listing.stderr}"

        data = json.loads(listing.stdout)
        result = data["result"]
        orgs = result.get("nonScratchOrgs", []) + result.get("scratchOrgs", [])
        assert orgs, f"expected at least one org in `sf org list --json`, got: {data}"

        pytest_org = next((o for o in orgs if o.get("alias") == "pytest-auth-org"), None)
        assert pytest_org is not None, f"pytest-auth-org not found in: {orgs}"
        assert pytest_org.get("connectedStatus") != "AuthDecryptError", (
            f"AuthDecryptError on a container-native login+recreate — the container's own "
            f"encryption key did not survive alongside the org auth in the named volume: "
            f"{pytest_org}"
        )
    finally:
        subprocess.run(["docker", "volume", "rm", "-f", vol_sf, vol_sfdx], check=False)
