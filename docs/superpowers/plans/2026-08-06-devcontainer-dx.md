# Devcontainer DX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Salesforce devcontainer match the host shell (Starship, no framework) and inherit the host's org authentication automatically.

**Architecture:** Two independent deliverables. In `sf-docker-images`, the `sf-devcontainer` image swaps Oh My Zsh + Powerlevel10k for Starship with directly-sourced zsh plugins and one cached `compinit`; this ships in the pending v3.0.0. In `sf-develop-demo`, the devcontainer bind-mounts the host `~/.sf` so credentials are shared, drops three dead files, and gains a post-create script that resolves the target org and fails loudly when it is not authorized.

**Tech Stack:** Docker (ubuntu:24.04), zsh, Starship, pytest-testinfra, devcontainer.json, Salesforce CLI v2.

**Spec:** [`docs/superpowers/specs/2026-08-06-devcontainer-dx-design.md`](../specs/2026-08-06-devcontainer-dx-design.md)

## Global Constraints

- **Starship is pinned:** `STARSHIP_VERSION=1.26.0`. Never `curl | sh` unpinned.
- **Plugin sources:** `zsh-autosuggestions` and `zsh-syntax-highlighting` from apt (verified present in ubuntu:24.04 as 0.7.0-1 and 0.7.1-2). `zsh-completions` is **not packaged — drop it**, do not reintroduce a git clone.
- **`zsh-syntax-highlighting` must be sourced LAST** of the plugins, or highlighting silently stops working.
- **The prompt must never call `sf`.** `sf config get target-org` pays ~500 ms of Node startup per prompt. Read `.sf/config.json` with `jq`.
- **Image runs non-root** as `vscode` (UID 1000); a `runner` account exists at UID 1001/GID 0. Never add `USER root` as a final instruction.
- **sf-devcontainer has no hard size cap** (only sf-bulk does, at 600 MB), but record before/after size rather than guessing.
- Conventional commits: `feat:` `fix:` `docs:` `test:` `chore:` `refactor:` `ci:`.
- A pre-commit hook runs yamllint on staged YAML (blocking) — max line length 120, 2-space indent.

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `sf-devcontainer/Dockerfile` | Install starship + apt zsh plugins; stop installing OMZ/p10k | 1 |
| `sf-devcontainer/.zshrc` | Rewritten: fpath → cached compinit → plugins → starship | 1 |
| `sf-devcontainer/starship.toml` | **New.** Prompt config incl. the target-org module | 1 |
| `sf-devcontainer/.p10k.zsh` | **Deleted** (89 KB) | 1 |
| `tests/test_sf_devcontainer.py` | Assert starship present, OMZ/p10k absent | 1 |
| `sf-devcontainer/README.md`, `TOOLS.md`, `cheatsheet.md` | Shell documentation | 2 |
| `CHANGELOG.md` | `[Unreleased]` entry beside the non-root one | 2 |
| `sf-develop-demo/.devcontainer/devcontainer.json` | Mounts, containerEnv, postCreateCommand | 3 |
| `sf-develop-demo/.devcontainer/post-create.sh` | **New.** Resolve + verify the target org | 3 |
| `sf-develop-demo/.devcontainer/{Dockerfile,.zshrc,.p10k.zsh}` | **Deleted** — never built, drifted to Node 20 | 3 |

---

### Task 1: Replace the shell stack in sf-devcontainer

**Files:**
- Modify: `sf-devcontainer/Dockerfile` (lines 82-87 add ARG; lines 141-150 replace)
- Rewrite: `sf-devcontainer/.zshrc`
- Create: `sf-devcontainer/starship.toml`
- Delete: `sf-devcontainer/.p10k.zsh`
- Test: `tests/test_sf_devcontainer.py:129-152`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: an image where `command -v starship` succeeds, `~/.oh-my-zsh` and `~/.p10k.zsh` do not exist, and `/home/vscode/.config/starship.toml` is present. Task 4 verifies these interactively.

- [ ] **Step 1: Write the failing tests**

Replace `tests/test_sf_devcontainer.py` lines 129-152 (the three functions
`test_oh_my_zsh_installed`, `test_powerlevel10k_theme_installed`,
`test_zsh_plugins_installed`) with:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
docker build -t sf-devcontainer:test ./sf-devcontainer
pytest tests/test_sf_devcontainer.py -v -k "starship or absent or plugins or order or shell_out"
```

Expected: FAIL — `starship --version` returns non-zero, `/home/vscode/.oh-my-zsh` exists.

- [ ] **Step 3: Add the Starship version ARG to the Dockerfile**

In `sf-devcontainer/Dockerfile`, add to the existing pinned-tools ARG block
(after `ARG LAZYGIT_VERSION=0.63.0`):

```dockerfile
ARG STARSHIP_VERSION=1.26.0
```

- [ ] **Step 4: Fetch the Starship binary in the same pinned-tools RUN**

In that same `RUN` (the one computing `RUST_ARCH`), append before its cleanup:

```dockerfile
    && curl -fsSL "https://github.com/starship/starship/releases/download/v${STARSHIP_VERSION}/starship-${RUST_ARCH}-unknown-linux-musl.tar.gz" \
    | tar -xz -C /usr/local/bin starship \
```

`RUST_ARCH` is already computed as `x86_64` / `aarch64`, which matches Starship's
asset naming exactly.

- [ ] **Step 5: Install the zsh plugins from apt**

Add `zsh-autosuggestions` and `zsh-syntax-highlighting` to the main apt install
list (alongside `zsh`, around line 47), so they land in the existing layer with
its `rm -rf /var/lib/apt/lists/*` cleanup.

- [ ] **Step 5b: Fail the build if the plugin paths are wrong**

Add immediately after the apt install layer. A silently-missing plugin would
produce a shell with no autosuggestions and no highlighting, and nothing would
report it:

```dockerfile
# Fail loudly at build time rather than shipping a shell with no plugins.
RUN test -f /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh \
    && test -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh \
    || { echo "zsh plugin paths changed — fix .zshrc and the tests" >&2; exit 1; }
```

- [ ] **Step 6: Delete the OMZ/p10k install layer**

Remove `sf-devcontainer/Dockerfile` lines 140-145 entirely — the comment
`# Install Oh My Zsh, Powerlevel10k theme, and Zsh plugins in one layer` and the
`RUN` that clones OMZ, powerlevel10k, and the three plugin repos.

- [ ] **Step 7: Replace the config COPY lines**

Replace:

```dockerfile
COPY --chown=vscode:vscode .zshrc /home/vscode/.zshrc
COPY --chown=vscode:vscode .p10k.zsh /home/vscode/.p10k.zsh
```

with:

```dockerfile
COPY --chown=vscode:vscode .zshrc /home/vscode/.zshrc
COPY --chown=vscode:vscode starship.toml /home/vscode/.config/starship.toml
```

- [ ] **Step 8: Create `sf-devcontainer/starship.toml`**

```toml
# Prompt for the Salesforce devcontainer.
#
# Mirrors the host's Starship setup so the shell feels identical inside and out.
# The sf_org module reads .sf/config.json directly with jq. Shelling out to the
# Salesforce CLI here would pay ~500ms of Node startup on EVERY prompt, which is
# exactly the latency this whole change removes — the test asserts it does not.

format = """$directory$git_branch$git_status$custom$character"""

add_newline = false

[directory]
truncation_length = 3
truncate_to_repo = true

[git_branch]
symbol = " "

[git_status]
style = "yellow"

[custom.sf_org]
description = "Salesforce target org for this project"
command = "jq -r '.\"target-org\" // empty' .sf/config.json 2>/dev/null"
when = "test -f .sf/config.json"
symbol = "☁ "
style = "cyan"
format = "[$symbol$output]($style) "

[character]
success_symbol = "[❯](green)"
error_symbol = "[❯](red)"
```

- [ ] **Step 9: Rewrite `sf-devcontainer/.zshrc`**

```zsh
# Salesforce devcontainer shell.
#
# Deliberately framework-free: Starship + directly-sourced plugins + ONE cached
# compinit, mirroring the host setup that cut startup from 1370ms to 61ms.
# Do not reintroduce Oh My Zsh — it is what this replaced.

# --- completions -----------------------------------------------------------
# Every fpath addition MUST happen before compinit.
fpath=(/usr/share/zsh/vendor-completions $fpath)

autoload -Uz compinit
_zcompdump="${HOME}/.cache/zsh/zcompdump"
mkdir -p "${_zcompdump:h}"
# Cached fast path when the dump is less than 24h old; full scan otherwise.
if [[ -n ${_zcompdump}(#qN.mh-24) ]]; then
  compinit -C -d "$_zcompdump"
else
  compinit -d "$_zcompdump"
fi
unset _zcompdump

# --- history ---------------------------------------------------------------
# Persists across container rebuilds when a volume is mounted at
# /commandhistory (see .devcontainer/devcontainer.json).
HISTSIZE=50000
SAVEHIST=50000
setopt HIST_IGNORE_ALL_DUPS HIST_REDUCE_BLANKS INC_APPEND_HISTORY
[[ -d /commandhistory && -w /commandhistory ]] && export HISTFILE=/commandhistory/.zsh_history

export EDITOR='vim'

# --- integrations ----------------------------------------------------------
command -v fzf >/dev/null && source <(fzf --zsh)      # ^R history, ^T files, alt-C dirs
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"

# --- aliases ---------------------------------------------------------------
alias ls='eza'
alias ll='eza -alF --git --group-directories-first'
alias la='eza -a'
alias l='eza -F'
alias lt='eza --tree --level=2'
alias ..='cd ..'
alias ...='cd ../..'

# Salesforce shortcuts — run `sfhelp` to list them
alias sfl='sf org list'
alias sfo='sf org open'
alias sfd='sf project deploy start'
alias sfdp='sf project deploy preview'
alias sfr='sf project retrieve start'
alias sft='sf apex run test --code-coverage --result-format human --wait 10'

function sfdelta() {
  sf sgd source delta --from "${1:-origin/main}" --to HEAD --output-dir delta-output
}

function sfhelp() {
  cat <<'EOF'
Salesforce shortcuts:
  sfl        sf org list
  sfo        sf org open
  sfd        sf project deploy start
  sfdp       sf project deploy preview
  sfr        sf project retrieve start
  sft        sf apex run test --code-coverage --result-format human --wait 10
  sfdelta    sf sgd source delta --from <ref, default origin/main> --to HEAD
EOF
}

function devhelp() {
  bat --style=plain --language=md /usr/local/share/sf-devcontainer/cheatsheet.md
}

function mkcd() {
  mkdir -p "$1" && cd "$1"
}

# --- welcome ---------------------------------------------------------------
# Static: no subprocesses, so it costs nothing at shell start.
echo ""
echo "🚀 Salesforce Development Environment"
echo "======================================"
echo "sf · node · java 17 · gh · fzf · zoxide · eza · bat · rg · fd · delta · lazygit"
echo "Run 'sfhelp' for Salesforce shortcuts, 'devhelp' for the CLI tools cheatsheet."
echo ""

# --- zsh plugins -----------------------------------------------------------
# ORDER MATTERS: zsh-syntax-highlighting must be sourced LAST, or it silently
# stops highlighting.
source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# --- prompt ----------------------------------------------------------------
eval "$(starship init zsh)"

SF_AC_ZSH_SETUP_PATH=/home/vscode/.cache/sf/autocomplete/zsh_setup && test -f $SF_AC_ZSH_SETUP_PATH && source $SF_AC_ZSH_SETUP_PATH; # sf autocomplete setup

# Per-developer overrides — layer your own aliases/tweaks without rebuilding.
# For full dotfiles, use VS Code's dotfiles.repository setting.
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
```

- [ ] **Step 10: Delete the p10k config**

```bash
git rm sf-devcontainer/.p10k.zsh
```

- [ ] **Step 11: Rebuild and run the tests**

```bash
docker build -t sf-devcontainer:test ./sf-devcontainer
pytest tests/test_sf_devcontainer.py -v
```

Expected: PASS, all tests.

- [ ] **Step 12: Record the size change**

```bash
docker image inspect sf-devcontainer:test --format '{{.Size}}' | numfmt --to=iec-i --suffix=B
```

Note the number in the commit message. Compare against
`gforceinnovation/sf-devcontainer:latest` pulled fresh.

- [ ] **Step 13: Commit**

```bash
git add sf-devcontainer/Dockerfile sf-devcontainer/.zshrc \
        sf-devcontainer/starship.toml tests/test_sf_devcontainer.py
git rm --cached sf-devcontainer/.p10k.zsh 2>/dev/null || true
git commit -m "feat!: replace Oh My Zsh and Powerlevel10k with Starship

The container shipped the exact shell setup the host migrated away from on
2026-08-02, when dropping OMZ + p10k cut startup from 1370ms to 61ms. Entering
the container meant a slower shell with a different prompt and keybindings.

Now framework-free and matching the host: Starship (pinned 1.26.0), plugins
from apt rather than git clones, and one cached compinit. zsh-completions is
not packaged for noble and is dropped rather than cloned — the two sourced
plugins plus compinit cover it.

The prompt gains a target-org module that reads .sf/config.json with jq. It
must never call \`sf config get\`: that is ~500ms of Node startup per prompt."
```

---

### Task 2: Update the image documentation

**Files:**
- Modify: `sf-devcontainer/README.md`, `sf-devcontainer/TOOLS.md`, `sf-devcontainer/cheatsheet.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: the shell built in Task 1.
- Produces: no code interface; documentation only.

- [ ] **Step 1: Find every stale shell reference**

```bash
grep -rn "oh-my-zsh\|Oh My Zsh\|[Pp]owerlevel10k\|p10k" \
  sf-devcontainer/*.md CLAUDE.md README.md AGENTS.md .claude/references/
```

- [ ] **Step 2: Rewrite each hit**

Replace descriptions of "Zsh with Oh My Zsh, Powerlevel10k theme,
zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions" with
"Zsh with Starship, zsh-autosuggestions and zsh-syntax-highlighting, no
framework". Keep every mention of fzf keybindings, zoxide, SF aliases,
`~/.zshrc.local`, and the persistent history volume — those are unchanged.

- [ ] **Step 3: Add the CHANGELOG entry**

Under the existing `## [Unreleased]` → `### Changed — BREAKING`, after the
non-root entry:

```markdown
- **sf-devcontainer's shell is now Starship with no framework**, replacing Oh My Zsh +
  Powerlevel10k. Plugins come from apt instead of git clones; `zsh-completions` is dropped
  (not packaged for noble). The prompt shows the project's Salesforce target org, read from
  `.sf/config.json` with `jq` — never by calling `sf`, which would add ~500 ms of Node
  startup to every prompt. Anyone relying on OMZ aliases or `p10k configure` must move that
  into `~/.zshrc.local`
```

- [ ] **Step 4: Verify no stale references remain**

```bash
grep -rn "oh-my-zsh\|Powerlevel10k\|p10k" sf-devcontainer/ CLAUDE.md README.md \
  .claude/ --include="*.md" | grep -v CHANGELOG
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add -A sf-devcontainer/*.md CHANGELOG.md CLAUDE.md README.md .claude/
git commit -m "docs: describe the Starship shell across the devcontainer docs"
```

---

### Task 3: sf-develop-demo devcontainer — inherit host auth

**Repo:** `~/gforce/sf-develop-demo` (not sf-docker-images)

**Files:**
- Delete: `.devcontainer/Dockerfile`, `.devcontainer/.zshrc`, `.devcontainer/.p10k.zsh`
- Modify: `.devcontainer/devcontainer.json`
- Create: `.devcontainer/post-create.sh`

**Interfaces:**
- Consumes: the published `gforceinnovation/sf-devcontainer` image.
- Produces: a container where `sf org list` shows the host's orgs and `target-org` resolves without manual login.

- [ ] **Step 1: Delete the dead files**

```bash
cd ~/gforce/sf-develop-demo
git rm .devcontainer/Dockerfile .devcontainer/.zshrc .devcontainer/.p10k.zsh
```

These are never built — `devcontainer.json` sets `"image":` — and the Dockerfile
claims Node 20 where the real image ships 24.

- [ ] **Step 2: Create `.devcontainer/post-create.sh`**

```bash
#!/usr/bin/env bash
#
# Resolve and verify this project's Salesforce org.
#
# The host's ~/.sf is bind-mounted, so credentials are inherited rather than
# created. This script cannot log you in — it can only tell you, precisely, that
# you need to, instead of leaving a shell that looks fine and silently cannot
# deploy.
set -euo pipefail

SF_DIR="${HOME}/.sf"

if [ ! -d "$SF_DIR" ]; then
  echo "::error:: ${SF_DIR} is not mounted. Check the 'mounts' entry in devcontainer.json."
  exit 1
fi

# .sf/ is gitignored, so a fresh clone has no target-org. Fall back to the
# alias committed in devcontainer.json.
target="$(sf config get target-org --json 2>/dev/null \
  | jq -r '.result[0].value // empty' || true)"

if [ -z "$target" ]; then
  target="${SF_DEFAULT_ORG_ALIAS:-}"
  if [ -z "$target" ]; then
    echo "No target-org set and SF_DEFAULT_ORG_ALIAS is empty. Set one with:"
    echo "    sf config set target-org <alias>"
    exit 1
  fi
  echo "No target-org configured; defaulting to '${target}'."
  sf config set target-org "$target"
fi

if sf org display --target-org "$target" >/dev/null 2>&1; then
  echo "✅ Salesforce org '${target}' is authorized and set as target-org."
  sf org display --target-org "$target" | head -n 12
else
  cat <<EOF
❌ Org '${target}' is NOT authorized in the mounted ~/.sf.

Credentials are shared with your host, so log in ONCE on the host (or here —
either persists to both):

    sf org login web --alias ${target} --set-default

Then reopen the container, or just re-run:

    .devcontainer/post-create.sh
EOF
  exit 1
fi
```

```bash
chmod +x .devcontainer/post-create.sh
```

- [ ] **Step 3: Update `.devcontainer/devcontainer.json`**

Replace the whole file with:

```jsonc
{
  "name": "Salesforce Development",
  "image": "gforceinnovation/sf-devcontainer:latest",

  // The host's Salesforce auth is shared, not copied: logging in on either
  // side persists to both. Note this exposes EVERY org you have authorized,
  // production included, to anything running in this container.
  "mounts": [
    "source=${localEnv:HOME}/.sf,target=/home/vscode/.sf,type=bind",
    "source=${localEnv:HOME}/.sfdx,target=/home/vscode/.sfdx,type=bind",
    "source=sf-develop-demo-history,target=/commandhistory,type=volume"
  ],

  // .sf/ is gitignored, so a fresh clone has no target-org. This committed
  // alias is what makes the default survive cloning.
  "containerEnv": {
    "SF_DEFAULT_ORG_ALIAS": "github1"
  },

  "customizations": {
    "vscode": {
      "extensions": [
        "salesforce.salesforcedx-vscode-expanded",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "redhat.vscode-xml",
        "github.copilot"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "zsh",
        "terminal.integrated.profiles.linux": {
          "zsh": { "path": "/bin/zsh" }
        }
      }
    }
  },

  "remoteUser": "vscode",
  "postCreateCommand": "npm install && .devcontainer/post-create.sh"
}
```

The `git` and `github-cli` features are gone — the image already ships both, so
they only added rebuild time.

- [ ] **Step 4: Verify the JSON parses**

```bash
jq empty .devcontainer/devcontainer.json && echo "valid JSONC-as-JSON"
```

If `jq` rejects the comments, that is expected for strict JSON — devcontainer
supports JSONC. Validate instead with:

```bash
npx --yes jsonc-parser-cli .devcontainer/devcontainer.json 2>/dev/null \
  || python3 -c "import json,re,sys; s=open('.devcontainer/devcontainer.json').read(); s=re.sub(r'^\s*//.*$','',s,flags=re.M); json.loads(s); print('valid')"
```

- [ ] **Step 5: Commit**

```bash
git add -A .devcontainer/
git commit -m "feat: inherit host Salesforce auth in the devcontainer

Opening the devcontainer left you unauthenticated every rebuild, because
credentials live in the host ~/.sf and were not shared. That directory is now
bind-mounted, so auth is inherited and a login on either side persists to both.

post-create.sh resolves target-org — falling back to a committed alias, since
.sf/ is gitignored and never reaches a fresh clone — and fails loudly with the
exact login command when the org is not authorized, rather than leaving a shell
that looks fine and cannot deploy.

Also deletes .devcontainer/{Dockerfile,.zshrc,.p10k.zsh}: devcontainer.json
pulls the published image, so none of them were ever built, and the Dockerfile
claimed Node 20 where the image ships 24."
```

---

### Task 4: Verify end-to-end in sf-develop-demo

**Files:** none modified — this task produces evidence.

**Interfaces:**
- Consumes: Task 1's image and Task 3's devcontainer config.

- [ ] **Step 1: Authorize an org on the host (prerequisite)**

```bash
sf org login web --alias github1 --set-default
sf org list
```

Expected: `github1` listed. Nothing below can pass without this — at plan time
the host has zero authorized orgs.

- [ ] **Step 2: Point the consumer at the locally built image**

In `sf-develop-demo/.devcontainer/devcontainer.json`, temporarily change:

```jsonc
"image": "sf-devcontainer:test",
```

(Task 1 built that tag. **Revert this line before committing.**)

- [ ] **Step 3: Reopen in container and run the checks**

Inside the container terminal:

```bash
sf org list                      # 1. shows the host's orgs
sf config get target-org         # 2. resolves to github1
sf org display                   # 3. succeeds with no login step
command -v starship              # 5. present
ls ~/.oh-my-zsh 2>&1             # 5. "No such file or directory"
time zsh -i -c exit              # 6. record the number
sf project deploy start --dry-run --source-dir force-app   # 8. reaches the org
```

Check 4 is visual: the prompt shows `☁ github1`.

- [ ] **Step 4: Verify the mount is bidirectional**

Inside the container:

```bash
sf org login web --alias probe-org
```

Then on the **host**:

```bash
sf org list | grep probe-org
```

Expected: present. Clean up with `sf org logout --target-org probe-org --no-prompt`.

- [ ] **Step 5: Run the negative test**

This is the check that matters most — it proves the script fails loudly.

```bash
sf config set target-org definitely-not-authorized
.devcontainer/post-create.sh; echo "exit=$?"
```

Expected: exit=1, and the output contains
`sf org login web --alias definitely-not-authorized --set-default`.

Restore: `sf config set target-org github1`.

- [ ] **Step 6: Revert the temporary image pin**

```bash
cd ~/gforce/sf-develop-demo
git diff .devcontainer/devcontainer.json   # confirm only the image line changed
git checkout .devcontainer/devcontainer.json
```

- [ ] **Step 7: Run the image regression suite**

```bash
cd ~/gforce/sf-docker-images
pytest tests/test_sf_devcontainer.py -v
```

Expected: PASS.

- [ ] **Step 8: Record the results in the spec**

Append a `## Verification results` section to
`docs/superpowers/specs/2026-08-06-devcontainer-dx-design.md` with the actual
shell-startup numbers (before and after), the image size delta, and a line per
check. Commit:

```bash
git add docs/superpowers/specs/2026-08-06-devcontainer-dx-design.md
git commit -m "docs: record devcontainer DX verification results"
```

---

## Notes for the implementer

- **Task 1 and Task 3 are independent.** Task 3 works against today's published
  image and can ship immediately; Task 1 only reaches users when v3.0.0
  publishes. Do not block one on the other.
- **Do not release as part of this plan.** v3.0.0 is cut separately via the
  `releasing` skill, and only on the user's explicit go-ahead.
- **If `zsh-autosuggestions` paths differ** from `/usr/share/zsh-autosuggestions/`
  on the built image, fix the paths in both `.zshrc` and the test — do not paper
  over it by falling back to git clones.
