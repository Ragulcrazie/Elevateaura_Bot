"""
Weekly Reward System - Announces winners 2 hours before weekly reset
and displays ₹600 earnings (virtual bonus credits) to convert free users.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database.db_client import SupabaseClient

logger = logging.getLogger(__name__)

async def announce_weekly_winners(bot: Bot):
    """
    Called 2 hours before weekly reset (Sunday 10 PM IST).
    Announces top 3 winners with ₹600 bonus credits display.
    """
    db = SupabaseClient()
    await db.connect()
    
    # Get top 1 weekly scorer (winner-takes-all)
    top_winners = await db.get_weekly_leaderboard(limit=1)
    
    if not top_winners or len(top_winners) == 0:
        logger.info("No weekly winner to announce")
        return
    
    # Single winner announcement
    winner = top_winners[0]
    winner_name = winner.get('first_name', 'Champion')
    score = winner.get('weekly_score', 0)
    user_id = winner.get('user_id')
    
    winner_msg = (
        "🏆 **WEEKLY WINNER ANNOUNCEMENT!**\n\n"
        "⏰ Competition ends in 2 hours\n\n"
        f"🥇 **CHAMPION: {winner_name}**\n"
        f"├─ Final Score: {score} pts\n"
        f"├─ Prize: ₹600 Bonus Credits\n"
        f"└─ Bonus: 90 Days Premium FREE\n\n"
        "Next week's race starts Monday 12 AM!"
    )
    
    # Send personal congratulations to winner
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 **CONGRATULATIONS - YOU WON!**\n\n"
                "You are this week's #1 Champion!\n\n"
                "💎 **Your Rewards:**\n"
                "├─ ₹600 Bonus Credits\n"
                "└─ 90 Days Premium Access\n\n"
                "Rewards will be credited to your account after weekly reset (tonight 12 AM).\n\n"
                "*Bonus credits can be redeemed for Premium subscription only. No cash withdrawal.*"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send winner message to {user_id}: {e}")
    
    # Broadcast to all active users (optional - for FOMO effect)
    # For now, just log it
    logger.info(f"Weekly winners announced: {winner_msg}")
    
    # You can optionally send to a broadcast channel if you have one
    return winner_msg

async def credit_weekly_rewards(bot: Bot):
    """
    Called at weekly reset (Monday 12 AM IST).
    Credits the virtual bonus to winner's wallet.
    """
    db = SupabaseClient()
    await db.connect()
    
    # Get #1 winner only
    top_winners = await db.get_weekly_leaderboard(limit=1)
    
    if not top_winners or len(top_winners) == 0:
        logger.info("No winner to credit")
        return
    
    winner = top_winners[0]
    user_id = winner.get('user_id')
    bonus = 600  # ₹600 Bonus credits for #1
    days = 90    # 90 days of premium
    
    try:
        # Get current wallet
        user = await db.get_user(user_id)
        if not user:
            return
        
        current_wallet = user.get('wallet_stars', 0) or 0
        new_wallet = current_wallet + bonus
        
        from datetime import datetime, timedelta
        expiry_date = (datetime.utcnow() + timedelta(days=days)).isoformat()

        # Update wallet and upgrade to premium with expiration
        await db.upsert_user({
            "user_id": user_id,
            "wallet_stars": new_wallet,
            "subscription_status": "premium",
            "subscription_expires_at": expiry_date,
            "last_payment_date": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Credited ₹{bonus} to winner {user_id}")
        
        # Send confirmation
        await bot.send_message(
            chat_id=user_id,
            text=(
                "✅ **REWARDS CREDITED!**\n\n"
                f"💰 Wallet Balance: ₹{new_wallet}\n"
                f"👑 Premium Status: Active ({days} days)\n\n"
                "Ready to defend your title this week?"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to credit rewards to {user_id}: {e}")

async def start_weekly_scheduler(bot: Bot):
    """
    Background task that runs weekly announcements and resets.
    Call this in main.py on bot startup.
    """
    while True:
        try:
            now = datetime.now()
            
            # Check if it's Sunday 10 PM IST (2 hours before reset)
            if now.weekday() == 6 and now.hour == 22:  # Sunday 
                await announce_weekly_winners(bot)
                # Sleep for 2 hours until reset
                await asyncio.sleep(7200)
            
            # Check if it's Monday 12 AM IST (reset time)
            if now.weekday() == 0 and now.hour == 0:  # Monday midnight
                await credit_weekly_rewards(bot)
                # Sleep for 1 hour to avoid re-triggering
                await asyncio.sleep(3600)
            
            # Check every 30 minutes
            await asyncio.sleep(1800)
            
        except Exception as e:
            logger.error(f"Weekly scheduler error: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour on error
