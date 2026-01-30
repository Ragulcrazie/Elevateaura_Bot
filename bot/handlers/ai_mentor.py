
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db_client import SupabaseClient
from bot.services.ai_service import ai_service
from bot.services.session_manager import session_manager # To start new quiz
import random

router = Router()

@router.callback_query(F.data == "ai_coach")
async def show_ai_coach(callback: types.CallbackQuery):
    await callback.answer()
    
    user_id = callback.from_user.id
    db = SupabaseClient()
    await db.connect()
    
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Error: User profile not found.")
        return

    # Determine Weakest Area
    # Priority: Saved Weak Spots > Random Guess
    quiz_state = user.get("quiz_state", {})
    stats = quiz_state.get("stats", {})
    weak_spots = stats.get("weak_spots", {})
    
    lang = user.get("language_pref", "english").lower()
    if "hind" in lang: lang = "hindi"
    else: lang = "english"
    
    category = user.get("exam_category", "aptitude").lower()
    
    # Sort weak spots by mistake count (descending)
    sorted_weak = sorted(weak_spots.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_weak:
        weak_topic = sorted_weak[0][0]
    else:
        # If no data, pick a random topic from the relevant category
        # This prevents "Unknown" errors
        context_data = ai_service.get_context(lang, category)
        if context_data:
            weak_topic = random.choice(context_data).get("topic", "General")
        else:
            weak_topic = "General"

    # Get Content
    mistake = ai_service.get_common_mistake(weak_topic, lang, category)
    
    # Store the topic in callback data for the shortcut button
    # Callback limit is 64 chars. "shortcut:TopicName" might exceed if topic is long.
    # We'll truncate topic or store in a temp map if needed. 
    # For now, let's assume standard topics fit.
    
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
    
    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("get_short:"))
async def give_shortcut(callback: types.CallbackQuery):
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
        category = user.get("exam_category", "aptitude").lower()

    shortcut = ai_service.get_shortcut(topic, lang, category)
    
    await callback.answer()
    await callback.message.answer(
        f"🚀 **Shortcut for {topic}**:\n\n{shortcut}",
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("get_psych:"))
async def give_psych_hack(callback: types.CallbackQuery):
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
        category = user.get("exam_category", "aptitude").lower()

    hack = ai_service.get_psych_hack(topic, lang, category)
    
    await callback.answer()
    await callback.message.answer(
        f"🧠 **Psych Hack for {topic}**:\n\n{hack}",
        parse_mode="Markdown"
    )

