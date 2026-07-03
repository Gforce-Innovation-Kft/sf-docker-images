# Per-image conventions

The three images serve different jobs and have **different, enforced constraints**. When
you add or remove anything, update the Dockerfile, the image README, and the matching
pytest-testinfra test in `tests/test_sf_*.py` (see
[testing-images skill](../skills/testing-images/SKILL.md)).

## sf-ci — thin CI image

- **Base:** `ubuntu:22.04`. **Runtimes:** Node 24.x, OpenJDK 17 (JRE), SF CLI `@2.*`.
- **Plugins:** `sfdx-git-delta` (keep minimal).
- **User:** `ci` (UID 1000, `/bin/bash`). **Runtime user: root** (ARC dind UID workaround).
- **Tools allowed:** git, jq, xmlstarlet, curl, unzip, zip.
- **FORBIDDEN:** vim, nano, zsh, htop, tree, build-essential, any editor/interactive/UI tool.
  Tests assert these are absent — do not add them.
- **Env:** `SFDX_CONTAINER_MODE`, `SFDX_DISABLE_DNS_CHECK`, `SF_AUTOUPDATE_DISABLE`,
  `SF_DISABLE_TELEMETRY`, `CI=true`; XDG dirs pinned to `/opt/sf-data` + `/opt/sf-config`.
- **Design rule:** must stay minimal. Consumable as `container: gforceinnovation/sf-ci:<tag>`.

## sf-devcontainer — rich VS Code dev image

- **Base:** `ubuntu:22.04`. **Runtimes:** Node 24.x, OpenJDK 17 (JDK), SF CLI `@2.*`.
- **Plugins:** `code-analyzer`, `sfdx-git-delta`, `sfdx-browserforce-plugin`.
- **User:** `vscode` (UID 1000, `/bin/zsh`, passwordless sudo).
- **Shell:** Oh My Zsh + Powerlevel10k + zsh-autosuggestions + zsh-syntax-highlighting +
  zsh-completions; `.zshrc` and `.p10k.zsh` baked in.
- **Tools:** everything in sf-ci plus vim, nano, wget, htop, tree, less, build-essential, openssl.
- **Design rule:** can be feature-rich; used via root [`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json).

## sf-bulk — ultralight Alpine image

- **Base:** `node:24-alpine` + `coreutils` (needed for `env -S` in the SF CLI shebang on musl/BusyBox).
- **No Java.** **Plugins:** `sfdx-git-delta`. **Tools:** bash, curl, git, jq, unzip, libc6-compat.
- **User:** `ci` (UID 1000, `/bin/bash`) created after `deluser node` (base ships `node` at UID 1000).
  **Runtime user: root.** XDG dirs pinned like sf-ci.
- **HARD LIMIT:** image must stay **under 600 MB** uncompressed (raised from 500 MB for the
  Node 24-alpine base). `tests/test_sf_bulk.py` fails if exceeded. No Java, no editors,
  no interactive tooling.

## Size budgets

| Image | Budget |
|-------|--------|
| sf-bulk | **< 600 MB** (hard, asserted in `tests/test_sf_bulk.py`) |
| sf-ci | medium (Ubuntu + Java + SF CLI) — keep minimal |
| sf-devcontainer | largest (full dev env) — no hard cap |
