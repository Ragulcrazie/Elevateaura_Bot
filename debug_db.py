import asyncio
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def debug():
    db = SupabaseClient()
    await db.connect()
    
    print("Attempting to insert 1 ghost...")
    try:
        res = db.client.table("ghost_profiles").insert({"name": "Test Ghost", "base_skill_level": 1000}).execute()
        print("Success!", res)
    except Exception as e:
        print("FULL ERROR DETAILS:")
        print(e)
        # Try to print specific attributes if they exist
        if hasattr(e, 'code'): print(f"Code: {e.code}")
        if hasattr(e, 'details'): print(f"Details: {e.details}")
        if hasattr(e, 'message'): print(f"Message: {e.message}")

if __name__ == "__main__":
    asyncio.run(debug())
