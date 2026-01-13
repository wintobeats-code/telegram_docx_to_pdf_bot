#!/bin/bash
set -euo pipefail

echo "запуск миграций"
uv run alembic upgrade head

echo "запуск бота"
exec uv run python -m main_bot "$@"
