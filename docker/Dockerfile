# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-root: Don't install the project itself, only dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY src/ /app/src

# Set up the entrypoint
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# The entrypoint will execute the CLI
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command can be --help
CMD ["--help"]
