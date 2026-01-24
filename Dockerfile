FROM python:3.14-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.18-python3.14-trixie-slim /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

RUN apt-get -y update &&  \ 
    apt-get install --no-install-recommends postgresql-client \
    -y libreoffice ca-certificates && update-ca-certificates \
    rm -rf /var/lib/apt/lists/*

COPY . .

ENV PYTHONPATH=/app/.venv/lib/python3.14/site-packages

RUN uv sync --no-dev --locked --no-editable --python python3.14

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
