FROM python:3.12-slim-trixie

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock /app/
COPY --from=services-src /common /common

RUN uv sync

COPY ./app /app/app
COPY ./protos /app/protos

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0" ]