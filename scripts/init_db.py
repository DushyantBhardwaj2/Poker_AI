"""Create the database schema from the SQLAlchemy models.

Run this once against a fresh database before starting the API:

    python scripts/init_db.py

It reports what it found and what it created, and exits non-zero if it could not
connect, so it is safe to put in front of a deploy step.

This replaces two files. `scripts/init_postgres.py` read `docs/schema.sql`, and
there is no `docs/` directory in this repository, so every run ended at
"Error: docs/schema.sql not found" - the schema lives in
`packages/domain/db_models.py` and nowhere else. `tests/integration/verify_db.py`
did work, but it was a script sitting in the test tree that pytest collected and
that the integration tests told you to run by hand first; the fixtures in
`tests/conftest.py` handle that now.
"""

import argparse
import os
import sys

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# The package imports itself absolutely, so the repository root has to be
# importable when this is run as a script from anywhere.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# database.py calls load_dotenv() and reads DATABASE_URL at import time, so the
# .env file is already in effect by the time these names exist.
from packages.domain import db_models  # noqa: E402,F401  (registers the mappers on Base)
from packages.domain.database import DATABASE_URL, Base, SessionLocal, engine, is_sqlite
from packages.domain.db_models import User  # noqa: E402


def redacted_target(url: str) -> str:
    """Describe where we are connecting without printing the password."""
    if "@" in url:
        scheme = url.split("://", 1)[0]
        host = url.split("@", 1)[1]
        return f"{scheme}://...@{host}"
    return url


def server_version() -> str:
    query = "SELECT sqlite_version()" if is_sqlite else "SELECT version()"
    with engine.connect() as conn:
        return str(conn.execute(text(query)).scalar())


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the PokerSense schema.")
    parser.add_argument(
        "--seed-user",
        metavar="EMAIL",
        help="also create a user row with this email, if it does not exist",
    )
    args = parser.parse_args()

    print(f"Target: {redacted_target(DATABASE_URL)}")
    if is_sqlite:
        # Worth saying out loud: the default in database.py is a local SQLite file,
        # so a missing DATABASE_URL does not fail, it quietly initialises the
        # wrong database.
        print("Dialect: SQLite. If you meant to hit Neon, DATABASE_URL is not set.")

    try:
        print(f"Server: {server_version()}")
    except SQLAlchemyError as exc:
        print(f"Could not connect: {exc}")
        return 1

    before = set(inspect(engine).get_table_names())
    Base.metadata.create_all(bind=engine)
    after = set(inspect(engine).get_table_names())

    created = sorted(after - before)
    existing = sorted(t for t in Base.metadata.tables if t in before)

    if created:
        print(f"Created {len(created)} table(s): {', '.join(created)}")
    if existing:
        # create_all is additive and never alters a table it already found, so an
        # existing table with an out-of-date shape stays out of date silently.
        print(f"Already present, left untouched: {', '.join(existing)}")
    if not created and not existing:
        print("No tables. Something is wrong with the model imports.")
        return 1

    if args.seed_user:
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.email == args.seed_user).first()
            if user:
                print(f"User {args.seed_user} already exists: {user.user_id}")
            else:
                user = User(email=args.seed_user)
                session.add(user)
                session.commit()
                print(f"Created user {args.seed_user}: {user.user_id}")
        except SQLAlchemyError as exc:
            session.rollback()
            print(f"Could not seed user: {exc}")
            return 1
        finally:
            session.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
