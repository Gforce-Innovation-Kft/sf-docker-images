# Pinned by multi-arch index digest. Refresh with:
#   docker buildx imagetools inspect node:24-alpine --format '{{.Manifest.Digest}}'
FROM node:24-alpine@sha256:a0b9bf06e4e6193cf7a0f58816cc935ff8c2a908f81e6f1a95432d679c54fbfd

# Metadata labels
LABEL org.opencontainers.image.authors="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce Bulk Runner"
LABEL org.opencontainers.image.description="Lightweight SF CLI image for bulk org operations. Alpine-based, no Java."
LABEL org.opencontainers.image.source="https://github.com/Gforce-Innovation-Kft/sf-docker-images"
LABEL org.opencontainers.image.base.name="node:24-alpine"

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
# node:24-alpine ships with a 'node' user at UID 1000; remove it first.
# Alpine's adduser syntax differs from useradd; -D = no password, -s = shell.
RUN deluser node \
    && adduser -D -u 1000 -s /bin/bash ci

# Second account matching the GitHub Actions runner UID — see the long rationale
# in sf-ci/Dockerfile. GitHub Actions container jobs run as the runner UID
# (1001) to write /github/home, and `sf` crashes on a UID with no passwd entry,
# so 1001 is registered statically. `-G root` puts it in GID 0.
RUN adduser -D -u 1001 -G root -s /bin/bash runner

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

# Runtime user: non-root `ci` (UID 1000) — same decision as sf-ci, see the full
# rationale there. CONSUMER REQUIREMENT: run as a UID this image knows —
# 1000 (`ci`) or 1001 (`runner`, matching the GitHub Actions runner that owns
# /github/home). An unregistered UID crashes `sf` and cannot be fixed in the
# image.
USER root
RUN chgrp -R 0 /home/ci /opt/sf-data /opt/sf-config \
    && chmod -R g=u /home/ci /opt/sf-data /opt/sf-config

USER ci

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
