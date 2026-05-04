# 📜 Automation Scripts

This directory contains scripts for database management and system maintenance.

## `init_postgres.py`
Initializes the PostgreSQL database with the required schema.

**Usage:**
```bash
export DATABASE_URL=your_postgres_url
python scripts/init_postgres.py
```
This script reads `docs/schema.sql` and executes it against the database. It handles both local development and production (Neon/Postgres).

## How to add new scripts
1. Place the Python script in this directory.
2. Ensure it respects the project root by adding `sys.path.append(os.getcwd())`.
3. Document its purpose here.
