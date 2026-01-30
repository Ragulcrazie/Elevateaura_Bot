
import asyncio
import os
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def toggle_premium():
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        print("Failed to connect to Supabase.")
        return

    # Fetch recent users
    print("Fetching recent users...")
    # Sync call (db.client is sync)
    res = db.client.from_("users").select("*").execute()
    users = res.data
    
    if not users:
        print("No users found in database.")
        return

    print(f"\nFound {len(users)} users. Showing first 5:")
    for i, u in enumerate(users[:5]):
        status = u.get('subscription_status', 'free')
        print(f"[{i+1}] {u.get('full_name', 'Unknown')} (ID: {u.get('user_id')}) - Status: {status}")
        
    choice = input("\nEnter number to toggle status (or 0 to exit): ")
    try:
        idx = int(choice) - 1
        if idx < 0: return
        
        target_user = users[idx]
        current_status = target_user.get('subscription_status', 'free')
        new_status = 'premium' if current_status != 'premium' else 'free'
        
        # Update (Sync call)
        db.client.from_("users").update({"subscription_status": new_status}).eq("user_id", target_user['user_id']).execute()
        
        print(f"\n✅ Success! Changed {target_user.get('full_name')} to {new_status.upper()}.")
        print("Go check the bot now!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(toggle_premium())
