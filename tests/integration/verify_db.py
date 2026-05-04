import os
import sys
import uuid
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Add current directory to path so we can import packages
sys.path.append(os.getcwd())

from packages.domain.database import Base, DATABASE_URL, engine, is_sqlite
from packages.domain.db_models import User, Opponent, OpponentStats

def verify_connection():
    print(f"Checking connection to: {DATABASE_URL}")
    
    try:
        with engine.connect() as conn:
            if is_sqlite:
                result = conn.execute(text("SELECT sqlite_version();"))
                print(f"✅ Successfully connected to SQLite!")
            else:
                result = conn.execute(text("SELECT version();"))
                print(f"✅ Successfully connected to PostgreSQL!")
            
            version = result.fetchone()
            print(f"Database Version: {version[0]}")
            
            print("\nCreating tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created successfully!")
            
            # Create a default test user
            Session = sessionmaker(bind=engine)
            session = Session()
            
            test_user = session.query(User).filter(User.email == "admin@pokersense.ai").first()
            if not test_user:
                print("Creating default test user: admin@pokersense.ai")
                test_user = User(email="admin@pokersense.ai")
                session.add(test_user)
                session.commit()
                print(f"✅ Test User Created! ID: {test_user.user_id}")
            else:
                print(f"ℹ️ Test User already exists. ID: {test_user.user_id}")
            
            session.close()
            
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    load_dotenv()
    verify_connection()
