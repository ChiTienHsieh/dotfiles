# YOLO-CC with UV (Python)
#
# Extends base image with uv for Python development

FROM yolo-cc-base

# Install uv (as claude user, inherited from base)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installed to user's home)
ENV PATH="/home/claude/.local/bin:$PATH"

# Verify installation
RUN uv --version

WORKDIR /workspace

CMD ["bash"]
