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

    def get_ist_date(self):
        """Returns current date in IST as string YYYY-MM-DD"""
        from datetime import datetime, timedelta, timezone
        # Simple IST offset calculation (UTC+5:30) without external deps if possible
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(ist_offset).strftime("%Y-%m-%d")

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

    async def update_user_stats(self, user_id: int, is_correct: bool, time_taken: float, forced_count: int = None, mistake_topic: str = None) -> bool:
        """
        Updates user stats.
        If forced_count is provided, uses that directly.
        If mistake_topic is provided (on wrong answer), updates weak_spots.
        """
        if not self.client: return False
        
        try:
            # 1. Get current stats
            user = await self.get_user(user_id)
            if not user: return False
            
            # --- JSONB STORAGE LOGIC ---
            today_str = self.get_ist_date()
            
            quiz_state = user.get("quiz_state") or {}
            saved_stats = quiz_state.get("stats", {})
            last_active = saved_stats.get("last_active_date")
            
            # DAILY RESET CHECK
            if last_active != today_str:
                logger.info(f"Daily Reset for {user_id}: New Day ({today_str})")
                current_inv = 0
                current_pace = 0.0 
                current_daily_score = 0
                weak_spots = {} # Reset weak spots daily
            else:
                current_inv = saved_stats.get("questions_answered", 0)
                current_pace = saved_stats.get("average_pace", 0.0)
                current_daily_score = saved_stats.get("daily_score", 0)
                weak_spots = saved_stats.get("weak_spots", {})
            
            # Score accumulates forever
            current_score = user.get("current_streak", 0) or 0

            # 2. Calculate New Values
            if forced_count is not None:
                new_inv = forced_count
            else:
                new_inv = current_inv + 1
            
            # Rolling Average Pace
            if new_inv == 1:
                new_pace = time_taken
            else:
                new_pace = ((current_pace * current_inv) + time_taken) / new_inv
            
            # Score Update
            new_score = current_score + 10 if is_correct else current_score
            new_daily_score = current_daily_score + 10 if is_correct else current_daily_score
            
            # Weak Spot Tracking (Legacy Logic - Only if Wrong)
            # The calling code now passes 'topic_context' as mistake_topic.
            # We need to differentiating: Is it a generic category (Correct) or specific topic (Wrong)?
            # Actually, simply: If !is_correct, add to weak_spots.
            
            topic_key = (mistake_topic or "General").strip()
            
            if not is_correct:
                 weak_spots[topic_key] = weak_spots.get(topic_key, 0) + 1

            # --- LIFETIME STATS (Premium Categories) ---
            metadata = user.get("metadata", {}) or {}
            lifetime_stats = metadata.get("lifetime_stats", {})
            
            # Determine Main Category from topic_key for aggregation
            # Determine Main Category from topic_key for aggregation
            # We map specific topics or domain strings to 3 Main Buckets
            cat_lower = topic_key.lower()
            main_bucket = "other"
            
            # --- ROBUST BUCKETING LOGIC ---
            if any(x in cat_lower for x in ["aptitude", "math", "quant", "data interpretation"]):
                main_bucket = "aptitude"
            elif any(x in cat_lower for x in ["reasoning", "logic", "english", "verbal"]):
                main_bucket = "reasoning"
            elif any(x in cat_lower for x in ["gk", "knowledge", "science", "history", "polity", "geography", "economy", "current affairs", "general"]):
                main_bucket = "gk"
            
            # Update Total/Correct for this Bucket
            # Structure: lifetime_stats = { "aptitude": {"total": 10, "correct": 8}, ... }
            
            if main_bucket not in lifetime_stats:
                lifetime_stats[main_bucket] = {"total": 0, "correct": 0}
            
            lifetime_stats[main_bucket]["total"] += 1
            if is_correct:
                lifetime_stats[main_bucket]["correct"] += 1
            
            # Also keep Global Total
            lifetime_stats["global_total"] = lifetime_stats.get("global_total", 0) + 1
            
            metadata["lifetime_stats"] = lifetime_stats

            # 3. Update DB
            quiz_state["stats"] = {
                "questions_answered": new_inv,
                "average_pace": round(new_pace, 2),
                "last_active_date": today_str,
                "daily_score": new_daily_score,
                "weak_spots": weak_spots
            }
            
            data = {
                "user_id": user_id,
                "current_streak": new_score,
                "quiz_state": quiz_state,
                "metadata": metadata
            }
            
            self.client.table('users').upsert(data).execute()
            logger.info(f"Stats Updated {user_id}: Score={new_score}, Bucket={main_bucket}")
            return quiz_state["stats"]
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
            return None

    async def save_quiz_state(self, user_id: int, state: dict) -> bool:
        """
        Saves the current quiz state (questions, index, score) to the DB.
        """
        if not self.client: return False
        try:
            # Fetch existing to preserve other keys (like 'stats')
            user = await self.get_user(user_id)
            current_data = user.get("quiz_state") or {} if user else {}
            
            # Merge new state into existing data
            current_data.update(state)
            
            data = {
                "user_id": user_id,
                "quiz_state": current_data
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

    async def clear_quiz_state(self, user_id: int, keep_stats: dict = None):
        """
        Clears the quiz state but PRESERVES stats.
        If keep_stats is provided, uses that instead of DB read (prevent stale reads).
        """
        if not self.client: return
        try:
            # 1. Use provided stats (Best for consistency)
            new_stats = {}
            if keep_stats:
                 new_stats["stats"] = keep_stats
            else:
                # 2. Fallback to DB fetch (Only if we don't have local copy)
                user = await self.get_user(user_id)
                existing_state = user.get("quiz_state") or {} if user else {}
                if "stats" in existing_state:
                    new_stats["stats"] = existing_state["stats"]
                
            data = {
                "user_id": user_id,
                "quiz_state": new_stats
            }
            self.client.table('users').upsert(data).execute()
        except Exception as e:
            logger.error(f"Failed to clear quiz state: {e}")

    async def reset_user_limit(self, user_id: int):
        """
        ADMIN TOOL: Resets a user's daily limit (sets questions_answered to 0).
        """
        if not self.client: return False
        try:
            user = await self.get_user(user_id)
            if not user: return False
            
            quiz_state = user.get("quiz_state") or {}
            # Preserve existing stats but zero out the counter
            if "stats" not in quiz_state: quiz_state["stats"] = {}
            quiz_state["stats"]["questions_answered"] = 0
            
            data = {
                "user_id": user_id,
                "quiz_state": quiz_state
            }
            self.client.table('users').upsert(data).execute()
            logger.info(f"ADMIN RESET for {user_id}: Limit cleared.")
            return True
        except Exception as e:
            logger.error(f"Failed to reset user limit: {e}")
            return False
