# Pinned by multi-arch index digest. Refresh with:
#   docker buildx imagetools inspect ubuntu:22.04 --format '{{.Manifest.Digest}}'
FROM ubuntu:22.04@sha256:0e0a0fc6d18feda9db1590da249ac93e8d5abfea8f4c3c0c849ce512b5ef8982

# Metadata labels
LABEL org.opencontainers.image.authors="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce CI"
LABEL org.opencontainers.image.description="Lightweight Salesforce CI/CD image with SF CLI, Node.js, and Java"
LABEL org.opencontainers.image.source="https://github.com/Gforce-Innovation-Kft/sf-docker-images"
LABEL org.opencontainers.image.base.name="ubuntu:22.04"

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install all system packages, Node.js, Java, and SF CLI in optimized layers
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    apt-transport-https \
    # XML and JSON processing tools for CI
    xmlstarlet \
    jq \
    # Minimal utilities
    unzip \
    zip \
    # envsubst — renders secret-bearing metadata templates at deploy time
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Catch pipe failures (e.g. curl | bash)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Node.js 24.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# gitleaks — the secret-scan gate that stands between a build and an uploaded
# artifact. Pinned: a scanner that silently changes its ruleset changes what
# passes CI. No apt package exists, so fetch the release tarball.
ARG GITLEAKS_VERSION=8.21.2
RUN set -eux; \
    case "$(dpkg --print-architecture)" in \
      amd64) GL_ARCH=x64 ;; \
      arm64) GL_ARCH=arm64 ;; \
      *) echo "unsupported arch: $(dpkg --print-architecture)" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/gitleaks.tar.gz \
      "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${GL_ARCH}.tar.gz"; \
    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks; \
    chmod 755 /usr/local/bin/gitleaks; \
    rm -f /tmp/gitleaks.tar.gz; \
    gitleaks version

# Create ci user (non-root for security)
RUN useradd -m -s /bin/bash -u 1000 ci

# The DEFAULT runtime account: UID 1001, matching the GitHub-hosted runner.
#
# GitHub Actions container jobs bind-mount /github/home AND create the runner
# file-command files ($GITHUB_OUTPUT, $GITHUB_ENV, $GITHUB_STEP_SUMMARY) owned
# by the runner's UID, 1001. A container running as anything else gets
# "Permission denied" the moment a step sets an output.
#
# Defaulting to 1001 is what lets every consumer write a plain
# `container: gforceinnovation/sf-ci:<tag>` with no `options:` at all. Requiring
# `--user 1001` worked, but it was invisible until it failed, and it failed in a
# way that named neither the UID nor the file commands.
#
# GID 0 so it can write the group-0 paths set up below.
RUN useradd -m -s /bin/bash -u 1001 -g 0 runner

# Pin SF CLI data dirs to fixed paths owned by root so any runner UID can write.
# XDG_DATA_HOME/XDG_CONFIG_HOME redirect SF CLI away from $HOME/.sf.
# Dirs are world-writable so plugins can be updated at runtime by any user.
ENV XDG_DATA_HOME=/opt/sf-data
ENV XDG_CONFIG_HOME=/opt/sf-config
RUN mkdir -p /opt/sf-data /opt/sf-config \
    && chmod 777 /opt/sf-data /opt/sf-config

# Install plugins as ci user so they land in XDG_DATA_HOME=/opt/sf-data
USER ci
WORKDIR /home/ci
RUN echo y | sf plugins install sfdx-git-delta

# Runtime user: non-root `runner` (UID 1001) — the GitHub-hosted runner's UID.
#
# History, so nobody re-litigates it:
#   v1/v2  ran as root. Immune to every permission problem, privileged in every
#          pipeline.
#   v3.0.0 dropped root and defaulted to `ci` (1000), which meant every
#          container job had to remember `options: --user 1001`. Forgetting it
#          failed with "Permission denied" on a path nobody recognises, or with
#          "uv_os_get_passwd ENOENT" from deep inside oclif — neither of which
#          names the actual mistake.
#   v3.1.0 defaults to 1001. Consumers write `container: <image>` and nothing
#          else. `ci` (1000) stays registered for local `docker run` and for
#          self-hosted runners whose UID is 1000.
#
# An UNREGISTERED UID still does not work, and no Dockerfile change can fix it:
# os.userInfo() throws ENOENT, and the usual remedy — an entrypoint appending a
# passwd line — never runs, because GitHub Actions container jobs override
# ENTRYPOINT with `--entrypoint tail`. That is why both UIDs are baked in rather
# than resolved at runtime. Verified; do not re-attempt.
#
# GID 0 ownership lets either account write the SF CLI data and config dirs.
USER root
# /workspace is created explicitly rather than left to WORKDIR, which would
# create it owned by whoever USER happens to be at that point — a dependency on
# instruction ordering that breaks silently the next time this file is edited.
RUN mkdir -p /workspace \
    && chgrp -R 0 /home/ci /home/runner /opt/sf-data /opt/sf-config /workspace \
    && chmod -R g=u /home/ci /home/runner /opt/sf-data /opt/sf-config /workspace

USER runner

# Set environment variables for CI
ENV SFDX_CONTAINER_MODE=true
ENV SFDX_DISABLE_DNS_CHECK=true
ENV SF_AUTOUPDATE_DISABLE=true
ENV SF_DISABLE_TELEMETRY=true
ENV CI=true

# Switch back to dialog
ENV DEBIAN_FRONTEND=dialog

# Verify installations
RUN echo "Node version: $(node --version)" \
    && echo "NPM version: $(npm --version)" \
    && echo "Java version: $(java -version 2>&1 | head -n 1)" \
    && echo "SF CLI version: $(sf version)" \
    && echo "jq version: $(jq --version)" \
    && echo "xmlstarlet version: $(xmlstarlet --version)"

# Health check to ensure SF CLI is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sf version --json || exit 1

WORKDIR /workspace

CMD ["/bin/bash"]
