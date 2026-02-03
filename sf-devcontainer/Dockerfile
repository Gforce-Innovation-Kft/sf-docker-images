FROM ubuntu:22.04

# Metadata labels
LABEL maintainer="GForce Innovation"
LABEL org.opencontainers.image.title="Salesforce DevContainer"
LABEL org.opencontainers.image.description="Full-featured Salesforce development environment with SF CLI, Node.js, Java, and Zsh"
LABEL org.opencontainers.image.source="https://github.com/gforceinnovation/sf-docker-images"
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

# Install Node.js 20.x, Java, and Salesforce CLI in consolidated layers
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @salesforce/cli@2.* \
    && npm cache clean --force

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

# Install Oh My Zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Install Powerlevel10k theme
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Install Zsh plugins
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting \
    && git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions

# Copy Zsh configuration files
COPY .zshrc /home/vscode/.zshrc
COPY .p10k.zsh /home/vscode/.p10k.zsh

# Fix ownership
USER root
RUN chown -R vscode:vscode /home/vscode
USER vscode

# Create directories for Salesforce CLI
RUN mkdir -p /home/vscode/.sfdx /home/vscode/.sf /home/vscode/.config

# Set environment variables
ENV SFDX_CONTAINER_MODE=true
ENV SFDX_DISABLE_DNS_CHECK=true
ENV SF_AUTOUPDATE_DISABLE=true

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set the default shell to zsh
SHELL ["/bin/zsh", "-c"]

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

CMD ["/bin/zsh"]
