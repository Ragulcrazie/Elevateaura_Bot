
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db_client import SupabaseClient
from bot.services.ai_service import ai_service
from bot.services.session_manager import session_manager # To start new quiz
import random
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "ai_coach")
async def show_ai_coach(callback: types.CallbackQuery):
    await callback.answer()
    
    try:
        user_id = callback.from_user.id
        logger.info(f"🤖 AI Coach requested by user {user_id}")
        
        db = SupabaseClient()
        await db.connect()
        
        user = await db.get_user(user_id)
        if not user:
            logger.error(f"❌ AI Coach: User {user_id} not found in DB")
            await callback.message.answer("Error: User profile not found. Please send /start first.")
            return

        # Check Premium Status
        sub_status = user.get("subscription_status", "free")
        logger.info(f"🤖 AI Coach: User {user_id} status = {sub_status}")
        
        if sub_status != "premium":
            # Create upgrade button
            builder = InlineKeyboardBuilder()
            builder.button(text="🚀 Upgrade to Premium (₹99/month)", callback_data="razorpay_monthly")
            builder.button(text="❌ Close", callback_data="close_message")
            builder.adjust(1)
            
            try:
                # Try editing the original message
                await callback.message.edit_text(
                    "🔒 **Premium Feature Locked**\n\n"
                    "The **AI Performance Coach** is available only for Premium users.\n\n"
                    "Upgrade to unlock:\n"
                    "• Personalized Weakness Analysis\n"
                    "• Instant Shortcuts & Psych Hacks\n"
                    "• 24/7 Mentorship\n\n"
                    "💰 Just ₹99/month for unlimited access!",
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
            except Exception as edit_err:
                logger.warning(f"Could not edit message for free user: {edit_err}")
                # Fallback: send new message
                await callback.message.answer(
                    "🔒 Premium Feature Locked\n\n"
                    "The AI Performance Coach is available only for Premium users.\n"
                    "Use /upgrade to unlock!",
                    reply_markup=builder.as_markup()
                )
            return

        # --- PREMIUM USER: Generate Coaching ---
        logger.info(f"🤖 AI Coach: Generating coaching for premium user {user_id}")
        
        # Determine Weakest Area
        quiz_state = user.get("quiz_state") or {}
        if isinstance(quiz_state, str):
            import json
            try:
                quiz_state = json.loads(quiz_state)
            except:
                quiz_state = {}
        
        stats = quiz_state.get("stats") or {}
        weak_spots = stats.get("weak_spots") or {}
        
        lang = user.get("language_pref", "english").lower()
        if "hind" in lang: lang = "hindi"
        else: lang = "english"
        
        category = user.get("exam_category", "aptitude") or "aptitude"
        category = category.lower()
        
        # Sort weak spots by mistake count (descending)
        sorted_weak = []
        if isinstance(weak_spots, dict) and weak_spots:
            sorted_weak = sorted(weak_spots.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_weak:
            weak_topic = sorted_weak[0][0]
            logger.info(f"🤖 AI Coach: Found weak topic from data: {weak_topic}")
        else:
            # If no data, pick a random topic from the relevant category
            context_data = [item for item in ai_service.data if item.get("category") == category]
            if not context_data:
                context_data = ai_service.data  # Fallback to all topics
            if context_data:
                weak_topic = random.choice(context_data).get("topic", "General")
            else:
                weak_topic = "General"
            logger.info(f"🤖 AI Coach: No weak spots, using random topic: {weak_topic}")

        # Get Content
        mistake = ai_service.get_common_mistake(weak_topic, lang, category)
        if not mistake:
            mistake = "Don't rush through problems. Read carefully before solving."
        
        safe_topic = weak_topic[:20] 
        
        text = (
            f"🤖 **AI Performance Coach**\n\n"
            f"Your main enemy right now is **{weak_topic}**. "
            f"You are spending too much time thinking instead of reacting.\n\n"
            f"💡 **Quick Fix**: For the next 24 hours, do not solve full problems. "
            f"Just identify the *First Step*.\n\n"
            f"⚠️ **Common Pitfall**: {mistake}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💡 Give me a Shortcut", callback_data=f"get_short:{safe_topic}")
        builder.button(text="🧠 Psych Hack", callback_data=f"get_psych:{safe_topic}")
        builder.button(text="😤 I'm Ready to Train", callback_data="start_quiz_cmd")
        builder.adjust(1)
        
        try:
            await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
            logger.info(f"✅ AI Coach: Response sent to user {user_id}")
        except Exception as send_err:
            logger.error(f"❌ AI Coach: Markdown send failed: {send_err}")
            # Retry without markdown
            plain_text = text.replace("**", "").replace("*", "")
            await callback.message.answer(plain_text, reply_markup=builder.as_markup())
            logger.info(f"✅ AI Coach: Plain text response sent to user {user_id}")
            
    except Exception as e:
        logger.error(f"❌ AI Coach CRITICAL ERROR for user {callback.from_user.id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Always send SOMETHING back to the user
        try:
            await callback.message.answer(
                "🤖 AI Coach is temporarily busy. Please try again in a moment.\n"
                f"Error: {str(e)[:100]}"
            )
        except:
            pass

@router.callback_query(F.data.startswith("get_short:"))
async def give_shortcut(callback: types.CallbackQuery):
    try:
        topic = callback.data.split(":")[1]
        
        user_id = callback.from_user.id
        db = SupabaseClient()
        await db.connect()
        user = await db.get_user(user_id)
        
        lang = "english"
        category = "aptitude"
        if user:
            if "hind" in user.get("language_pref", "").lower():
                lang = "hindi"
            category = (user.get("exam_category", "aptitude") or "aptitude").lower()

        shortcut = ai_service.get_shortcut(topic, lang, category)
        if not shortcut:
            shortcut = "Focus on identifying the pattern first, then apply the formula."
        
        await callback.answer()
        await callback.message.answer(
            f"🚀 **Shortcut for {topic}**:\n\n{shortcut}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"❌ Shortcut error: {e}")
        await callback.answer()
        await callback.message.answer(f"🚀 Quick Tip: Focus on accuracy before speed. Practice the basics first.")

@router.callback_query(F.data.startswith("get_psych:"))
async def give_psych_hack(callback: types.CallbackQuery):
    try:
        topic = callback.data.split(":")[1]
        
        user_id = callback.from_user.id
        db = SupabaseClient()
        await db.connect()
        user = await db.get_user(user_id)
        
        lang = "english"
        category = "aptitude"
        if user:
            if "hind" in user.get("language_pref", "").lower():
                lang = "hindi"
            category = (user.get("exam_category", "aptitude") or "aptitude").lower()

        hack = ai_service.get_psych_hack(topic, lang, category)
        if not hack:
            hack = "Visualize yourself solving the problem confidently before you start."
        
        await callback.answer()
        await callback.message.answer(
            f"🧠 **Psych Hack for {topic}**:\n\n{hack}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"❌ Psych hack error: {e}")
        await callback.answer()
        await callback.message.answer(f"🧠 Mental Tip: Stay calm, breathe, and trust your preparation.")

@router.callback_query(F.data == "close_message")
async def close_message_handler(callback: types.CallbackQuery):
    """Closes/deletes the message cleanly"""
    await callback.answer()
    try:
        await callback.message.delete()
    except:
        # If deletion fails, just edit to a minimal message
        await callback.message.edit_text("✅ Message closed")
