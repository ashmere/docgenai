#!/bin/bash

# DocGenAI Docker Runner Script
# This script makes it easy to run DocGenAI with proper Docker configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MEMORY="8g"
CPUS="4"
IMAGE_NAME="docgenai"
VERBOSE=false

# Help function
show_help() {
    echo "DocGenAI Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND [ARGS...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose logging"
    echo "  -m, --memory   Set memory limit (default: 8g)"
    echo "  -c, --cpus     Set CPU limit (default: 4)"
    echo "  --build        Build the Docker image first"
    echo ""
    echo "Commands:"
    echo "  generate FILE/DIR  Generate documentation"
    echo "  diagram FILE       Generate diagram for file"
    echo "  shell             Start interactive shell"
    echo "  help              Show DocGenAI help"
    echo ""
    echo "Examples:"
    echo "  $0 generate src/models.py"
    echo "  $0 diagram src/models.py"
    echo "  $0 --verbose generate src/"
    echo "  $0 shell"
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
    log_info "Building DocGenAI Docker image..."
    if docker build -f docker/Dockerfile -t $IMAGE_NAME .; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Setup cache directory
setup_cache() {
    local cache_dir="$HOME/.cache/huggingface"
    if [ ! -d "$cache_dir" ]; then
        log_info "Creating cache directory: $cache_dir"
        mkdir -p "$cache_dir"
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

# Run Docker container
run_docker() {
    local cmd="$1"
    shift

    setup_cache
    setup_output

    local docker_args=(
        "--rm"
        "--memory=$MEMORY"
        "--cpus=$CPUS"
        "-v" "$HOME/.cache/huggingface:/app/.cache/huggingface"
        "-v" "$(pwd)/output:/app/output"
    )

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

            # Mount the target if it's outside the current directory
            if [[ "$target" = /* ]]; then
                docker_args+=("-v" "$target:$target")
            fi

            log_info "Generating documentation for: $target"
            docker run "${docker_args[@]}" $IMAGE_NAME \
                poetry run docgenai "${docgenai_args[@]}" generate "$target" "$@"
            ;;

        "diagram")
            if [ $# -eq 0 ]; then
                log_error "Please specify a file to generate diagram for"
                exit 1
            fi

            local target="$1"
            shift

            # Mount the target if it's outside the current directory
            if [[ "$target" = /* ]]; then
                docker_args+=("-v" "$target:$target")
            fi

            log_info "Generating diagram for: $target"
            docker run "${docker_args[@]}" $IMAGE_NAME \
                poetry run docgenai "${docgenai_args[@]}" generate "$target" --diagram "$@"
            ;;

        "shell")
            log_info "Starting interactive shell..."
            docker run -it "${docker_args[@]}" \
                -v "$(pwd):/app/workspace" \
                $IMAGE_NAME bash
            ;;

        "help")
            docker run --rm $IMAGE_NAME poetry run docgenai --help
            ;;

        *)
            log_error "Unknown command: $cmd"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments
BUILD_IMAGE=false

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
    show_help
    exit 1
fi

# Main execution
log_info "Starting DocGenAI with Docker"
log_info "Memory limit: $MEMORY, CPU limit: $CPUS"

check_docker

if [ "$BUILD_IMAGE" = true ]; then
    build_image
else
    check_image
fi

run_docker "$@"

log_success "DocGenAI completed successfully"
