# Smart Steps AI Professional Persona Module - Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.9-slim AS builder

# Set build arguments and environment variables
ARG BUILD_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user
RUN groupadd -g 1000 smartsteps && \
    useradd -u 1000 -g smartsteps -s /bin/bash -m smartsteps

# Create directory structure
WORKDIR /app
RUN mkdir -p /app/smart_steps_ai /app/logs /app/data

# Copy and install requirements first (for better caching)
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

# Copy application code
COPY smart_steps_ai/ /app/smart_steps_ai/
COPY setup.py README.md /app/

# Install the application
RUN pip install --user -e .

# Production stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/smartsteps/.local/bin:$PATH \
    SMARTSTEPS_ENV=production \
    SMARTSTEPS_CONFIG_DIR=/etc/smartsteps

# Create a non-privileged user
RUN groupadd -g 1000 smartsteps && \
    useradd -u 1000 -g smartsteps -s /bin/bash -m smartsteps

# Create directory structure
RUN mkdir -p /app /app/logs /app/data /etc/smartsteps /var/lib/smartsteps && \
    chown -R smartsteps:smartsteps /app /app/logs /app/data /etc/smartsteps /var/lib/smartsteps

# Copy installed packages and application from builder
COPY --from=builder --chown=smartsteps:smartsteps /root/.local /home/smartsteps/.local
COPY --from=builder --chown=smartsteps:smartsteps /app/smart_steps_ai /app/smart_steps_ai

# Copy configuration templates and entrypoint script
COPY --chown=smartsteps:smartsteps config/templates/ /app/config/templates/
COPY --chown=smartsteps:smartsteps scripts/docker/entrypoint.sh /app/entrypoint.sh

# Set permissions
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER smartsteps
WORKDIR /app

# Expose API port
EXPOSE 8543

# Set volumes
VOLUME ["/app/data", "/app/logs", "/etc/smartsteps"]

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Set default command
CMD ["python", "-m", "smart_steps_ai.server"]
