import logging
from typing import Dict, Any, Optional
from database.db_client import SupabaseClient

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages quiz sessions via Supabase Database (Cloud Persistence).
    """
    def __init__(self):
        # We don't maintain local cache to ensure cloud consistency
        pass

    async def save_session(self, user_id: int, data: Dict[str, Any]):
        """Saves current session to Supabase."""
        try:
            db = SupabaseClient()
            await db.connect()
            success = await db.save_quiz_state(user_id, data)
            if not success:
               logger.error(f"Failed to save session to DB for {user_id}")
        except Exception as e:
            logger.error(f"DB Save Error: {e}")

    async def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves session from Supabase."""
        try:
            db = SupabaseClient()
            await db.connect()
            return await db.get_quiz_state(user_id)
        except Exception as e:
             logger.error(f"DB Get Error: {e}")
             return None

    async def delete_session(self, user_id: int, keep_stats: Dict[str, Any] = None):
        """Deletes session from Supabase, preserving stats if provided."""
        try:
            db = SupabaseClient()
            await db.connect()
            await db.clear_quiz_state(user_id, keep_stats)
        except Exception as e:
            logger.error(f"DB Delete Error: {e}")

# Singleton Instance
session_manager = SessionManager()
