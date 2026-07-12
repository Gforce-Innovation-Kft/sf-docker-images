# Pinned by multi-arch index digest. Refresh with:
#   docker buildx imagetools inspect ubuntu:22.04 --format '{{.Manifest.Digest}}'
FROM ubuntu:22.04@sha256:0e0a0fc6d18feda9db1590da249ac93e8d5abfea8f4c3c0c849ce512b5ef8982

# Metadata labels
LABEL org.opencontainers.image.authors="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce DevContainer"
LABEL org.opencontainers.image.description="Full-featured Salesforce development environment with SF CLI, Node.js, Java, and Zsh"
LABEL org.opencontainers.image.source="https://github.com/Gforce-Innovation-Kft/sf-docker-images"
LABEL org.opencontainers.image.base.name="ubuntu:22.04"

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages in a single layer with cleanup
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    apt-utils \
    dialog \
    ca-certificates \
    curl \
    wget \
    git \
    gnupg2 \
    lsb-release \
    apt-transport-https \
    software-properties-common \
    build-essential \
    openssl \
    vim \
    nano \
    unzip \
    zip \
    xz-utils \
    # XML and JSON processing tools
    xmlstarlet \
    jq \
    # Additional utilities
    less \
    htop \
    tree \
    # Modern CLI tools (Ubuntu ships fd/bat as fdfind/batcat — symlinked below)
    ripgrep \
    fd-find \
    bat \
    # Zsh and related
    zsh \
    fonts-powerline \
    locales \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    2>&1

# Set locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Catch pipe failures (e.g. curl | bash)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Node.js 24.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

# GitHub CLI from the official apt repo
RUN mkdir -p -m 755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Pinned CLI tools from GitHub releases (multi-arch; apt versions are too old
# for shell integration — e.g. `fzf --zsh` needs >= 0.48, Ubuntu 22.04 ships 0.29)
ARG TARGETARCH
ARG FZF_VERSION=0.74.0
ARG ZOXIDE_VERSION=0.10.0
ARG EZA_VERSION=0.23.5
ARG DELTA_VERSION=0.19.2
ARG LAZYGIT_VERSION=0.63.0
RUN ARCH="${TARGETARCH:-$(dpkg --print-architecture)}" \
    && case "${ARCH}" in \
    amd64) RUST_ARCH=x86_64; LG_ARCH=x86_64 ;; \
    arm64) RUST_ARCH=aarch64; LG_ARCH=arm64 ;; \
    *) echo "unsupported architecture: ${ARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/junegunn/fzf/releases/download/v${FZF_VERSION}/fzf-${FZF_VERSION}-linux_${ARCH}.tar.gz" | tar -xz -C /usr/local/bin fzf \
    && curl -fsSLo /tmp/zoxide.deb "https://github.com/ajeetdsouza/zoxide/releases/download/v${ZOXIDE_VERSION}/zoxide_${ZOXIDE_VERSION}-1_${ARCH}.deb" \
    && curl -fsSLo /tmp/delta.deb "https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION}_${ARCH}.deb" \
    && dpkg -i /tmp/zoxide.deb /tmp/delta.deb \
    && curl -fsSL "https://github.com/eza-community/eza/releases/download/v${EZA_VERSION}/eza_${RUST_ARCH}-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin \
    && curl -fsSL "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_${LG_ARCH}.tar.gz" | tar -xz -C /usr/local/bin lazygit \
    && rm -f /tmp/*.deb \
    && ln -sf /usr/bin/batcat /usr/local/bin/bat \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd

# Global formatters/linters for Apex + LWC work (usable without a project package.json)
RUN npm install -g prettier prettier-plugin-apex eslint \
    && npm cache clean --force

# delta as the system git pager (only engages on a TTY — no effect on scripts/CI)
RUN git config --system core.pager delta \
    && git config --system interactive.diffFilter "delta --color-only" \
    && git config --system delta.navigate true \
    # diff3, not zdiff3 — Ubuntu 22.04's git 2.34 predates zdiff3 (2.35+)
    && git config --system merge.conflictStyle diff3

# Create vscode user with sudo privileges
RUN useradd -m -s /bin/zsh -u 1000 vscode \
    && echo vscode ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Switch to vscode user
USER vscode
WORKDIR /home/vscode

# Install SF CLI autocomplete for zsh
RUN sf autocomplete zsh

# Install SF CLI plugins
RUN echo y | sf plugins install code-analyzer && \
    echo y | sf plugins install sfdx-git-delta && \
    echo y | sf plugins install sfdx-browserforce-plugin

# Install Oh My Zsh, Powerlevel10k theme, and Zsh plugins in one layer
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k" \
    && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" \
    && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" \
    && git clone --depth=1 https://github.com/zsh-users/zsh-completions "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-completions"

# Copy Zsh configuration files owned by vscode directly — avoids a recursive
# root chown layer that would duplicate all of /home/vscode in the image
COPY --chown=vscode:vscode .zshrc /home/vscode/.zshrc
COPY --chown=vscode:vscode .p10k.zsh /home/vscode/.p10k.zsh

# Create directories for Salesforce CLI
RUN mkdir -p /home/vscode/.sfdx /home/vscode/.sf /home/vscode/.config

# Set environment variables
ENV SFDX_CONTAINER_MODE=true
ENV SFDX_DISABLE_DNS_CHECK=true
ENV SF_AUTOUPDATE_DISABLE=true
ENV SF_DISABLE_TELEMETRY=true

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Verify installations (keep bash SHELL here so ShellCheck can lint the pipes)
RUN echo "Node version: $(node --version)" \
    && echo "NPM version: $(npm --version)" \
    && echo "Java version: $(java -version 2>&1 | head -n 1)" \
    && echo "SF CLI version: $(sf version)" \
    && echo "jq version: $(jq --version)" \
    && echo "xmlstarlet version: $(xmlstarlet --version)"

# Set the default shell to zsh for runtime
SHELL ["/bin/zsh", "-c"]

# Health check to ensure SF CLI is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sf version --json || exit 1

WORKDIR /workspace

CMD ["/bin/zsh"]
