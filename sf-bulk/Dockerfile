FROM node:20-alpine

# Metadata labels
LABEL maintainer="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce Bulk Runner"
LABEL org.opencontainers.image.description="Lightweight SF CLI image for bulk org operations. Alpine-based, no Java."
LABEL org.opencontainers.image.source="https://github.com/gforceinnovation/sf-docker-images"
LABEL org.opencontainers.image.base.name="node:20-alpine"

# libc6-compat: glibc compatibility layer for musl Alpine.
# Required because some npm native modules (included transitively by SF CLI)
# are compiled against glibc. Without this they fail to dlopen on musl.
# All other packages are pure JS so Alpine works cleanly.
RUN apk add --no-cache \
    bash \
    coreutils \
    curl \
    git \
    jq \
    unzip \
    libc6-compat

# Use bash for subsequent RUN steps (matches sf-ci behaviour, catches pipe failures)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Salesforce CLI globally as root
RUN npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# Create ci user (UID 1000) — used only to install plugins into XDG_DATA_HOME.
# node:20-alpine ships with a 'node' user at UID 1000; remove it first.
# Alpine's adduser syntax differs from useradd; -D = no password, -s = shell.
RUN deluser node \
    && adduser -D -u 1000 -s /bin/bash ci

# Pin SF CLI data dirs to fixed paths owned by nobody so any runner UID can write.
# XDG_DATA_HOME / XDG_CONFIG_HOME redirect SF CLI away from $HOME/.sf.
# Dirs are world-writable so plugins installed by ci user are readable by root,
# and so auth written at runtime by root (or any UID) succeeds without permission errors.
# This mirrors the exact same pattern used in sf-ci.
ENV XDG_DATA_HOME=/opt/sf-data
ENV XDG_CONFIG_HOME=/opt/sf-config
RUN mkdir -p /opt/sf-data /opt/sf-config \
    && chmod 777 /opt/sf-data /opt/sf-config

# Install plugins as ci user so they land in XDG_DATA_HOME=/opt/sf-data
USER ci
WORKDIR /home/ci
RUN echo y | sf plugins install sfdx-git-delta

# Switch back to root for runtime.
# ARC dind runner uses UID 1001 (runner) which != ci (1000).
# GitHub Actions bind-mounts /github/home with the runner's UID as owner,
# so running as ci causes EACCES. Root bypasses this on all runner types.
# This is the same deliberate decision as sf-ci.
USER root

# SF CLI environment — same set as sf-ci, ensures headless/container behaviour
ENV SFDX_CONTAINER_MODE=true
ENV SFDX_DISABLE_DNS_CHECK=true
ENV SF_AUTOUPDATE_DISABLE=true
ENV SF_DISABLE_TELEMETRY=true
ENV CI=true

# Verify installations
RUN echo "Node: $(node --version)" \
    && echo "SF CLI: $(sf version)" \
    && echo "jq: $(jq --version)" \
    && echo "sfdx-git-delta: $(sf plugins | grep sfdx-git-delta)"

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sf version --json || exit 1

WORKDIR /workspace

CMD ["/bin/bash"]
