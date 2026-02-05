
import asyncio
import os
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def run_migration():
    print("🚀 Starting Referral Migration...")
    db = SupabaseClient()
    await db.connect()
    
    # Raw SQL execution via PostgREST is limited, but we can try via RPC or just assume column exists if valid.
    # Actually, Supabase-py doesn't support raw SQL easily without RPC.
    # But since I am the Agent, I can tell the user to run it.
    # OR better: I will handle the "column missing" error gracefully in code, 
    # but I strongly recommend running the SQL.
    
    print("Please run this in Supabase SQL Editor:")
    print("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT;")

if __name__ == "__main__":
    asyncio.run(run_migration())
