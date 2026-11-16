"""
Shared fixtures for pytest.
DATABASE_URL must be set BEFORE importing app because init_db() runs
at module level.  GitHub Actions will supply it via the env: key;
locally you need a running Postgres instance.
"""

import os, pytest, psycopg2

# ── Guarantee the env-var exists before app is imported ──────────
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/tasks_test",
)
os.environ["DATABASE_URL"] = DB_URL

from app import app                       # noqa: E402  (import after env-var)


@pytest.fixture()
def client():
    """Yield a Flask test client; wipe the tasks table between tests."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    # clean up so each test starts with an empty table
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks")

