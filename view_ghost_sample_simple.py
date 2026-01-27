import asyncio
from dotenv import load_dotenv
from database.db_client import SupabaseClient
import sys

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def view_ghosts():
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        print("Failed to connect")
        return

    try:
        # Fetch last 20 inserted ghosts
        response = db.client.table("ghost_profiles").select("name").order("id", desc=True).limit(20).execute()
        
        print(f"Total Ghosts: {len(response.data)} (showing last 20)")
        for ghost in response.data:
            print(f"- {ghost['name']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(view_ghosts())
