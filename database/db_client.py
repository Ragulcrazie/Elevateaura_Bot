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
