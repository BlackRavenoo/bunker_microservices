docker compose up -d --build
uv sync --all-packages
source ./.venv/bin/activate
cd services/game_service/ && alembic upgrade head