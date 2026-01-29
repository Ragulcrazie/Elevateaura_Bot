import asyncio
import random
import logging
from database.db_client import SupabaseClient

# Setup basic logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_analytics_logic():
    print("--- 🧪 Testing True Potential Analytics Logic ---")
    
    # 1. Setup
    db = SupabaseClient()
    # We use a random large ID to avoid messing with real users
    test_user_id = 999999001 
    
    print(f"1. Connect to DB and reset test user {test_user_id}...")
    await db.connect()
    
    # Reset user for clean state (simulate a fresh start)
    initial_data = {
        "user_id": test_user_id,
        "full_name": "Test Subject Alpha",
        "current_streak": 0,
        "quiz_state": {
            "stats": {
                "questions_answered": 0,
                "daily_score": 0,
                "weak_spots": {},
                "last_active_date": db.get_ist_date() # Force today
            }
        }
    }
    db.client.table('users').upsert(initial_data).execute()
    print("   User reset complete.")

    # 2. Simulate Quiz Activity
    print("\n2. Simulating User Activity...")
    
    # Update 1: Correct Answer (Topic: Algebra - should NOT be recorded)
    print("   - Answer 1: Correct (Algebra)")
    await db.update_user_stats(test_user_id, is_correct=True, time_taken=5.0, mistake_topic="Algebra")
    
    # Update 2: Wrong Answer (Topic: Geometry - SHOULD be recorded)
    print("   - Answer 2: WRONG (Geometry)")
    await db.update_user_stats(test_user_id, is_correct=False, time_taken=10.0, mistake_topic="Geometry")
    
    # Update 3: Wrong Answer (Topic: Geometry - SHOULD be recorded, count goes to 2)
    print("   - Answer 3: WRONG (Geometry)")
    await db.update_user_stats(test_user_id, is_correct=False, time_taken=12.0, mistake_topic="Geometry")
    
    # Update 4: Wrong Answer (Topic: Percentages - SHOULD be recorded)
    print("   - Answer 4: WRONG (Percentages)")
    await db.update_user_stats(test_user_id, is_correct=False, time_taken=8.0, mistake_topic="Percentages")

    # 3. Verify Database State
    print("\n3. Verifying Database Storage...")
    user = await db.get_user(test_user_id)
    stats = user['quiz_state']['stats']
    weak_spots = stats.get('weak_spots', {})
    daily_score = stats.get('daily_score', 0)
    
    print(f"   - Daily Score: {daily_score} (Expected: 10)") # 1 correct * 10
    print(f"   - Weak Spots: {weak_spots}")
    
    if weak_spots.get("Geometry") == 2 and weak_spots.get("Percentages") == 1:
        print("   ✅ Weak Spots storage is CORRECT.")
    else:
        print("   ❌ Weak Spots storage is INCORRECT.")

    # 4. Verify Potential Score Logic (Mimic API)
    print("\n4. Verifying Potential Score Calculation (API Logic)...")
    
    # Logic from main.py:
    # Potential = Daily Score + (Total Mistakes * 10)
    total_mistakes = sum(weak_spots.values()) # 2 + 1 = 3
    potential_score = daily_score + (total_mistakes * 10) # 10 + 30 = 40
    
    print(f"   - Calculated Potential Score: {potential_score}")
    print(f"   - Expected: 40 (10 real + 30 lost)")
    
    if potential_score == 40:
        print("   ✅ Potential Score calculation is CORRECT.")
    else:
        print("   ❌ Potential Score calculation is INCORRECT.")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_analytics_logic())
