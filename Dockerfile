FROM python:3.11

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION="1.4.1" \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install poetry in an isolated environment
RUN python -m venv $POETRY_HOME \
    && pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /opt
COPY poetry.lock pyproject.toml ./
RUN poetry install --only main

WORKDIR /opt/app
COPY mo_smtp .
WORKDIR /opt/

#CMD ["poetry", "run", "python", "-m",  "mo_smtp.smtp_agent"]
CMD ["uvicorn", "--factory", "app.smtp_agent:create_app", "--host", "0.0.0.0"]

# Add build version to the environment last to avoid build cache misses
ARG COMMIT_TAG
ARG COMMIT_SHA
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD} \
    COMMIT_SHA=${COMMIT_SHA}
