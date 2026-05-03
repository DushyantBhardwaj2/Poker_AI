import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
project_root = os.getcwd()
sys.path.append(project_root)

# Explicitly load .env from root
dotenv_path = os.path.join(project_root, ".env")
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment after loading .env")
    sys.exit(1)

print(f"Debug: DATABASE_URL starts with '{DATABASE_URL[:15]}...'")

# Safer host logging
try:
    host = DATABASE_URL.split('@')[1].split('/')[0]
    print(f"Connecting to: {host}")
except Exception:
    print("Connecting to database...")

if DATABASE_URL.startswith("sqlite"):
    print("Warning: Detected SQLite URL. This script is intended for PostgreSQL.")
    
engine = create_engine(DATABASE_URL)

def run_schema():
    schema_path = os.path.join("docs", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found")
        return

    with open(schema_path, "r") as f:
        sql_commands = f.read()

    # Split by semicolon to execute commands individually (Postgres usually handles full scripts but this is safer)
    # However, plpgsql blocks contain semicolons. Better to use one large execute if possible or a proper parser.
    # We'll try executing the whole block first.
    
    with engine.connect() as conn:
        print("Executing schema script...")
        try:
            conn.execute(text(sql_commands))
            conn.commit()
            print("Successfully initialized PostgreSQL schema.")
        except Exception as e:
            print(f"Error during schema execution: {e}")
            # If it fails due to multi-command, we might need a more sophisticated runner or run it via a tool.

if __name__ == "__main__":
    run_schema()
