import asyncio
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def view_ghosts():
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        print("Failed to connect")
        return

    try:
        # Fetch last 50 inserted ghosts
        response = db.client.table("ghost_profiles").select("name", count="exact").order("id", desc=True).limit(50).execute()
        
        print(f"Total Ghosts in DB: {response.count}\n")
        print("Here are the latest 50 generated names:\n")
        print("-" * 30)
        for i, ghost in enumerate(response.data, 1):
            print(f"{i}. {ghost['name']}")
        print("-" * 30)
            
    except Exception as e:
        print(f"Error fetching ghosts: {e}")

if __name__ == "__main__":
    asyncio.run(view_ghosts())
