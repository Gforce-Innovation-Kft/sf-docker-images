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
    && rm -rf /var/lib/apt/lists/*

# Catch pipe failures (e.g. curl | bash)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Node.js 24.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# Create ci user (non-root for security)
RUN useradd -m -s /bin/bash -u 1000 ci

# Second, non-default account matching the GitHub Actions runner UID.
#
# GitHub Actions container jobs mount /github/home and the runner file-command
# dir owned by the runner's UID (1001 on GitHub-hosted runners), so a container
# job must run as that UID to write them — `options: --user 1001`. That alone is
# not enough: `sf` (oclif) calls Node's os.userInfo(), which throws ENOENT when
# the running UID has no passwd entry, so an unregistered 1001 crashes the CLI.
# Registering it statically is what lets those jobs drop `--user root`.
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

# Runtime user: non-root `ci` (UID 1000).
#
# History: this was `USER root` (927c06d) because GitHub Actions bind-mounts
# /github/home owned by the runner's UID — self-hosted (UID 1000) matched `ci`,
# but ARC dind (UID 1001) did not, giving EACCES on `mkdir /github/home/.sf`.
# Root bypassed the mismatch by ignoring permissions, at the cost of running
# every pipeline privileged. We take the security trade instead.
#
# CONSUMER REQUIREMENT: run the container as a UID this image knows about —
# 1000 (`ci`, the default) or 1001 (`runner`). GitHub Actions container jobs
# should pass `options: --user 1001` to match the runner that owns
# /github/home; on ARC set the runner pod's `securityContext.runAsUser`
# to whichever of the two matches.
#
# An UNREGISTERED UID does not work, and no Dockerfile change can fix it:
# os.userInfo() throws ENOENT, and the usual remedy — an entrypoint appending a
# passwd line — never runs, because GitHub Actions container jobs override
# ENTRYPOINT with `--entrypoint tail`. That is why the two UIDs are baked in
# rather than resolved at runtime. Verified; do not re-attempt.
#
# GID 0 ownership lets either account write the SF CLI data and config dirs.
USER root
RUN chgrp -R 0 /home/ci /opt/sf-data /opt/sf-config \
    && chmod -R g=u /home/ci /opt/sf-data /opt/sf-config

USER ci

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
