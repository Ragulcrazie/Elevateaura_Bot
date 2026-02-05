
import logging
from database.db_client import SupabaseClient
from aiogram import Bot

logger = logging.getLogger(__name__)

async def process_referral_reward(bot: Bot, user_id: int):
    """
    Called when user_id activates PREMIUM.
    Checks if they were referred, giving +50 Stars to referrer.
    """
    db = SupabaseClient()
    await db.connect()
    
    try:
        # 1. Get User to find 'referred_by'
        user = await db.get_user(user_id)
        if not user: return
        
        referrer_id = user.get("referred_by")
        if not referrer_id: return # No referrer
        
        # 2. Check if already rewarded (Idempotency)
        # We use metadata to track if we paid for this referral
        metadata = user.get("metadata", {}) or {}
        if metadata.get("referral_paid", False):
            return
            
        # 3. Credit Referrer
        referrer = await db.get_user(referrer_id)
        if referrer:
            current_stars = referrer.get("wallet_stars", 0) or 0
            new_balance = current_stars + 50
            
            await db.upsert_user({
                "user_id": referrer_id,
                "wallet_stars": new_balance
            })
            
            # 4. Notify Referrer
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎉 **REFERRAL BONUS!**\n\n"
                    f"Your friend just activated Premium!\n"
                    f"💰 **+50 Stars** added to your wallet.\n"
                    f"🏦 New Balance: {new_balance} Stars\n\n"
                    "Invite more friends to earn Free Premium!"
                )
            except Exception as e:
                logger.warning(f"Failed to notify referrer {referrer_id}: {e}")
                
        # 5. Mark as Paid in User's metadata
        metadata["referral_paid"] = True
        await db.upsert_user({
            "user_id": user_id,
            "metadata": metadata
        })
        
        logger.info(f"Referral Success: {referrer_id} earned 50 stars via {user_id}")
        
    except Exception as e:
        logger.error(f"Referral Error: {e}")
