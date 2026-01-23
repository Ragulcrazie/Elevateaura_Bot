from aiogram import Router, types, F
from aiogram.types import Message
import json
import logging
from database.db_client import SupabaseClient

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """
    Handles data sent from the Mini App (e.g., Payment Success).
    """
    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"Web App Data received: {data}")
        
        if data.get("action") == "subscribe_pro":
            user_id = message.from_user.id
            
            # 1. Update DB to 'pro_99'
            db = SupabaseClient()
            await db.connect()
            
            # Using raw SQL or client update since we don't have a specific update method yet
            # For MVP, we'll re-use upsert or create a new method. 
            # Let's just assume upsert works for now with partial data if we had it, 
            # but safest is to fetch and update.
            # actually db_client.upsert_user handles it.
            
            user_data = {
                "user_id": user_id,
                "subscription_status": "pro_99",
                "full_name": message.from_user.full_name # Required field in our current logic
            }
            await db.upsert_user(user_data)
            
            await message.answer(
                "🎉 **PAYMENT SUCCESSFUL!**\n\n"
                "👑 **You are now a PRO Member.**\n"
                "✅ Unlimited Quizzes\n"
                "✅ Detailed Analytics\n"
                "✅ 'Competitor Intelligence' Unlocked\n\n"
                "Type /quiz to test your new powers!",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Failed to handle web app data: {e}")
