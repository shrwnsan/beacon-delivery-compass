# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - 
ENV PATH="${PATH}:/root/.local/bin"

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && mkdir -p /home/$USERNAME/.vscode-server /home/$USERNAME/.vscode-server-insiders \
    && chown ${USERNAME}:${USERNAME} /home/$USERNAME/.vscode-server* \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Switch to the non-root user
USER $USERNAME

# Set the working directory
WORKDIR /workspaces/beacon-delivery-compass

# Copy only the dependency files first for better caching
COPY --chown=$USERNAME:$USERNAME pyproject.toml ./

# Install project dependencies
RUN pip install --user -e .[dev]

# Copy the rest of the project files
COPY --chown=$USERNAME:$USERNAME . .

# Install pre-commit hooks
RUN pre-commit install
