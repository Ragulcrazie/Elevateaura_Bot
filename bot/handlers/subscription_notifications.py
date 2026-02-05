"""
Subscription Expiration Notification Handler
Sends 24-hour warning messages to users about to lose premium
"""

import logging
import asyncio
from datetime import datetime
from aiogram import Bot
from database.db_client import SupabaseClient
from bot.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

async def check_and_notify_expirations(bot: Bot):
    """
    Check all premium users and send 24-hour expiration warnings.
    This should be called periodically (e.g., every 6 hours).
    """
    
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        logger.error("DB connection failed for expiration notifications")
        return
    
    try:
        # Get all premium users
        result = db.client.from_("users").select(
            "user_id, subscription_expires_at, expiration_warning_sent"
        ).eq("subscription_status", "premium").execute()
        
        if not result.data:
            logger.info("No premium users found")
            return
        
        sub_service = SubscriptionService()
        notifications_sent = 0
        
        for user in result.data:
            user_id = user.get('user_id')
            
            try:
                # Check if warning should be sent
                should_warn = await sub_service.should_send_expiration_warning(user_id)
                
                if should_warn:
                    await send_expiration_warning(bot, user_id, user.get('subscription_expires_at'))
                    notifications_sent += 1
                    await asyncio.sleep(1)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Warning notification failed for {user_id}: {e}")
        
        logger.info(f"Sent {notifications_sent} expiration warnings")
        
    except Exception as e:
        logger.error(f"Expiration check failed: {e}")

async def send_expiration_warning(bot: Bot, user_id: int, expires_at: str):
    """Send 24-hour expiration warning to user"""
    
    try:
        expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        expiry_date = expires_dt.strftime("%d %b, %I:%M %p")
        
        message = (
            "⏰ **PREMIUM EXPIRING SOON!**\n\n"
            f"Your premium access expires on **{expiry_date}** (tomorrow).\n\n"
            "**What You'll Lose:**\n"
            "❌ Ad-free experience\n"
            "❌ Full weak topic names\n"
            "❌ AI Coach access\n"
            "❌ Premium analytics\n\n"
            "**Renew Now for 99 ⭐**\n"
            "Keep your competitive advantage!\n\n"
            "👉 Tap /upgrade to renew\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🇮🇳 **हिंदी में जानकारी**\n\n"
            "⏰ **PREMIUM खत्म होने वाला है!**\n\n"
            f"आपका premium **{expiry_date}** को खत्म हो जाएगा।\n\n"
            "**क्या खो देंगे:**\n"
            "❌ बिना ads का अनुभव\n"
            "❌ पूरे weak topics\n"
            "❌ AI Coach\n"
            "❌ Premium analytics\n\n"
            "**99 ⭐ में renew करें**\n\n"
            "👉 /upgrade दबाएं\n"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"✅ Expiration warning sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send warning to {user_id}: {e}")

async def send_expired_notification(bot: Bot, user_id: int):
    """
    Send notification when premium has expired.
    This gets called by the subscription service when expiration is detected.
    """
    
    try:
        message = (
            "⛔ **PREMIUM EXPIRED**\n\n"
            "Your premium subscription has ended.\n\n"
            "**Back to Free Tier:**\n"
            "• Ads are now showing\n"
            "• Weak topics are locked\n"
            "• AI Coach unavailable\n\n"
            "**Renew for 99 ⭐**\n"
            "Get back your ad-free experience!\n\n"
            "👉 Tap /upgrade to renew\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🇮🇳 **हिंदी में**\n\n"
            "⛔ **PREMIUM खत्म हो गया**\n\n"
            "आपकी premium membership समाप्त हो गई।\n\n"
            "**Free tier में:**\n"
            "• Ads दिखेंगे\n"
            "• Weak topics लॉक हैं\n"
            "• AI Coach बंद\n\n"
            "**99 ⭐ में फिर से activate करें**\n\n"
            "👉 /upgrade दबाएं\n"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"✅ Expiration notification sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send expiration notification to {user_id}: {e}")
