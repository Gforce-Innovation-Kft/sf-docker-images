FROM ubuntu:22.04

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages only
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

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Java (OpenJDK 17)
RUN apt-get update \
    && apt-get install -y openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Salesforce CLI
RUN npm install -g @salesforce/cli

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

# Verify installations and create versions file
RUN echo "Node version: $(node --version)" \
    && echo "NPM version: $(npm --version)" \
    && echo "Java version: $(java -version 2>&1 | head -n 1)" \
    && echo "SF CLI version: $(sf version)" \
    && echo "jq version: $(jq --version)" \
    && echo "xmlstarlet version: $(xmlstarlet --version)" \
    && echo "nodejs=$(node --version | sed 's/v//')\" > /home/ci/versions.txt \
    && echo "npm=$(npm --version)" >> /home/ci/versions.txt \
    && echo "java=$(java -version 2>&1 | head -n 1 | awk -F '\"' '{print $2}')" >> /home/ci/versions.txt \
    && echo "salesforce-cli=$(sf version --json 2>/dev/null | grep -o '\"version\":\"[^\"]*' | head -1 | cut -d'\"' -f4 || echo 'latest')" >> /home/ci/versions.txt \
    && echo "git=$(git --version | awk '{print $3}')" >> /home/ci/versions.txt \
    && echo "jq=$(jq --version | sed 's/jq-//')" >> /home/ci/versions.txt \
    && echo "xmlstarlet=$(xmlstarlet --version | head -n 1 | awk '{print $2}')" >> /home/ci/versions.txt \
    && cat /home/ci/versions.txt

WORKDIR /workspace

CMD ["/bin/bash"]
