
import asyncio
from database.db_client import SupabaseClient

async def run_migration():
    print("🚀 Adding Terms Acceptance Columns...")
    # Since we can't run raw SQL easily via the client library without RCP, 
    # we will rely on the user running the SQL in the dashboard.
    # BUT, I can try to use the 'rpc' function if you have a 'run_sql' function set up (unlikely).
    
    print("\nPlease run this in Supabase SQL Editor:")
    print("ALTER TABLE users ADD COLUMN IF NOT EXISTS terms_accepted BOOLEAN DEFAULT FALSE;")
    print("ALTER TABLE users ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMP WITH TIME ZONE;")

if __name__ == "__main__":
    asyncio.run(run_migration())
