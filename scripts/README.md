# Scripts

Operational scripts that are not part of the running application.

## `init_db.py`

Creates the schema from the SQLAlchemy models in `packages/domain/db_models.py`.
Run it once against a new database before starting the API.

```bash
python scripts/init_db.py
```

It prints the dialect and server version, lists the tables it created and the ones
it found already there, and exits non-zero if it cannot connect, so it can be run
as a deploy step. `DATABASE_URL` is read from the environment or `.env`; if it is
unset, `packages/domain/database.py` falls back to a local SQLite file, and the
script says so rather than silently initialising the wrong database.

To create a user row at the same time:

```bash
python scripts/init_db.py --seed-user you@example.com
```

Two caveats worth knowing:

- `create_all` is additive. It never alters a table that already exists, so if a
  model changes shape the existing table stays as it was and nothing warns you.
  There is no migration tool in this project yet; a schema change means dropping
  the table or writing the ALTER by hand.
- The tests do not need this script. `tests/conftest.py` builds a throwaway SQLite
  database per run, so `python -m pytest` works on a clean clone with no setup.

## Adding a script here

Import from the repository root (`from packages.domain... import`) and put this at
the top so the import resolves when the file is run directly:

```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

Anchor it to `__file__`, not to `os.getcwd()`. Using the working directory means
the script only runs if you happen to be standing in the repository root, which is
the trap that made every test file in this project start with
`sys.path.append(os.getcwd())`. Tests get the path from `pythonpath` in
`pyproject.toml` instead.
