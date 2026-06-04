from sqlalchemy import create_engine
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "finance.db")

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

@contextmanager
def get_conn():
    with engine.begin() as conn:
        yield conn