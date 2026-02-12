"""
Weekly Reward System - Top 10 Prize Split
Total Pool: ₹600 distributed across Top 10 weekly performers.

Prize Structure:
  Rank 1:  ₹200
  Rank 2:  ₹120
  Rank 3:  ₹80
  Rank 4:  ₹50
  Rank 5:  ₹40
  Rank 6:  ₹30
  Rank 7:  ₹30
  Rank 8:  ₹20
  Rank 9:  ₹15
  Rank 10: ₹15
"""
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database.db_client import SupabaseClient

logger = logging.getLogger(__name__)

# --- PRIZE CONFIGURATION ---
WEEKLY_PRIZES = {
    1: {"amount": 200, "emoji": "🥇", "label": "Champion"},
    2: {"amount": 120, "emoji": "🥈", "label": "Runner-Up"},
    3: {"amount": 80,  "emoji": "🥉", "label": "Podium Finisher"},
    4: {"amount": 50,  "emoji": "4️⃣", "label": "Elite"},
    5: {"amount": 40,  "emoji": "5️⃣", "label": "Elite"},
    6: {"amount": 30,  "emoji": "6️⃣", "label": "Top Performer"},
    7: {"amount": 30,  "emoji": "7️⃣", "label": "Top Performer"},
    8: {"amount": 20,  "emoji": "8️⃣", "label": "Rising Star"},
    9: {"amount": 15,  "emoji": "9️⃣", "label": "Rising Star"},
    10: {"amount": 15, "emoji": "🔟", "label": "Rising Star"},
}

PREMIUM_DAYS_RANK1 = 90  # Only Rank 1 gets premium


async def announce_weekly_winners(bot: Bot):
    """
    Called 2 hours before weekly reset (Sunday 10 PM IST).
    Announces top 10 winners with their prizes.
    """
    db = SupabaseClient()
    await db.connect()
    
    # Get top 10 weekly scorers
    top_winners = await db.get_weekly_leaderboard(limit=10)
    
    if not top_winners or len(top_winners) == 0:
        logger.info("No weekly winners to announce")
        return
    
    # Build leaderboard announcement
    leaderboard_lines = []
    for i, winner in enumerate(top_winners):
        rank = i + 1
        if rank > 10:
            break
        prize_info = WEEKLY_PRIZES.get(rank)
        if not prize_info:
            break
        
        name = winner.get('first_name', 'Aspirant')
        score = winner.get('weekly_score', 0)
        leaderboard_lines.append(
            f"{prize_info['emoji']} **{name}** — {score} pts → ₹{prize_info['amount']}"
        )
    
    leaderboard_text = "\n".join(leaderboard_lines)
    
    broadcast_msg = (
        "🏆 **WEEKLY LEADERBOARD — FINAL STANDINGS!**\n\n"
        "⏰ Competition ends in 2 hours!\n\n"
        f"{leaderboard_text}\n\n"
        "━━━━━━━━━━━━━━━━━\n"
        "💰 Total Prize Pool: **₹600**\n"
        "🔄 Next week starts Monday 12 AM!\n\n"
        "Push harder — every point counts! 🔥"
    )
    
    # Send personalized congratulations to each winner
    for i, winner in enumerate(top_winners):
        rank = i + 1
        if rank > 10:
            break
        
        prize_info = WEEKLY_PRIZES.get(rank)
        if not prize_info:
            break
        
        user_id = winner.get('user_id')
        score = winner.get('weekly_score', 0)
        
        # Build personalized message
        if rank == 1:
            personal_msg = (
                "🎉🏆 **CONGRATULATIONS — YOU'RE THE CHAMPION!** 🏆🎉\n\n"
                f"You finished **Rank #{rank}** on this week's leaderboard!\n\n"
                f"📊 Final Score: **{score} pts**\n\n"
                "💎 **Your Rewards:**\n"
                f"├─ ₹{prize_info['amount']} Bonus Credits\n"
                f"└─ {PREMIUM_DAYS_RANK1} Days Premium Access\n\n"
                "Rewards will be credited after weekly reset (tonight 12 AM).\n\n"
                "👑 Can you defend your title next week?"
            )
        elif rank <= 3:
            personal_msg = (
                f"🎉 **CONGRATULATIONS — PODIUM FINISH!** 🎉\n\n"
                f"You finished **Rank #{rank}** on this week's leaderboard!\n\n"
                f"📊 Final Score: **{score} pts**\n\n"
                "💎 **Your Reward:**\n"
                f"└─ ₹{prize_info['amount']} Bonus Credits\n\n"
                "Rewards will be credited after weekly reset (tonight 12 AM).\n\n"
                "🔥 Push for #1 next week to unlock Premium!"
            )
        else:
            personal_msg = (
                f"🎉 **CONGRATULATIONS — TOP 10 FINISH!** 🎉\n\n"
                f"You finished **Rank #{rank}** on this week's leaderboard!\n\n"
                f"📊 Final Score: **{score} pts**\n\n"
                "💎 **Your Reward:**\n"
                f"└─ ₹{prize_info['amount']} Bonus Credits\n\n"
                "Rewards will be credited after weekly reset (tonight 12 AM).\n\n"
                "💪 Aim higher next week — Top 3 gets bigger prizes!"
            )
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=personal_msg,
                parse_mode="Markdown"
            )
            logger.info(f"Sent winner announcement to Rank {rank}: {user_id}")
        except Exception as e:
            logger.error(f"Failed to send winner message to Rank {rank} ({user_id}): {e}")
    
    logger.info(f"Weekly winners announced: Top {min(len(top_winners), 10)}")
    return broadcast_msg


async def credit_weekly_rewards(bot: Bot):
    """
    Called at weekly reset (Monday 12 AM IST).
    Credits the virtual bonus to each winner's wallet.
    """
    db = SupabaseClient()
    await db.connect()
    
    # Get top 10 winners
    top_winners = await db.get_weekly_leaderboard(limit=10)
    
    if not top_winners or len(top_winners) == 0:
        logger.info("No winners to credit")
        return
    
    credited_count = 0
    
    for i, winner in enumerate(top_winners):
        rank = i + 1
        if rank > 10:
            break
        
        prize_info = WEEKLY_PRIZES.get(rank)
        if not prize_info:
            break
        
        user_id = winner.get('user_id')
        bonus = prize_info['amount']
        
        try:
            # Get current wallet
            user = await db.get_user(user_id)
            if not user:
                continue
            
            current_wallet = user.get('wallet_stars', 0) or 0
            new_wallet = current_wallet + bonus
            
            update_data = {
                "user_id": user_id,
                "wallet_stars": new_wallet,
            }
            
            # Only Rank 1 gets premium access
            if rank == 1:
                expiry_date = (datetime.utcnow() + timedelta(days=PREMIUM_DAYS_RANK1)).isoformat()
                update_data["subscription_status"] = "premium"
                update_data["subscription_expires_at"] = expiry_date
                update_data["last_payment_date"] = datetime.utcnow().isoformat()
            
            await db.upsert_user(update_data)
            credited_count += 1
            logger.info(f"Credited ₹{bonus} to Rank {rank} winner {user_id}")
            
            # Send confirmation message
            if rank == 1:
                confirm_msg = (
                    "✅ **REWARDS CREDITED!**\n\n"
                    f"{prize_info['emoji']} Rank #{rank} — {prize_info['label']}\n\n"
                    f"💰 ₹{bonus} added → Wallet Balance: ₹{new_wallet}\n"
                    f"👑 Premium Status: Active ({PREMIUM_DAYS_RANK1} days)\n\n"
                    "Ready to defend your title this week? 🔥"
                )
            else:
                confirm_msg = (
                    "✅ **REWARDS CREDITED!**\n\n"
                    f"{prize_info['emoji']} Rank #{rank} — {prize_info['label']}\n\n"
                    f"💰 ₹{bonus} added → Wallet Balance: ₹{new_wallet}\n\n"
                    "Keep grinding — aim for #1 this week! 🔥"
                )
            
            await bot.send_message(
                chat_id=user_id,
                text=confirm_msg,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to credit rewards to Rank {rank} ({user_id}): {e}")
    
    logger.info(f"Weekly rewards credited to {credited_count} winners")


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
