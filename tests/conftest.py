"""Shared setup for the whole suite.

Two things happen here, both at import time rather than in a fixture, because
`packages.domain.database` reads `DATABASE_URL` and builds its engine on import
and pytest imports conftest before any test module.

1. The suite gets its own throwaway SQLite file. It used to run against whatever
   `DATABASE_URL` pointed at, which for anyone who had followed the setup steps
   was the real development database, or on CI was nothing at all.

2. `SKIP_AUTH` is forced off. `verify_neon_token` returns a canned test user when
   `SKIP_AUTH=true` and `ENVIRONMENT` is local, and `load_dotenv()` pulls a
   developer's `.env` into the process, so the auth tests passed or failed
   depending on whose machine they ran on.

The integration tests also used to require a database somebody had created and
seeded by hand (`python tests/integration/verify_db.py`), and when it was missing
they printed "run verify_db.py first" and returned, which pytest counts as a
pass. The fixtures below replace that.
"""

import os
import tempfile
from pathlib import Path

import pytest

_DB_PATH = Path(tempfile.mkdtemp(prefix="pokersense-tests-")) / "test.db"

# Assignment, not setdefault: the point is to override an inherited value.
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH.as_posix()}"
os.environ["SKIP_AUTH"] = "false"
os.environ["ENVIRONMENT"] = "test"

from packages.domain import db_models  # noqa: E402  (registers the mappers on Base)
from packages.domain.database import Base, SessionLocal, engine  # noqa: E402
from packages.domain.db_models import User  # noqa: E402

ADMIN_EMAIL = "admin@pokersense.ai"


@pytest.fixture(scope="session", autouse=True)
def _database():
    """Create the schema once for the session and clean the file up afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    try:
        _DB_PATH.unlink()
    except OSError:
        # Windows can still hold the handle. A stray file in the system temp
        # directory is not worth failing an otherwise green run over.
        pass


@pytest.fixture
def db():
    """A session that is rolled back at the end of the test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def admin_user(db):
    """The account the integration tests attribute their writes to."""
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if user is None:
        user = User(email=ADMIN_EMAIL, name="Test Operator")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
