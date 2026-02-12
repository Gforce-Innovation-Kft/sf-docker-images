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

# Install Node.js 20.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# Create ci user (non-root for security)
RUN useradd -m -s /bin/bash -u 1000 ci

# Switch to ci user
USER ci
WORKDIR /home/ci

# Install essential SF CLI plugins for CI/CD
RUN echo y | sf plugins install sfdx-git-delta

# Create directories for Salesforce CLI
RUN mkdir -p /home/ci/.sfdx /home/ci/.sf /home/ci/.config

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
