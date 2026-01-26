import asyncio
import os
from dotenv import load_dotenv
from database.db_client import SupabaseClient

load_dotenv()

async def test_lifecycle():
    print("--- STARTING REPRODUCTION TEST ---")
    db = SupabaseClient()
    connected = await db.connect()
    if not connected:
        print("Failed to connect DB")
        return

    # 1. Setup Test User
    USER_ID = 999999999
    print(f"1. Creating Test User {USER_ID}")
    await db.upsert_user({
        "user_id": USER_ID,
        "full_name": "Test Bot",
        "quiz_state": None # Start clean
    })

    # 2. Simulate 10 Questions
    print("2. Simulating 10 Updates...")
    for i in range(1, 11):
        # Update Stats (Simulates update_user_stats)
        await db.update_user_stats(USER_ID, is_correct=True, time_taken=10.0)
        
        # Save Session (Simulates save_quiz_state)
        # In the bot, this happens AFTER update_user_stats
        dummy_state = {
            "questions": [],
            "current_q_index": i,
            "score": i*10
        }
        await db.save_quiz_state(USER_ID, dummy_state)
        print(f"   - Question {i} handled.")

    # 3. Verify Stats BEFORE Clear
    user = await db.get_user(USER_ID)
    stats = user["quiz_state"].get("stats", {})
    print(f"3. Stats BEFORE Clear: {stats}")
    if stats.get("questions_answered") != 10:
        print("❌ FAILED: Stats didn't reach 10 before clear.")
        return

    # 4. Simulate Finish (Clear State)
    print("4. Clearing Quiz State (Simulating finish_quiz)...")
    await db.clear_quiz_state(USER_ID)

    # 5. Verify Stats AFTER Clear
    user = await db.get_user(USER_ID)
    state = user.get("quiz_state")
    print(f"5. Final State: {state}")
    
    if not state:
        print("❌ FAILED: quiz_state is None! (Deleted everything)")
    elif "stats" not in state:
        print("❌ FAILED: 'stats' key missing in quiz_state!")
    elif state["stats"].get("questions_answered") != 10:
        val = state["stats"].get("questions_answered")
        print(f"❌ FAILED: questions_answered is {val}, expected 10.")
    else:
        print("✅ SUCCESS: Stats persisted through lifecycle!")

if __name__ == "__main__":
    asyncio.run(test_lifecycle())
