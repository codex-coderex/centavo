import os
from pathlib import Path

import webview
from alembic import command
from alembic.config import Config

from db.seed import run_seed
from api.bridge import FinanceApi


BASE_DIR = Path(__file__).resolve().parent


def run_migrations() -> None:
    alembic_ini = BASE_DIR / "alembic.ini"

    if not alembic_ini.exists():
        raise RuntimeError(f"Missing Alembic config: {alembic_ini}")

    cfg = Config(str(alembic_ini))

    db_path = os.getenv("DB_PATH", "finance.db")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    command.upgrade(cfg, "head")


def init_database() -> None:
    run_migrations()
    run_seed(sample_data=False)


def main() -> None:
    init_database()

    frontend_url = os.getenv("FRONTEND_DEV_URL")

    if frontend_url:
        window_url = frontend_url
    else:
        window_url = str(BASE_DIR / "frontend" / "app.html")

    webview.create_window(
        "Centavo",
        window_url,
        js_api=FinanceApi(),
        width=1280,
        height=800,
        min_size=(900, 600),
    )

    webview.start(debug=bool(frontend_url))


if __name__ == "__main__":
    main()