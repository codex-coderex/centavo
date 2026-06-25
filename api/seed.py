from db.seed import run_seed
from api.responses import safe


def seed_sample_data():
    return safe(lambda: _seed_sample_data())


def _seed_sample_data():
    run_seed(sample_data=True)

    return {
        "status": "seeded",
        "message": "Demo sample data seeded successfully.",
        "summary": {
            "accounts": 4,
            "budgets": 3,
            "recurring_rules": 4,
            "goals": 3,
            "transactions": 30,
        },
    }