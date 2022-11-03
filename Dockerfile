FROM python:3.10

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN pip install --no-cache-dir poetry==1.2.0

WORKDIR /opt
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

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
