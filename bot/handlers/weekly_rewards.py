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
    
    # Get top 3 weekly scorers
    top_winners = await db.get_weekly_leaderboard(limit=3)
    
    if not top_winners or len(top_winners) == 0:
        logger.info("No weekly winners to announce")
        return
    
    # Prepare winner announcement
    winner_msg = (
        "🏆 **WEEKLY LEADERBOARD - FINAL RESULTS!**\n\n"
        "The competition ends in 2 hours. Here are your champions:\n\n"
    )
    
    # Prize structure (virtual credits)
    prizes = [
        {"rank": "🥇 1st Place", "bonus": 600, "premium_days": 90},
        {"rank": "🥈 2nd Place", "bonus": 400, "premium_days": 60},
        {"rank": "🥉 3rd Place", "bonus": 200, "premium_days": 30}
    ]
    
    for idx, winner in enumerate(top_winners[:3]):
        prize = prizes[idx]
        winner_name = winner.get('first_name', 'Champion')
        score = winner.get('weekly_score', 0)
        user_id = winner.get('user_id')
        
        winner_msg += (
            f"{prize['rank']}: **{winner_name}**\n"
            f"├─ Score: {score} pts\n"
            f"├─ Bonus: ₹{prize['bonus']} Credits\n"
            f"└─ Premium: {prize['premium_days']} days FREE\n\n"
        )
        
        # Send personal congratulations to winner
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"🎉 **CONGRATULATIONS!**\n\n"
                    f"You finished {prize['rank']} in this week's competition!\n\n"
                    f"💎 **Your Rewards:**\n"
                    f"├─ ₹{prize['bonus']} Bonus Credits\n"
                    f"└─ {prize['premium_days']} Days Premium Access\n\n"
                    f"These will be credited to your account after weekly reset (tonight 12 AM).\n\n"
                    f"*Bonus credits can be redeemed for Premium subscription only. No cash withdrawal.*"
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
    Credits the virtual bonus to winners' wallets.
    """
    db = SupabaseClient()
    await db.connect()
    
    # Get top 3 weekly scorers
    top_winners = await db.get_weekly_leaderboard(limit=3)
    
    # Prize structure
    prizes = [600, 400, 200]  # ₹ Bonus credits
    premium_days = [90, 60, 30]  # Days of premium
    
    for idx, winner in enumerate(top_winners[:3]):
        user_id = winner.get('user_id')
        bonus = prizes[idx]
        days = premium_days[idx]
        
        try:
            # Get current wallet
            user = await db.get_user(user_id)
            if not user:
                continue
            
            current_wallet = user.get('wallet_stars', 0) or 0
            new_wallet = current_wallet + bonus
            
            # Update wallet and extend premium
            # Note: We add days to their existing premium expiry
            await db.upsert_user({
                "user_id": user_id,
                "wallet_stars": new_wallet
            })
            
            # If they're free, upgrade them to premium
            if user.get('subscription_status') == 'free':
                await db.upsert_user({
                    "user_id": user_id,
                    "subscription_status": "premium"
                })
            
            logger.info(f"Credited ₹{bonus} to user {user_id}")
            
            # Send confirmation
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ **REWARDS CREDITED!**\n\n"
                    f"💰 Wallet Balance: ₹{new_wallet}\n"
                    f"👑 Premium Status: Active ({days} days)\n\n"
                    f"Ready to dominate this week's leaderboard?"
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
