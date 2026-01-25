import asyncio
import os
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def probe():
    db = SupabaseClient()
    connected = await db.connect()
    try:
        res = db.client.table('users').select("*").limit(1).execute()
        if res.data:
            print("Columns found:", list(res.data[0].keys()))
            print("Quiz State:", res.data[0].get('quiz_state'))
        else:
            print("No users.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe())
