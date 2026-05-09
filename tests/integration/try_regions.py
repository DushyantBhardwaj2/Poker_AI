import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

load_dotenv()

project_ref = os.getenv("SUPABASE_PROJECT_REF")
password = os.getenv("SUPABASE_PASSWORD")

if not project_ref or not password:
    print("Error: SUPABASE_PROJECT_REF or SUPABASE_PASSWORD not found in .env")
    # We will exit or handle it gracefully
user = f"postgres.{project_ref}"

regions = [
    "ap-south-1",        # Mumbai
    "ap-southeast-1",    # Singapore
    "ap-southeast-2",    # Sydney
    "ap-northeast-1",    # Tokyo
    "us-east-1",         # N. Virginia
    "us-west-1",         # N. California
    "eu-west-1",         # Ireland
    "eu-central-1",      # Frankfurt
    "sa-east-1",         # Sao Paulo
    "ca-central-1"       # Canada
]

def try_connect():
    print(f"--- Starting Regional Search for Project: {project_ref} ---\n")
    for region in regions:
        host = f"aws-0-{region}.pooler.supabase.com"
        conn_str = f"postgresql://{user}:{password}@{host}:6543/postgres?sslmode=require"
        
        print(f"Trying {region} ({host})...", end=" ", flush=True)
        try:
            conn = psycopg2.connect(conn_str, connect_timeout=5)
            print("✅ SUCCESS!")
            conn.close()
            return region
        except OperationalError as e:
            err_msg = str(e).strip()
            if "tenant/user" in err_msg.lower() or "tenant or user" in err_msg.lower():
                print("❌ Not in this region.")
            elif "timeout" in err_msg.lower():
                print("⏳ Timeout.")
            else:
                print(f"❌ Error: {err_msg[:50]}...")
                
    return None

if __name__ == "__main__":
    found_region = try_connect()
    if found_region:
        print(f"\n🎉 FOUND IT! Your project is in: {found_region}")
        print(f"Update your .env with: aws-0-{found_region}.pooler.supabase.com")
    else:
        print("\n❌ Could not find the project in common regions. Please check your Supabase dashboard for the exact host.")
