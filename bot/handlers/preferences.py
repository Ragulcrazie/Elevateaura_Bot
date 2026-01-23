from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_client import SupabaseClient
import logging

router = Router()
logger = logging.getLogger(__name__)

# Keyboards
def get_lang_keyboard():
    kb = [
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="pref_lang_english")],
        [InlineKeyboardButton(text="🇮🇳 Hindi", callback_data="pref_lang_hindi")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_category_keyboard():
    kb = [
        [InlineKeyboardButton(text="🧠 Aptitude", callback_data="pref_cat_aptitude")],
        [InlineKeyboardButton(text="🧩 Reasoning", callback_data="pref_cat_reasoning")],
        [InlineKeyboardButton(text="🌍 General Knowledge (GK)", callback_data="pref_cat_gk")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.callback_query(F.data == "settings")
async def cmd_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ **Settings**\n\nChoose your preferred language:", reply_markup=get_lang_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("pref_lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2] # english or hindi
    user_id = callback.from_user.id
    
    try:
        # Update DB
        db = SupabaseClient()
        await db.connect()
        # logging to see if it hangs here
        logger.info(f"Updating language for {user_id} to {lang}")
        
        # Check if user exists first, if not create them (safety net)
        # Actually upsert_user logic in db_client might be safer if we used that, 
        # but pure update requires row to exist.
        # Let's try upserting with minimal data to ensure existence.
        
        data = {"user_id": user_id, "language_pref": lang}
        db.client.table("users").upsert(data).execute()
        
        await callback.message.edit_text(f"✅ Language set to **{lang.title()}**.\n\nNow choose your subject:", reply_markup=get_category_keyboard(), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to set language: {e}")
        await callback.message.answer(f"❌ Error saving preference: {e}")
    
    await callback.answer()

@router.callback_query(F.data.startswith("pref_cat_"))
async def set_category(callback: types.CallbackQuery):
    cat = callback.data.split("_")[2] # aptitude or reasoning
    user_id = callback.from_user.id
    
    db = SupabaseClient()
    await db.connect()
    db.client.table("users").update({"exam_category": cat}).eq("user_id", user_id).execute()
    
    await callback.message.edit_text(
        f"✅ **Setup Complete!**\n\n"
        f"Topic: {cat.title()}\n"
        f"ready to start?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Start Quiz Now", callback_data="start_quiz_cmd")]]),
        parse_mode="Markdown"
    )
    await callback.answer()
