FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10


ENV APP_MODULE="opalizer.main:app"

COPY --from=requirements-stage /tmp/requirements.txt /opalizer/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opalizer/requirements.txt

COPY tests/ tests/
COPY opalizer/ opalizer/
COPY alembic/ alembic/
COPY alembic.ini ./
