import os
import logging
from supabase import create_client, Client
from database.models import User

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Client = None

    async def connect(self):
        """
        Connects to Supabase.
        """
        try:
            if not self.url or not self.key:
                logger.error("Supabase credentials missing in .env")
                return False
                
            self.client = create_client(self.url, self.key)
            logger.info("Supabase connected successfully.")
            return True
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            return False

    async def upsert_user(self, user_data: dict) -> bool:
        """
        Inserts or updates a user in the 'users' table.
        """
        if not self.client:
            logger.warning("DB Client not initialized.")
            return False

        try:
            # Validate with Pydantic (Optional, ensuring types)
            # user = User(**user_data) 
            
            response = self.client.table('users').upsert(user_data).execute()
            logger.info(f"Upserted User: {user_data.get('user_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert user: {e}")
            return False

    async def get_user(self, user_id: int):
        """
        Fetches user data.
        """
        if not self.client: return None
        try:
            response = self.client.table('users').select("*").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    async def update_user_stats(self, user_id: int, is_correct: bool, time_taken: float) -> bool:
        """
        Updates user stats: Total Score, Questions Answered, Average Pace.
        Calculates a rolling average for pace.
        """
        if not self.client: return False
        
        try:
            # 1. Get current stats
            user = await self.get_user(user_id)
            if not user: return False
            
            # 2. Calculate new values
            # 2. Daily Reset Logic (Temporarily Disabled - Requires Schema Update)
            # We removed 'metadata' column usage because it likely caused the DB write to fail (Column does not exist).
            # TODO: User needs to add 'last_active_date' or 'metadata' column to Supabase 'users' table.
            
            # For now, we ACCUMULATE scores without reset to ensure points are saved.
            # current_inv = user.get("questions_answered", 0) or 0
            # current_score = user.get("current_streak", 0) or 0

            current_inv = user.get("questions_answered", 0) or 0
            current_score = user.get("current_streak", 0) or 0
                
            current_pace = user.get("average_pace", 0.0) or 0.0
            
            # Avoid division by zero
            if current_pace is None: current_pace = 0.0
            if current_inv is None: current_inv = 0
            
            # New Pace Formula
            new_inv = current_inv + 1
            new_pace = ((current_pace * current_inv) + time_taken) / new_inv
            
            # Score Update: 10 points per correct answer
            new_score = current_score + 10 if is_correct else current_score
            
            # 3. Update DB
            data = {
                "user_id": user_id,
                # "questions_answered": new_inv, # DISABLED: Column missing
                # "average_pace": round(new_pace, 2), # DISABLED: Column missing
                "current_streak": new_score
            }
            
            self.client.table('users').upsert(data).execute()
            logger.info(f"Updated Stats for {user_id}: Score={new_score} (Inv/Pace Ignored due to Schema)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
            return False

    async def save_quiz_state(self, user_id: int, state: dict) -> bool:
        """
        Saves the current quiz state (questions, index, score) to the DB.
        """
        if not self.client: return False
        try:
            # We explicitly update ONLY the quiz_state entry to avoid overwriting other fields if possible,
            # but upsert works on the whole row if we provide the PK.
            # State can be large, so ensure the column 'quiz_state' (JSONB) exists in Supabase.
            data = {
                "user_id": user_id,
                "quiz_state": state
            }
            self.client.table('users').upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save quiz state: {e}")
            return False

    async def get_quiz_state(self, user_id: int) -> dict:
        """
        Retrieves the active quiz state from the DB.
        """
        if not self.client: return None
        try:
            user = await self.get_user(user_id)
            if user and user.get("quiz_state"):
                return user["quiz_state"]
            return None
        except Exception as e:
            logger.error(f"Failed to get quiz state: {e}")
            return None

    async def clear_quiz_state(self, user_id: int):
        """
        Clears the quiz state (sets to Null).
        """
        if not self.client: return
        try:
            data = {
                "user_id": user_id,
                "quiz_state": None
            }
            self.client.table('users').upsert(data).execute()
        except Exception as e:
            logger.error(f"Failed to clear quiz state: {e}")
