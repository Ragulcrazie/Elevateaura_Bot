import asyncio
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def debug():
    db = SupabaseClient()
    await db.connect()
    
    print("Fetching User Stats...")
    try:
        res = db.client.table("users").select("user_id, questions_answered, quiz_state").execute()
        for user in res.data:
            print(f"User: {user['user_id']}")
            print(f"  - Questions Answered (Col): {user.get('questions_answered')}")
            state = user.get('quiz_state') or {}
            import json
            print(f"  - Quiz State (JSON):")
            print(json.dumps(state, indent=2, default=str)) 
            if state:
                print(f"  - Stats in JSON: {state.get('stats')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug())
