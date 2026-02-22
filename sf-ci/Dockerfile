FROM ubuntu:22.04

# Metadata labels
LABEL maintainer="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce CI"
LABEL org.opencontainers.image.description="Lightweight Salesforce CI/CD image with SF CLI, Node.js, and Java"
LABEL org.opencontainers.image.source="https://github.com/gforceinnovation/sf-docker-images"
LABEL org.opencontainers.image.base.name="ubuntu:22.04"

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install all system packages, Node.js, Java, and SF CLI in optimized layers
# Note: Using --allow-unauthenticated temporarily to work around ARM64 GPG signature issues
RUN apt-get update --allow-insecure-repositories || apt-get update \
    && apt-get -y install --no-install-recommends --allow-unauthenticated \
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

# Install Node.js 20.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# Create ci user (non-root for security)
RUN useradd -m -s /bin/bash -u 1000 ci

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

# Switch back to root for runtime.
# GitHub Actions bind-mounts /github/home with the runner's UID as owner:
#   - self-hosted (gabor, UID 1000 = ci): worked without this
#   - ARC dind (runner, UID 1001 ≠ ci): ci can't write → EACCES on mkdir .sf
# Running as root bypasses UID mismatch on /github/home across all runner types.
USER root

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
