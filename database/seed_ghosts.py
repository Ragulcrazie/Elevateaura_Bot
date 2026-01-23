import asyncio
import logging
import random
from dotenv import load_dotenv
from database.db_client import SupabaseClient

# Load env variables (to ensure DB connection works)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fake Data Source
INDIAN_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohan", "Kavita",
    "Suresh", "Pooja", "Arjun", "Divya", "Karan", "Meera", "Sanjay", "Riya",
    "Deepak", "Nisha", "Manish", "Swati", "Vivek", "Tanvi", "Alok", "Varsha"
]
SURNAMES = [
    "Sharma", "Verma", "Singh", "Patel", "Gupta", "Kumar", "Yadav", "Das",
    "Reddy", "Nair", "Mishra", "Joshi", "Chopra", "Malhotra", "Khan", "Jain"
]

def generate_ghost_name():
    return f"{random.choice(INDIAN_NAMES)} {random.choice(SURNAMES)}"

async def seed_ghosts(count=500):
    """
    Generates 'count' fake user profiles and inserts them into Supabase.
    """
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        logger.error("Could not connect to Supabase.")
        return

    logger.info(f"👻 Generating {count} ghost profiles...")
    
    ghosts_batch = []
    
    for _ in range(count):
        # Skill Level: Bell Curve centered around 1200 (Elo-like)
        # Min: 800 (Beginner), Max: 2000 (Expert)
        skill = int(random.gauss(1200, 200))
        skill = max(800, min(2000, skill))
        
        # Consistency: How varied their scores are (0.7 to 0.99)
        consistency = round(random.uniform(0.7, 0.99), 2)
        
        ghost = {
            "name": generate_ghost_name(),
            "base_skill_level": skill,
            "consistency_factor": consistency
        }
        ghosts_batch.append(ghost)

    # Insert in batches of 50 to avoid timeouts
    BATCH_SIZE = 50
    inserted_count = 0
    
    try:
        for i in range(0, len(ghosts_batch), BATCH_SIZE):
            batch = ghosts_batch[i : i + BATCH_SIZE]
            # Supabase insert
            response = db.client.table("ghost_profiles").insert(batch).execute()
            inserted_count += len(batch)
            logger.info(f"✅ Inserted batch {i//BATCH_SIZE + 1} ({len(batch)} ghosts)")
            
        logger.info(f"🎉 Successfully seeded {inserted_count} ghosts!")
        
    except Exception as e:
        logger.error(f"Failed to insert ghosts: {e}")

if __name__ == "__main__":
    asyncio.run(seed_ghosts())
