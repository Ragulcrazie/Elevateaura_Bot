"""
Ad Handlers - Telegram Bot Ad Integration
Provides helper functions to show ads in the bot flow.
"""

import logging
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.ad_service import get_ad_service

logger = logging.getLogger(__name__)


async def show_post_quiz_ad(
    message: types.Message, 
    user_id: int,
    user_data: dict,
    db_client
) -> bool:
    """
    Show ad after quiz completion (if eligible).
    
    Args:
        message: Telegram message object
        user_id: User's Telegram ID
        user_data: User data from database
        db_client: Database client instance
        
    Returns:
        bool: True if ad was shown, False otherwise
    """
    
    ad_service = get_ad_service(db_client)
    
    # Check if ad should be shown
    should_show, reason = await ad_service.should_show_ad(
        user_id=user_id,
        placement="post_quiz",
        user_data=user_data
    )
    
    if not should_show:
        logger.info(f"❌ Ad skipped for {user_id}: {reason}")
        return False
    
    try:
        # Show transitional message
        await message.answer(
            "📊 **Calculating Your Results...**\n\n"
            "⏳ Please wait a moment...",
            parse_mode="Markdown"
        )
        
        # Record impression BEFORE showing (prevents double-show on retry)
        await ad_service.record_ad_impression(user_id, "post_quiz", success=True)
        
        # Show Monetag ad message
        # Note: Since Telegram bots can't inject HTML/JS, we show a placeholder
        # The actual ad is triggered in WebApp (if user opens leaderboard)
        # But we still track the "slot" here for analytics
        
        await message.answer(
            "✨ **Quick Message from Our Sponsors**\n\n"
            "This free quiz is supported by ads.\n"
            "Thank you for your patience! 🙏",
            parse_mode="Markdown"
        )
        
        logger.info(f"✅ Post-quiz ad shown to {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to show post-quiz ad: {e}")
        # Don't record failed impressions
        return False


async def check_leaderboard_ad_eligibility(
    user_id: int,
    user_data: dict,
    db_client
) -> dict:
    """
    Check if user should see ad before opening leaderboard.
    Returns data to pass to WebApp.
    
    Returns:
        dict: {
            "show_ad": bool,
            "reason": str,
            "monetag_code": str (if applicable)
        }
    """
    
    ad_service = get_ad_service(db_client)
    
    should_show, reason = await ad_service.should_show_ad(
        user_id=user_id,
        placement="leaderboard",
        user_data=user_data
    )
    
    result = {
        "show_ad": should_show,
        "reason": reason,
        "monetag_code": None
    }
    
    if should_show:
        # Get Monetag JS code
        result["monetag_code"] = ad_service.get_monetag_code("leaderboard")
        
        # Record impression
        await ad_service.record_ad_impression(user_id, "leaderboard", success=True)
        logger.info(f"✅ Leaderboard ad approved for {user_id}")
    else:
        logger.info(f"❌ Leaderboard ad skipped for {user_id}: {reason}")
    
    return result


async def show_ai_coach_ad(
    message: types.Message,
    user_id: int,
    user_data: dict,
    db_client,
    query_count: int = 0
) -> bool:
    """
    Show ad after AI Coach query (based on frequency setting).
    
    Args:
        message: Telegram message object
        user_id: User's Telegram ID
        user_data: User data from database
        db_client: Database client instance
        query_count: Number of queries in this session
        
    Returns:
        bool: True if ad was shown
    """
    
    ad_service = get_ad_service(db_client)
    config = ad_service.config
    
    # Check frequency rule (every Nth query)
    ai_config = config.get("placements", {}).get("ai_coach", {})
    show_every_nth = ai_config.get("show_every_nth_query", 2)
    
    # Only check on Nth query
    if query_count % show_every_nth != 0:
        return False
    
    should_show, reason = await ad_service.should_show_ad(
        user_id=user_id,
        placement="ai_coach",
        user_data=user_data
    )
    
    if not should_show:
        logger.info(f"❌ AI Coach ad skipped for {user_id}: {reason}")
        return False
    
    try:
        await message.answer(
            "💡 **AI Coach Tip**\n\n"
            "_This intelligent feature is supported by our partners._",
            parse_mode="Markdown"
        )
        
        await ad_service.record_ad_impression(user_id, "ai_coach", success=True)
        logger.info(f"✅ AI Coach ad shown to {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to show AI Coach ad: {e}")
        return False


async def get_user_ad_stats(user_id: int, db_client) -> dict:
    """
    Get ad statistics for a user (for admin/debugging).
    
    Returns:
        dict: Ad stats by placement
    """
    
    ad_service = get_ad_service(db_client)
    stats = await ad_service.get_ad_stats(user_id, days=7)
    
    return stats
