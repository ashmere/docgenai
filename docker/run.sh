#!/bin/bash

# DocGenAI Docker Runner Script
# Optimized for DeepSeek-Coder-V2-Lite implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
MEMORY="12g"  # Increased for DeepSeek models
CPUS="4"
IMAGE_NAME="docgenai"
VERBOSE=false
BUILD_IMAGE=false

# Help function
show_help() {
    echo -e "${CYAN}DocGenAI Docker Runner${NC}"
    echo -e "${CYAN}DeepSeek-Coder-V2-Lite Implementation${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND [ARGS...]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose logging"
    echo "  -m, --memory   Set memory limit (default: 12g)"
    echo "  -c, --cpus     Set CPU limit (default: 4)"
    echo "  --build        Build the Docker image first"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  generate FILE/DIR     Generate documentation for files or directories"
    echo "  cache                 Manage caches (show stats, clear caches)"
    echo "  info                  Show model and configuration information"
    echo "  init                  Create default configuration file"
    echo "  test FILE             Test documentation generation on a single file"
    echo "  shell                 Start interactive shell in container"
    echo "  help                  Show DocGenAI help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 generate src/models.py"
    echo "  $0 generate src/ --output-dir docs/"
    echo "  $0 test src/models.py"
    echo "  $0 cache --clear-output-cache"
    echo "  $0 info"
    echo "  $0 --verbose --memory 16g generate src/"
    echo "  $0 shell"
    echo ""
    echo -e "${YELLOW}Cache Management:${NC}"
    echo "  $0 cache                    # Show cache statistics"
    echo "  $0 cache --clear            # Clear all caches"
    echo "  $0 cache --clear-model-cache     # Clear model cache only"
    echo "  $0 cache --clear-output-cache    # Clear output cache only"
    echo ""
    echo -e "${YELLOW}Performance Notes:${NC}"
    echo "  • First run downloads DeepSeek model (~4-8GB)"
    echo "  • Subsequent runs use cached model (much faster)"
    echo "  • Recommended: 12GB+ memory, 4+ CPUs"
    echo "  • Uses 4-bit quantization by default for efficiency"
}

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if image exists
check_image() {
    if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
        log_warning "Docker image '$IMAGE_NAME' not found."
        log_info "Building image..."
        build_image
    fi
}

# Build Docker image
build_image() {
    log_info "Building DocGenAI Docker image for DeepSeek-Coder-V2-Lite..."
    if docker build -f docker/Dockerfile -t $IMAGE_NAME .; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Setup cache directories
setup_cache() {
    local model_cache_dir="$HOME/.cache/models"
    local output_cache_dir="$(pwd)/.docgenai_cache"

    if [ ! -d "$model_cache_dir" ]; then
        log_info "Creating model cache directory: $model_cache_dir"
        mkdir -p "$model_cache_dir"
    fi

    if [ ! -d "$output_cache_dir" ]; then
        log_info "Creating output cache directory: $output_cache_dir"
        mkdir -p "$output_cache_dir"
    fi
}

# Setup output directory
setup_output() {
    local output_dir="$(pwd)/output"
    if [ ! -d "$output_dir" ]; then
        log_info "Creating output directory: $output_dir"
        mkdir -p "$output_dir"
    fi
}

# Get base Docker arguments
get_docker_args() {
    local docker_args=(
        "--rm"
        "--memory=$MEMORY"
        "--cpus=$CPUS"
        "-v" "$HOME/.cache/models:/app/.cache/models"
        "-v" "$(pwd)/.docgenai_cache:/app/.docgenai_cache"
        "-v" "$(pwd)/output:/app/output"
    )

    # Add current directory mount for relative paths
    docker_args+=("-v" "$(pwd):/app/workspace")

    echo "${docker_args[@]}"
}

# Run Docker container
run_docker() {
    local cmd="$1"
    shift

    setup_cache
    setup_output

    local docker_args
    IFS=' ' read -ra docker_args <<< "$(get_docker_args)"

    # Add verbose flag if requested
    local docgenai_args=()
    if [ "$VERBOSE" = true ]; then
        docgenai_args+=("--verbose")
    fi

    case "$cmd" in
        "generate")
            if [ $# -eq 0 ]; then
                log_error "Please specify a file or directory to generate documentation for"
                exit 1
            fi

            local target="$1"
            shift

            log_info "Generating documentation for: $target"
            docker run "${docker_args[@]}" $IMAGE_NAME \
                "${docgenai_args[@]}" generate "$target" "$@"
            ;;

        "cache")
            log_info "Managing DocGenAI cache..."
            docker run "${docker_args[@]}" $IMAGE_NAME \
                "${docgenai_args[@]}" cache "$@"
            ;;

        "info")
            log_info "Showing DocGenAI information..."
            docker run "${docker_args[@]}" $IMAGE_NAME \
                "${docgenai_args[@]}" info "$@"
            ;;

        "init")
            log_info "Initializing DocGenAI configuration..."
            docker run "${docker_args[@]}" $IMAGE_NAME \
                "${docgenai_args[@]}" init "$@"
            ;;

        "test")
            if [ $# -eq 0 ]; then
                log_error "Please specify a file to test documentation generation"
                exit 1
            fi

            local target="$1"
            shift

            log_info "Testing documentation generation for: $target"
            docker run "${docker_args[@]}" $IMAGE_NAME \
                "${docgenai_args[@]}" test "$target" "$@"
            ;;

        "shell")
            log_info "Starting interactive shell..."
            docker run -it "${docker_args[@]}" \
                --entrypoint bash \
                $IMAGE_NAME
            ;;

        "help")
            docker run --rm $IMAGE_NAME --help
            ;;

        *)
            log_error "Unknown command: $cmd"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -m|--memory)
            MEMORY="$2"
            shift 2
            ;;
        -c|--cpus)
            CPUS="$2"
            shift 2
            ;;
        --build)
            BUILD_IMAGE=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Check if command provided
if [ $# -eq 0 ]; then
    log_error "No command provided"
    echo ""
    show_help
    exit 1
fi

# Main execution
log_info "Starting DocGenAI with Docker (DeepSeek-Coder-V2-Lite)"
log_info "Memory limit: $MEMORY, CPU limit: $CPUS"

check_docker

if [ "$BUILD_IMAGE" = true ]; then
    build_image
else
    check_image
fi

run_docker "$@"

log_success "DocGenAI completed successfully"
