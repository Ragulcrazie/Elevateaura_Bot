import asyncio
import os
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def count_ghosts():
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        print("Failed to connect")
        return

    # Supabase doesn't always support simple count queries via client easily without exact syntax
    # But we can try selecting a single column and using count='exact'
    try:
        response = db.client.table("ghost_profiles").select("id", count="exact").execute()
        print(f"Total ghosts: {response.count}")
    except Exception as e:
        print(f"Error counting ghosts: {e}")

if __name__ == "__main__":
    asyncio.run(count_ghosts())
