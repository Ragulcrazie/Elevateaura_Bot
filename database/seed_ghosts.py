import asyncio
import logging
import random
from dotenv import load_dotenv
from database.db_client import SupabaseClient

# Load env variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MASSIVE DATASETS FOR REALISM ---

MALE_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharva", "Dhruv", "Kabir", "Riyan", "Aryan", "Advik", "Kartik", "Shiv", "Rudra",
    "Ayush", "Vedant", "Om", "Aadi", "Sarthak", "Pranav", "Darsh", "Angad", "Ritesh", "Harsh",
    "Yash", "Kunal", "Rahul", "Rohit", "Amit", "Sumit", "Vikas", "Manish", "Sandeep", "Deepak",
    "Ajay", "Vijay", "Suresh", "Ramesh", "Manoj", "Anil", "Sunil", "Prakash", "Raj", "Raju",
    "Nikhil", "Gaurav", "Abhishek", "Rajat", "Akash", "Ankit", "Varun", "Tarun", "Siddharth", "Mayank",
    "Chirag", "Jatin", "Lalit", "Pankaj", "Bhavesh", "Chetan", "Tushar", "Nitin", "Prateek", "Mohit",
    "Gautam", "Kamal", "Naveen", "Sachin", "Saurabh", "Vishal", "Vivek", "Yogesh", "Alok", "Ankur",
    "Ashish", "Bipul", "Chandan", "Dinesh", "Ganesh", "Hemant", "Himanshu", "Jagdish", "Kailash", "Lakshay",
    "Madhav", "Mukesh", "Narendra", "Pawan", "Pradeep", "Praveen", "Rajeev", "Rakesh", "Ranjan", "Ravi",
    "Rishabh", "Rohan", "Samir", "Sanju", "Shubham", "Sonu", "Subhash", "Suraj", "Umesh", "Vinay", "Zain", "Rehan", "Bilal", "Adil"
]

FEMALE_NAMES = [
    "Aadhya", "Diya", "Saanvi", "Aram", "Ananya", "Pari", "Riya", "Pihu", "Myra", "Trisha",
    "Kiara", "Siya", "Prisha", "Anvi", "Aarohi", "Vanshika", "Jiya", "Sneha", "Isha", "Kavya",
    "Avni", "Zara", "Alya", "Khushi", "Angel", "Mahi", "Navya", "Sarah", "Tanya", "Veda",
    "Pooja", "Neha", "Priya", "Divya", "Anjali", "Swati", "Komal", "Megha", "Ritika", "Simran",
    "Nisha", "Rani", "Sushma", "Rekha", "Suman", "Sunita", "Anita", "Geeta", "Seema", "Reena",
    "Meena", "Kiran", "Jyoti", "Aarti", "Shweta", "Sakshi", "Pallavi", "Nidhi", "Ritu", "Monika",
    "Deepika", "Priyanka", "Shruti", "Akanksha", "Garima", "Shivani", "Sonali", "Tanvi", "Vani", "Vidya",
    "Esha", "Heena", "Kajal", "Kritika", "Latika", "Mansi", "Natasha", "Parul", "Radha", "Rashmi",
    "Richa", "Sania", "Sapna", "Shikha", "Shilpa", "Smriti", "Sonal", "Srishti", "Surbhi", "Tania",
    "Vaishnavi", "Vandana", "Varsha", "Yamini", "Zoya", "Ayesha", "Fatima", "Sana"
]

SURNAMES = [
    "Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Kumar", "Yadav", "Patel", "Mishra", "Joshi",
    "Reddy", "Nair", "Iyer", "Rao", "Gowda", "Pillai", "Menon", "Jain", "Agarwal", "Bansal",
    "Mehta", "Shah", "Parekh", "Desai", "Jadhav", "Patil", "Kulkarni", "Deshmukh", "Chavan", "Pawar",
    "Das", "Dutta", "Bose", "Ghosh", "Chatterjee", "Banerjee", "Mukherjee", "Roy", "Sarkar", "Sen",
    "Khan", "Pathan", "Sheikh", "Ansari", "Siddiqui", "Qureshi", "Mirza", "Baig", "Syed", "Ali",
    "Chopra", "Kapoor", "Khanna", "Bhatia", "Saxena", "Kaushik", "Tiwari", "Dubey", "Pandey", "Tripathi",
    "Chaudhary", "Jha", "Thakur", "Rana", "Biswas", "Nayak", "Sahu", "Swain", "Mohanty", "Acharya",
    "Bhat", "Hegde", "Shetty", "Kamath", "Prabhu", "Naik", "Shenoy", "Pai", "Kudva", "Rai",
    "Garg", "Goel", "Mittal", "Singhal", "Jindal", "Lohia", "Bajaj", "Birla", "Ambani", "Adani"
]

TELEGRAM_MOODS = [
    "Official", "King", "Queen", "Cool", "Rock", "Star", "Lover", "Boy", "Girl", "Tech",
    "Coder", "Gamer", "Vibes", "X", "Pro", "Max", "Zone", "World", "India", "007"
]

def generate_random_name():
    """
    Generates a name with high variance in style:
    - First Last (60%)
    - First only (10%)
    - Telegram Handle Style (10%)
    - First + Initial (10%)
    - Lowercase style (10%)
    """
    is_female = random.random() < 0.45 # 45% female representation
    first_list = FEMALE_NAMES if is_female else MALE_NAMES
    
    first = random.choice(first_list)
    last = random.choice(SURNAMES)
    
    style_roll = random.random()
    
    if style_roll < 0.60:
        # Standard: Rahul Sharma
        return f"{first} {last}"
    
    elif style_roll < 0.70:
        # First name only: Rahul
        return first
        
    elif style_roll < 0.80:
        # Handle style / Number suffix: rahul_123, Rahul07
        suffix = random.choice(["", "_", "."])
        num = random.randint(1, 999) if random.random() < 0.5 else ""
        base = f"{first}{suffix}{last}" if random.random() < 0.5 else f"{first}{suffix}"
        name = f"{base}{num}"
        return name.lower() if random.random() < 0.5 else name
        
    elif style_roll < 0.90:
        # First + Initial: Rahul S.
        return f"{first} {last[0]}."
        
    else:
        # Trendy / Mood: Rahul King, Cool Priya
        mood = random.choice(TELEGRAM_MOODS)
        if random.random() < 0.5:
             return f"{first} {mood}"
        else:
             return f"{mood} {first}"

async def seed_ghosts(count=10000):
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        logger.error("Could not connect to Supabase.")
        return

    logger.info(f"👻 Generating {count} ULTRA-REALISTIC ghost profiles...")
    
    ghosts_batch = []
    
    for _ in range(count):
        # Skill Level: Bell Curve centered around 1100 (Slightly above average)
        # Min: 600, Max: 2200
        skill = int(random.gauss(1100, 250))
        skill = max(600, min(2200, skill))
        
        # Consistency: 60% are very consistent, 40% are erratic
        if random.random() < 0.6:
            consistency = round(random.uniform(0.85, 0.98), 2)
        else:
            consistency = round(random.uniform(0.50, 0.85), 2)
        
        ghost = {
            "name": generate_random_name(),
            "base_skill_level": skill,
            "consistency_factor": consistency,
            # Resetting counts to 0 so they can start fresh logic if needed, 
            # or pre-fill them to look like they've been playing a while is also an option.
            # But usually ghost logic runs daily updates. Let's keep them clean or leave as per schema defaults.
        }
        ghosts_batch.append(ghost)

    # Insert in batches
    BATCH_SIZE = 100 
    inserted_count = 0
    
    try:
        # Split into chunks
        for i in range(0, len(ghosts_batch), BATCH_SIZE):
            batch = ghosts_batch[i : i + BATCH_SIZE]
            
            # Using upsert requires a unique constraint usually, or just insert.
            # `ghost_profiles` likely uses `id` as PK serial.
            response = db.client.table("ghost_profiles").insert(batch).execute()
            
            inserted_count += len(batch)
            if inserted_count % 1000 == 0:
                logger.info(f"✅ Progress: {inserted_count}/{count} ghosts seeded...")
            
        logger.info(f"🎉 SUCCESS! Total {inserted_count} ghosts added to the ecosystem.")
        
    except Exception as e:
        logger.error(f"Failed during insertion loop: {e}")

if __name__ == "__main__":
    asyncio.run(seed_ghosts(10000))
