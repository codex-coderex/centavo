import os
from pathlib import Path

import webview

from db.connection import get_conn
from db.seed import run_seed
from db.tables import initialize_schema
from api.bridge import FinanceApi


BASE_DIR = Path(__file__).resolve().parent


def initialize_database_schema() -> None:
    with get_conn() as conn:
        initialize_schema(conn)


def init_database() -> None:
    initialize_database_schema()
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
