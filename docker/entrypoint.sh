#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Execute the docgenai CLI with any arguments passed to the container
poetry run docgenai "$@"
