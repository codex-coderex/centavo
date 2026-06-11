import webview
from db.connection import engine
from db.tables import metadata
from db.seed import run_seed

from api.accounts import AccountsAPI
from api.transactions import TransactionsAPI
from api.categories import CategoriesAPI
from api.budgets import BudgetsAPI
from api.goals import GoalsAPI
from api.recurring import RecurringAPI
from api.tags import TagsAPI
from api.currencies import CurrenciesAPI
from api.users import UsersAPI


class API(
    AccountsAPI,
    TransactionsAPI,
    CategoriesAPI,
    BudgetsAPI,
    GoalsAPI,
    RecurringAPI,
    TagsAPI,
    CurrenciesAPI,
    UsersAPI,
):
    """Combined API class exposed to frontend via pywebview."""
    pass


def init_database():
    """Create tables if they don't exist, seed system data."""
    metadata.create_all(engine)
    run_seed(sample_data=False)


def after_window_loaded(window):
    """
    Optional function that runs in a background thread after GUI starts.
    Can be used for tasks that need to run after the window is ready
    """
    pass


if __name__ == "__main__":
    init_database()

    api = API()

    window = webview.create_window(
        "Centavo",
        "frontend/dist/index.html",
        js_api=api,
        width=1280,
        height=800,
        min_size=(900, 600)
    )

    webview.start(after_window_loaded, window)