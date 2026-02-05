"""
Subscription Notification Scheduler
Runs periodic checks for expiration warnings every 6 hours
"""

import asyncio
import logging
from aiogram import Bot
from bot.handlers.subscription_notifications import check_and_notify_expirations

logger = logging.getLogger(__name__)

async def start_subscription_notification_scheduler(bot: Bot):
    """Start the subscription notification scheduler"""
    
    logger.info("🔔 Subscription notification scheduler started")
    
    while True:
        try:
            # Run expiration check
            await check_and_notify_expirations(bot)
            
            # Wait 6 hours before next check
            await asyncio.sleep(6 * 3600)  # 6 hours
            
        except Exception as e:
            logger.error(f"Subscription scheduler error: {e}")
            # Wait 1 hour before retry on error
            await asyncio.sleep(3600)
