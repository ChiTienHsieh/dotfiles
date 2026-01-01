# YOLO-CC Base Image
#
# Minimal image with bun + Claude Code
# Uses OAuth token passed via environment variable

FROM oven/bun:1-debian

# Install essential tools (including npm for global installs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    sudo \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (CC refuses --dangerously-skip-permissions as root)
RUN useradd -m -s /bin/bash claude && \
    echo "claude ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to claude user
USER claude
WORKDIR /home/claude

# Set npm prefix to user's home
RUN mkdir -p /home/claude/.npm-global && \
    npm config set prefix '/home/claude/.npm-global'
ENV PATH="/home/claude/.npm-global/bin:$PATH"

# Install Claude Code globally via npm
RUN npm install -g @anthropic-ai/claude-code

# Verify installation
RUN claude --version

WORKDIR /workspace

# Default command
CMD ["bash"]
