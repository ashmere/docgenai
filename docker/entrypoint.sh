#!/bin/bash

# DocGenAI Docker Entrypoint
# Provides environment validation and proper error handling

set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

# Validate environment
log "Starting DocGenAI container..."

# Check if cache directories exist
if [ ! -d "$HF_HOME" ]; then
    log "Warning: Model cache directory not found at $HF_HOME"
fi

if [ ! -d "$DOCGENAI_CACHE_DIR" ]; then
    log "Warning: Output cache directory not found at $DOCGENAI_CACHE_DIR"
fi

# Check available memory
if [ -f /proc/meminfo ]; then
    TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024))
    if [ $TOTAL_MEM_GB -lt 6 ]; then
        log "Warning: Only ${TOTAL_MEM_GB}GB memory available. DeepSeek models recommend 6GB+ for optimal performance."
    fi
fi

# Execute the docgenai CLI with arguments
log "Executing: docgenai $*"
exec poetry run docgenai "$@"
