import asyncio
import logging
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from database.db_client import SupabaseClient
from bot.handlers.quiz import router as quiz_router
from bot.handlers.payment import router as payment_router
from bot.handlers.preferences import router as prefs_router
from bot.services.rank_engine import RankEngine

rank_engine = RankEngine()

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Bot & Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
from bot.handlers.ai_mentor import router as ai_router
from bot.handlers.career_reward import router as career_router
dp.include_router(quiz_router)
dp.include_router(payment_router)
dp.include_router(prefs_router)
dp.include_router(ai_router)
dp.include_router(career_router)
db = SupabaseClient()

# --- Admin Handlers ---
from aiogram import F
@dp.message(F.text.startswith("Crazie@0907"))
async def admin_reset(message: types.Message):
    """
    Secret Admin Command to reset daily limit.
    Usage: Crazie@0907
    """
    await db.connect()
    success = await db.reset_user_limit(message.from_user.id)
    if success:
        await message.answer("🛠️ **ADMIN OVERRIDE**\n\nDaily limit has been reset to 0.\nYou can now start from Question 1 again.", parse_mode="Markdown")
    else:
        await message.answer("❌ Error resetting limit.")

# --- Handlers (Temporary placement, will move to handlers/ folder) ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Handle /start command.
    Checks user in DB and sends welcome message.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # --- Deep Link Handling (Payment Success) ---
    # Manual parsing is safer than imports for now
    args = None
    if len(message.text.split()) > 1:
        args = message.text.split()[1]
    
    if args == "subscribe_pro":
        logger.info(f"User {user_id} triggered PRO subscription via Deep Link.")
        # Update DB to PRO
        await db.upsert_user({
            "user_id": user_id, 
            "subscription_status": "pro_99",
            "full_name": full_name
        })
        await message.answer(
            "🎉 **PAYMENT SUCCESSFUL!**\n\n"
            "👑 **You are now a PRO Member.**\n"
            "✅ Unlimited Quizzes\n"
            "✅ Detailed Analytics\n"
            "✅ 'Competitor Intelligence' Unlocked\n\n"
            "Type /quiz to test your new powers!",
            parse_mode="Markdown"
        )
        return

    logger.info(f"User {user_id} started the bot.")
    
    # 1. Register User in DB
    # 1. Register/Update User in DB
    # Fetch existing to avoid overwriting stats (like questions_answered) with defaults
    existing_user = await db.get_user(user_id)
    is_new_user = (existing_user is None)
    
    user_data = {
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        # Preserve existing fields if they exist
        "subscription_status": existing_user.get("subscription_status", "free") if existing_user else "free",
        "current_streak": existing_user.get("current_streak", 0) if existing_user else 0,
        "questions_answered": existing_user.get("questions_answered", 0) if existing_user else 0,
        "average_pace": existing_user.get("average_pace", 0) if existing_user else 0
    }
    
    # Run DB operation
    # Check for Referral Code
    referrer_id = None
    if args and args.startswith("ref_"):
        try:
            referrer_id = int(args.split("_")[1])
            # Prevent self-referral
            if referrer_id == user_id: 
                referrer_id = None
        except:
            pass

    # Update User Data
    user_update = user_data.copy()
    
    # Only set referred_by if it's a NEW user and they don't have one
    if is_new_user and referrer_id:
        user_update["referred_by"] = referrer_id
        logger.info(f"User {user_id} referred by {referrer_id}")

    try:
        await db.upsert_user(user_update)
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        # Proceed anyway so the user gets the welcome message

    
    # 2. Terms Check
    terms_accepted = existing_user.get("terms_accepted", False) if existing_user else False
    
    if not terms_accepted:
        # Show Terms Agreement Screen INSTEAD of Main Menu
        terms_kb = InlineKeyboardBuilder()
        terms_kb.button(text="📄 Read Terms", callback_data="read_terms_summary")
        terms_kb.button(text="🔒 Privacy Policy", callback_data="read_privacy_summary")
        terms_kb.button(text="✅ I AGREE & CONTINUE", callback_data="agree_terms_action")
        terms_kb.adjust(2, 1) # 2 buttons top, 1 big button bottom
        
        await message.answer(
            f"👋 **Hello {full_name}!**\n\n"
            "To use **Elevate Aura**, you must accept our updated Terms & Privacy Policy.\n\n"
            "🛡️ **Your Data is Safe:** We only store your scores and generic profile info as per GDPR/CCPA standards.\n\n"
            "⚠️ **Virtual Currency:** Credits are digital assets subject to platform terms.\n\n"
            "Please confirm you agree to continue:",
            reply_markup=terms_kb.as_markup(),
            parse_mode="Markdown"
        )
        return

    # 3. Send Main Menu (Only if Terms Accepted)
    # Create Layout
    from urllib.parse import quote
    safe_name = quote(full_name)
    import time
    timestamp = int(time.time())
    # USE RENDER URL for instant updates (serving from main.py)
    render_base_url = "https://elevateaura-bot.onrender.com"
    web_app_url = f"{render_base_url}/?user_id={user_id}&name={safe_name}&v={timestamp}"

    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Check Leaderboard (v82)", web_app=WebAppInfo(url=web_app_url))
    builder.button(text="📝 Start Quiz", callback_data="start_quiz_cmd") # Shortcuts
    builder.button(text="⚙️ Language & Topic", callback_data="settings")
    builder.adjust(1)
    
    
    # Check if this is a new user (first time using bot)
    # is_new_user variable is defined at top of function

    
    await message.answer(
        f"👋 **Welcome Back, {full_name}!**\n\n"
        "🇬🇧 **ENGLISH:**\n"
        "Ready to perform? Open your Dashboard to check Ranks & Start Quizzes.\n\n"
        "🇮🇳 **HINDI:**\n"
        "तैयार हैं? रैंक देखने और क्विज़ शुरू करने के लिए डैशबोर्ड खोलें।\n\n"
        "👇 **Action Center / एक्शन सेंटर:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    
    # Send legal disclaimer ONLY for new users (first time)
    if is_new_user:
        await message.answer(
            "📋 **IMPORTANT**: By using this bot, you agree to our:\n"
            "• /terms - Terms & Conditions\n"
            "• /privacy - Privacy Policy\n\n"
            "Commands are available anytime if you need to review them.",
            parse_mode="Markdown"
        )
    
    # --- PERSISTENT REWARD REMINDER ---
    # Check if user is eligible for career consultation reward
    if existing_user:
        metadata = existing_user.get("metadata", {}) or {}
        already_claimed = metadata.get("lead_submitted", False)
        
        # Show reminder if they qualified (scored 8/10 at any time) but haven't claimed
        if not already_claimed:
            # Check if they've ever scored 8+ in a single quiz
            quiz_state = existing_user.get("quiz_state", {}) or {}
            lifetime_stats = metadata.get("lifetime_stats", {}) or {}
            
            # Simple check: if they have stats, they've taken quizzes
            # We'll show reminder to anyone who hasn't claimed yet (they might have qualified)
            # More precise: check if current_streak >= 8 (though this might be from multiple quizzes)
            current_streak = existing_user.get("current_streak", 0) or 0
            
            if current_streak >= 8 or lifetime_stats.get("global_total", 0) >= 8:
                reward_builder = InlineKeyboardBuilder()
                reward_builder.button(text="🎁 Claim Your Reward", callback_data=f"claim_reward:{user_id}")
                
                await message.answer(
                    "🏆 **REWARD AVAILABLE!**\n\n"
                    "You've unlocked a **Career Consultation Reward** for being a top performer!\n\n"
                    "**Benefits:**\n"
                    "✅ FREE Career Guidance\n"
                    "✅ Exclusive Coaching Discounts\n"
                    "✅ Study Material Access\n\n"
                    "👇 **Claim it now before it expires!**",
                    reply_markup=reward_builder.as_markup(),
                    parse_mode="Markdown"
                )

# --- Terms Callback Handlers ---
from datetime import datetime

@dp.callback_query(F.data == "agree_terms_action")
async def cb_agree_terms(callback: types.CallbackQuery):
    await callback.answer("✅ Terms Accepted!")
    user_id = callback.from_user.id
    
    # Update DB
    await db.client.from_("users").update({
        "terms_accepted": True,
        "terms_accepted_at": datetime.utcnow().isoformat()
    }).eq("user_id", user_id).execute()
    
    # Re-trigger start to show menu
    # Fetch user details for the URL
    full_name = callback.from_user.full_name
    
    # --- NEW WELCOME BONUS TRIGGER (High Conversion) ---
    builder = InlineKeyboardBuilder()
    builder.button(text="🎟️ Activate Ticket / टिकट सक्रिय करें", callback_data=f"claim_reward:{user_id}")
    
    await callback.message.answer(
        "🎉 **WELCOME BONUS UNLOCKED!**\n\n"
        "You've been entered into our **Weekly Career Scholarship Lucky Draw** (Worth ₹25,000)! 💰\n\n"
        "👇 **Complete your profile to activate your ticket:**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎉 **स्वागत बोनस अनलॉक!**\n\n"
        "आपको हमारी **साप्ताहिक करियर स्कॉलरशिप लकी ड्रा** (₹25,000 मूल्य) में शामिल किया गया है! 💰\n\n"
        "👇 **अपना टिकट सक्रिय करने के लिए प्रोफाइल पूरा करें:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    
    # Also show the main menu below so they aren't stuck, but the Bonus is the focus
    from urllib.parse import quote
    safe_name = quote(full_name)
    import time
    timestamp = int(time.time())
    render_base_url = "https://elevateaura-bot.onrender.com"
    web_app_url = f"{render_base_url}/?user_id={user_id}&name={safe_name}&v={timestamp}"

    menu_kb = InlineKeyboardBuilder()
    menu_kb.button(text="🔥 Check Leaderboard (v82)", web_app=WebAppInfo(url=web_app_url))
    menu_kb.button(text="📝 Start Quiz", callback_data="start_quiz_cmd")
    menu_kb.adjust(1)
    
    await callback.message.answer(
        f"✅ **Account Created for {full_name}**\n\n"
        "You can find your main menu below:",
        reply_markup=menu_kb.as_markup(),
        parse_mode="Markdown"
    )
    from urllib.parse import quote
    import time
    safe_name = quote(full_name)
    timestamp = int(time.time())
    render_base_url = "https://elevateaura-bot.onrender.com"
    web_app_url = f"{render_base_url}/?user_id={user_id}&name={safe_name}&v={timestamp}"

    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Check Leaderboard (v82)", web_app=WebAppInfo(url=web_app_url))
    builder.button(text="📝 Start Quiz", callback_data="start_quiz_cmd")
    builder.button(text="⚙️ Language & Topic", callback_data="settings")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"👋 **Welcome to Elevate Aura, {full_name}!**\n"
        "*(The Ultimate Daily Quiz Arena)*\n\n"
        "🇬🇧 **ENGLISH:**\n"
        "1. **Play Daily Quizzes:** Sharpen your skills in GK, Math & English.\n"
        "2. **Climb the Leaderboard:** Compete with 500+ active aspirants.\n"
        "3. **Unlock Premium:** Earn 'Aura Credits' to get exclusive Notes & Mentorship.\n\n"
        "───────────────\n\n"
        "🇮🇳 **HINDI / हिंदी:**\n"
        "1. **रोज़ाना क्विज़ खेलें:** सामान्य ज्ञान, गणित और अंग्रेजी में पकड़ मजबूत करें।\n"
        "2. **लीडरबोर्ड पर छा जाएं:** हज़ारों छात्रों के साथ मुकाबला करें।\n"
        "3. **प्रीमियम अनलॉक करें:** 'औरा क्रेडिट्स' से खास नोट्स और गाइडेंस पाएं।\n\n"
        "👇 **Start Your Journey / अपनी यात्रा शुरू करें:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "read_terms_summary")
async def cb_read_terms(callback: types.CallbackQuery):
    await callback.message.answer(
        "📜 **TERMS SUMMARY**\n\n"
        "1. **Fair Play**: No cheating or multiple accounts.\n"
        "2. **Virtual Currency**: 'Aura Credits' are not real money.\n"
        "3. **Age**: You must be 13+.\n"
        "4. **Refunds**: No refunds on subscriptions.\n\n"
        "Full text: /terms",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "read_privacy_summary")
async def cb_read_privacy(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔒 **PRIVACY SUMMARY**\n\n"
        "1. **We Collect**: Name, ID, Quiz Scores.\n"
        "2. **We Don't Collect**: Phone number, Chat history.\n"
        "3. **Usage**: Leaderboards & Stats.\n\n"
        "Full text: /privacy",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(Command("terms"))
async def cmd_terms(message: types.Message):
    """
    Display Terms and Conditions.
    Splits into multiple messages if exceeds Telegram's 4096 character limit.
    """
    try:
        # Read the terms file
        terms_path = os.path.join(os.path.dirname(__file__), "assets", "terms_and_conditions.txt")
        with open(terms_path, "r", encoding="utf-8") as f:
            terms_content = f.read()
        
        # Split into chunks (Telegram limit: 4096 chars)
        max_length = 4000  # Leave some buffer
        chunks = [terms_content[i:i+max_length] for i in range(0, len(terms_content), max_length)]
        
        await message.answer("📜 **TERMS AND CONDITIONS**\n\nReading document...", parse_mode="Markdown")
        
        for idx, chunk in enumerate(chunks, 1):
            if len(chunks) > 1:
                await message.answer(f"📄 **Part {idx}/{len(chunks)}**\n\n{chunk}")
            else:
                await message.answer(chunk)
            await asyncio.sleep(0.5)  # Avoid rate limiting
        
        await message.answer(
            "✅ End of Terms and Conditions\n\n"
            "By using ElevateAura, you agree to these terms.",
            parse_mode="Markdown"
        )
        
    except FileNotFoundError:
        await message.answer("⚠️ Terms and Conditions file not found. Please contact support.")
    except Exception as e:
        logger.error(f"Error reading terms: {e}")
        await message.answer("❌ Error loading Terms and Conditions. Please try again later.")

@dp.message(Command("privacy"))
async def cmd_privacy(message: types.Message):
    """
    Display Privacy Policy.
    Splits into multiple messages if exceeds Telegram's 4096 character limit.
    """
    try:
        # Read the privacy policy file
        privacy_path = os.path.join(os.path.dirname(__file__), "assets", "privacy_policy.txt")
        with open(privacy_path, "r", encoding="utf-8") as f:
            privacy_content = f.read()
        
        # Split into chunks (Telegram limit: 4096 chars)
        max_length = 4000  # Leave some buffer
        chunks = [privacy_content[i:i+max_length] for i in range(0, len(privacy_content), max_length)]
        
        await message.answer("🔒 **PRIVACY POLICY**\n\nReading document...", parse_mode="Markdown")
        
        for idx, chunk in enumerate(chunks, 1):
            if len(chunks) > 1:
                await message.answer(f"📄 **Part {idx}/{len(chunks)}**\n\n{chunk}")
            else:
                await message.answer(chunk)
            await asyncio.sleep(0.5)  # Avoid rate limiting
        
        await message.answer(
            "✅ End of Privacy Policy\n\n"
            "Your data is handled according to this policy.",
            parse_mode="Markdown"
        )
        
    except FileNotFoundError:
        await message.answer("⚠️ Privacy Policy file not found. Please contact support.")
    except Exception as e:
        logger.error(f"Error reading privacy policy: {e}")
        await message.answer("❌ Error loading Privacy Policy. Please try again later.")

@dp.message(Command("support"))
async def cmd_support(message: types.Message):
    """
    Support Contact Info
    """
    await message.answer(
        "🛠 **Elevate Aura Support**\n\n"
        "Need help with Premium, Payments, or Bugs?\n\n"
        "📧 Email: reviewerelevateaura@gmail.com\n"
        "⏳ Response Time: Within 24 hrs\n\n"
        "Please provide your User ID when contacting us."
    )

# --- Keep Alive Server for Render ---
from aiohttp import web

async def health_check(request):
    return web.Response(text="Bot is alive!")

    logger.info(f"Web server started on port {port}")
    return site

async def handle_options(request):
    return web.Response(headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

async def get_user_data(request):
    user_id = request.query.get("user_id")
    if not user_id:
        return web.json_response({"error": "Missing user_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
    
    try:
        from bot.services.subscription_service import SubscriptionService
        
        user_data = await db.get_user(int(user_id))
        if user_data:
            # Check subscription expiration first
            sub_service = SubscriptionService()
            sub_status = await sub_service.check_and_update_expiration(int(user_id))
            
            # Refresh user_data if subscription was just expired
            if sub_status.get("expired"):
                user_data = await db.get_user(int(user_id))
            
            # Simple Pack Logic: 1200 rating -> Pack 12
            # Default to Pack 10 (Rating 1000) if no rating
            rating = user_data.get("skill_rating", 1200) # Assuming default 1200
            # If skill_rating is missing in DB (old schema), default to 1200
            if rating is None: rating = 1200
                
            pack_id = int(rating / 100)
            
            # Stats via JSONB (quiz_state['stats'])
            today_str = db.get_ist_date()
            
            quiz_state = user_data.get("quiz_state") or {}
            saved_stats = quiz_state.get("stats", {})
            last_active = saved_stats.get("last_active_date")
            
            # --- BUCKET DATA RETRIEVAL ---
            # Try metadata first, then quiz_state fallback
            ls_meta = user_data.get("metadata", {}).get("lifetime_stats", {})
            ls_fallback = quiz_state.get("lifetime_stats", {})
            
            # Merge logic: If meta is empty but fallback has data, use fallback
            final_lifetime_stats = ls_meta if ls_meta.get("global_total", 0) > 0 else ls_fallback

            # --- DAILY RESET LOGIC (VIEW ONLY) ---
            # If score > 0, we trust it even if date is slightly off (timezone edge cases)
            has_score_today = saved_stats.get("daily_score", 0) > 0
            
            if last_active != today_str and not has_score_today:
                # New day, but user hasn't played yet. Return 0 stats.
                derived_q_answered = 0
                db_pace = user_data.get("average_pace") or saved_stats.get("average_pace") or 0
                daily_score = 0
                weak_spots = {}
                potential_score = 0
            else:
                # Same day OR user has played today despite date string mismatch
                db_q_answered_json = saved_stats.get("questions_answered")
                db_q_answered_col = user_data.get("questions_answered")
                
                # Check explicitly for None to allow 0
                if db_q_answered_json is not None:
                    derived_q_answered = db_q_answered_json
                elif db_q_answered_col is not None:
                    derived_q_answered = db_q_answered_col
                else:
                    # Fallback only if NO data exists (migration case)
                    derived_q_answered = int(user_data.get("current_streak", 0) / 10)
                
                db_pace = saved_stats.get("average_pace") or user_data.get("average_pace") or 0
                daily_score = saved_stats.get("daily_score", 0)
                weak_spots = saved_stats.get("weak_spots", {})
                
                # Calculate Potential Score (Real)
                # Potential = Current Score + (Mistakes * 10)
                # But we don't store "mistakes count" explicitly, we store map.
                total_mistakes = sum(weak_spots.values()) if weak_spots else 0
                potential_score = daily_score + (total_mistakes * 10)
                
                # Cap at 600 just in case
                if potential_score > 600: potential_score = 600
                
                # Process Weak Spots (Top 3)
                # Convert {"Topic": 3, "Topic2": 1} -> [{"topic": "Topic", "count": 3}]
                sorted_spots = sorted(weak_spots.items(), key=lambda x: x[1], reverse=True)[:3]
                processed_weak_spots = [{"topic": k, "count": v} for k, v in sorted_spots]
            
            # Use 'processed_weak_spots' variable to assign to response, or empty list if new day
            # If we decided to show stats (has_score_today is true), show weak spots too
            final_weak_spots = processed_weak_spots if (last_active == today_str or has_score_today) else []
            
            return web.json_response({
                "full_name": user_data.get("full_name", "Unknown Aspirant"),
                "total_score": daily_score, 
                "weekly_score": user_data.get("weekly_score", 0), # V2
                "wallet_stars": user_data.get("wallet_stars", 0), # V2
                "lead_data": user_data.get("lead_data", None),    # V2
                "total_payments": user_data.get("total_payments", 0), # V3.8 for Loyalty Check
                "questions_answered": derived_q_answered,
                "pack_id": pack_id,
                "average_pace": db_pace,
                "subscription_status": user_data.get("subscription_status", "free"),
                "language": user_data.get("language_pref", "english"),
                "potential_score": potential_score,
                "weak_spots": final_weak_spots,
                "lifetime_stats": final_lifetime_stats
            }, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "User not found"}, status=404, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logger.error(f"API Error: {e}")
        return web.json_response({"error": "Internal Server Error"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def redeem_stars(request):
    """
    Handle Star Redemption for Premium.
    Body: { user_id: 123, plan: 'monthly' | 'yearly' }
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        plan = data.get("plan") # 'monthly' or 'yearly'
        
        if not user_id or plan not in ['monthly', 'yearly']:
            return web.json_response({"error": "Invalid request"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
            
        # Pricing
        cost = 99 if plan == 'monthly' else 999
        days_to_add = 30 if plan == 'monthly' else 365
        
        # 1. Get User Data
        user_res = db.client.from_("users").select("wallet_stars, subscription_status, subscription_expires_at").eq("user_id", user_id).execute()
        
        if not user_res.data:
            return web.json_response({"error": "User not found"}, status=404, headers={"Access-Control-Allow-Origin": "*"})
            
        user = user_res.data[0]
        current_balance = user.get("wallet_stars", 0) or 0
        
        # 2. Check Balance
        if current_balance < cost:
            return web.json_response({"error": "Insufficient balance"}, status=402, headers={"Access-Control-Allow-Origin": "*"})
            
        # 3. Calculate New Expiry
        from datetime import datetime, timedelta
        
        expiry_str = user.get("subscription_expires_at")
        now = datetime.utcnow()
        
        if expiry_str:
            try:
                current_expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                # If active, extend from expiry. If expired, start from now.
                # Use replace(tzinfo=None) to ensure comparison works if one is offset-naive
                if current_expiry > now:
                     start_date = current_expiry
                else:
                     start_date = now
            except:
                start_date = now
        else:
            start_date = now
            
        new_expiry = start_date + timedelta(days=days_to_add)
        
        # 4. Execute Transaction (Deduct Stars + Grant Premium)
        update_res = db.client.from_("users").update({
            "wallet_stars": current_balance - cost,
            "subscription_status": "premium",
            "subscription_expires_at": new_expiry.isoformat(),
            "last_payment_date": now.isoformat(), # Track as payment
            "total_payments": (user.get("total_payments", 0) or 0) + 1,
            "expiration_warning_sent": False # Reset warning
        }).eq("user_id", user_id).execute()
        
        if update_res.data:
            # --- REFERRAL HOOK ---
            # Trigger background task for referral reward
            try:
                 from bot.services.referral_service import process_referral_reward
                 # Since this is aiohttp, we need to schedule it on the loop or run it
                 # 'bot' variable is global in main.py
                 asyncio.create_task(process_referral_reward(bot, int(user_id)))
            except Exception as e:
                 logger.error(f"Referral trigger failed: {e}")

            return web.json_response({
                "success": True, 
                "new_balance": current_balance - cost,
                "new_expiry": new_expiry.isoformat(),
                "days_added": days_to_add
            }, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "Update failed"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

    except Exception as e:
        logger.error(f"Redeem Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def update_name(request):
    """
    Update User Display Name.
    Body: { user_id: 123, new_name: "Warrior_007" }
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        new_name = data.get("new_name")
        
        if not user_id or not new_name:
            return web.json_response({"error": "Invalid request"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
            
        # Sanitize: Max 20 chars, no crazy symbols
        new_name = new_name.strip()[:20]
        
        # Update DB
        res = db.client.from_("users").update({"first_name": new_name}).eq("user_id", user_id).execute()
        
        if res.data:
            return web.json_response({"success": True, "name": new_name}, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "Update failed"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

    except Exception as e:
        logger.error(f"Name Update Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def get_ghosts_for_pack(request):
    try:
        pack_id = request.query.get("pack_id")
        user_id_str = request.query.get("user_id")
        mode = request.query.get("mode", "daily") # 'daily' or 'weekly'
        
        if not pack_id:
            return web.json_response({"error": "Missing pack_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
        
        # 1. Fetch User Score & Pace
        user_score = 0
        user_pace = None
        god_mode = False # TODO: Fetch from metadata (last_win_date)

        if user_id_str:
            try:
                user_data = await db.get_user(int(user_id_str))
                if user_data:
                    # Fetch Pace (Stored in 'average_pace' column or metadata)
                    # Assuming column exists or stored in metadata
                    user_pace = user_data.get("average_pace")
                    if not user_pace:
                        # Fallback to metadata
                        meta = user_data.get("metadata", {})
                        user_pace = meta.get("average_pace", 30) # Default 30s
                        
                        # Check God Mode (Win Lockout)
                        last_win = meta.get("last_win_epoch", 0)
                        import time
                        if time.time() - last_win < (7 * 24 * 3600): # Won in last 7 days
                            god_mode = True

                    if mode == 'weekly':
                        user_score = user_data.get("weekly_score", 0) or 0
                    else:
                        # Daily Logic: STRICT RESET
                        today_str = db.get_ist_date()
                        quiz_state = user_data.get("quiz_state") or {}
                        saved_stats = quiz_state.get("stats", {})
                        
                        last_active = saved_stats.get("last_active_date")
                        
                        if last_active == today_str:
                            user_score = saved_stats.get("daily_score", 0)
                        else:
                            user_score = 0
            except:
                pass 

        # 2. Fetch Raw Ghosts (SIMPLIFIED & ROBUST)
        # We need exactly 49 ghosts to make a Top 50 (including user)
        target_count = 49
        raw_ghosts = []
        
        try:
            # Simple Fetch: Get 49 items.
            response = db.client.table("ghost_profiles").select("*").limit(49).execute()
            raw_ghosts = response.data if response.data else []
        except Exception as e:
            logger.error(f"Ghost DB Error: {e}")
            raw_ghosts = []
            
        # Ensure we never exceed 49 (in case limit didn't work or logic changed)
        raw_ghosts = raw_ghosts[:49]

        # PADDING LOGIC - ABSOLUTE GUARANTEE
        # If DB returns 0, 2, or 10 ghosts, we fill the rest up to 49.
        current_count = len(raw_ghosts)
        if current_count < target_count:
            needed = target_count - current_count
            for i in range(needed):
                # Use a specific ID range for synthetic ghosts to ensure deterministic seeding in RankEngine
                syn_id = 990000 + i + (pack_id * 100) 
                raw_ghosts.append({
                    "id": syn_id, 
                    "full_name": "" # RankEngine will assign names like "Rahul Sharma"
                })
        
        # 3. Process Scores
        if mode == 'weekly':
            # Generate Weekly Accumulated Scores with SMART RIVALRY
            processed_ghosts = rank_engine.generate_weekly_ghosts(raw_ghosts, user_score, user_pace, god_mode)
            
            # Merge with Real Weekly Leaders (Top 5)
            real_leaders = await db.get_weekly_leaderboard(limit=5)
            for real in real_leaders:
                if str(real.get('user_id')) == str(user_id_str): continue 
                
                # Check real user pace too?
                real_pace = real.get("average_pace", 30)
                
                processed_ghosts.append({
                    "user_id": real['user_id'],
                    "full_name": real.get('first_name') or "Aspirant",
                    "weekly_score": real.get('weekly_score', 0),
                    "average_pace": real_pace,
                    "is_ghost": False,
                    "is_user": False
                })
            
            processed_ghosts.sort(key=lambda x: x.get("weekly_score", 0), reverse=True)
            processed_ghosts = processed_ghosts[:target_count] # Cap at 49 ghosts
            
            for p in processed_ghosts:
                p["total_score"] = p.get("weekly_score", 0)
                
        else:
            # Daily Logic with SMART RIVALRY
            processed_ghosts = rank_engine.generate_ghost_data(raw_ghosts, user_score, user_pace, god_mode)
        
        return web.json_response({"ghosts": processed_ghosts}, headers={"Access-Control-Allow-Origin": "*"})
        
    except Exception as e:
        logger.error(f"Failed to fetch ghosts: {e}")
        # FINAL SAFETY NET
        return web.json_response({
            "ghosts": [
                {"full_name": "Ghost Leader", "total_score": 100, "is_ghost": True},
                {"full_name": "Elite Player", "total_score": 90, "is_ghost": True}
            ]
        }, headers={"Access-Control-Allow-Origin": "*"})

async def simulate_payment(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        if not user_id:
             return web.json_response({"error": "Missing user_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
        
        # Read-Modify-Write to ensure we don't wipe other fields if upsert is partial
        user_id_int = int(user_id)
        existing_user = await db.get_user(user_id_int)
        
        if existing_user:
            existing_user["subscription_status"] = "premium"
            # remove 'id' if present as it might conflict with auto-increment if Supabase is strictly typed, 
            # though user_id is the key. Safer to just pass what we have.
            await db.upsert_user(existing_user)
        else:
            # New user case (rare here)
            await db.upsert_user({
                "user_id": user_id_int,
                "subscription_status": "premium"
            })
            
        return web.json_response({"status": "success"}, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logger.error(f"Payment Sim Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def reward_ad_api(request):
    """
    Reward user for watching an ad (Adds +1 Star).
    Body: { user_id: 123 }
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return web.json_response({"error": "Missing user_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
            
        # 1. Fetch current balance
        user_data = await db.get_user(int(user_id))
        if not user_data:
             return web.json_response({"error": "User not found"}, status=404, headers={"Access-Control-Allow-Origin": "*"})
             
        current_balance = user_data.get("wallet_stars", 0) or 0
        new_balance = current_balance + 1
        
        # 2. Update DB
        res = db.client.from_("users").update({"wallet_stars": new_balance}).eq("user_id", int(user_id)).execute()
        
        if res.data:
            return web.json_response({"success": True, "new_balance": new_balance}, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "Update failed"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

    except Exception as e:
        logger.error(f"Ad Reward Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def handle_options_post(request):
     return web.Response(headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

# 4. Payment API Route
async def create_invoice_api(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        plan = data.get("plan", "monthly") # Default to monthly if missing, but should be explicit
        
        if not user_id:
            return web.json_response({"error": "Missing user_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
        
        from bot.handlers.payment import generate_invoice_link, get_product_description
        
        # 0. Send Brainwashing Message (Optional, maybe skip for quicker UI flow? user expects invoice)
        # Verify wallet balance logic is handled in pre_checkout_query, but good to check here too?
        # No, let the invoice link generation proceed. Pre-checkout handles the hard check.
        
        # 1. Send Invoice Link
        link = await generate_invoice_link(bot, int(user_id), plan)
        
        return web.json_response({"invoice_link": link}, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logger.error(f"Invoice Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def start_web_server():
    # Define all async functions FIRST, before route registration
    
    # Lead Capture Route Handler
    async def save_lead_api(request):
        try:
            data = await request.json()
            user_id = data.get("user_id")
            lead_info = data.get("lead_data") # {phone, exam, mode}
            
            if not user_id or not lead_info:
                return web.json_response({"error": "Missing Data"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
                
            success = await db.save_lead(int(user_id), lead_info)
            if success:
                return web.json_response({"status": "success"}, headers={"Access-Control-Allow-Origin": "*"})
            else:
                return web.json_response({"error": "DB Error"}, status=500, headers={"Access-Control-Allow-Origin": "*"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

    # Ad Eligibility Check Handler
    async def check_ad_eligibility(request):
        """Check if user should see ad before leaderboard."""
        try:
            user_id_str = request.query.get("user_id")
            placement = request.query.get("placement", "leaderboard")
            
            if not user_id_str:
                return web.json_response(
                    {"show_ad": False, "reason": "no_user_id"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            from bot.handlers.ads import check_leaderboard_ad_eligibility
            
            user_id = int(user_id_str)
            user_data = await db.get_user(user_id)
            
            if not user_data:
                return web.json_response(
                    {"show_ad": False, "reason": "user_not_found"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            result = await check_leaderboard_ad_eligibility(user_id, user_data, db)
            
            return web.json_response(result, headers={"Access-Control-Allow-Origin": "*"})
        
        except Exception as e:
            logger.error(f"Ad eligibility check error: {e}")
            return web.json_response(
                {"show_ad": False, "reason": "error"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    # NOW create the app and register routes
    app = web.Application()
    
    # API Routes
    app.router.add_get("/api/user_data", get_user_data)
    app.router.add_options("/api/user_data", handle_options)
    app.router.add_get("/api/ghosts", get_ghosts_for_pack)
    app.router.add_options("/api/ghosts", handle_options)
    
    # Dummy Payment Route
    app.router.add_post("/api/simulate_payment", simulate_payment)
    app.router.add_options("/api/simulate_payment", handle_options_post)
    
    # Invoice Generation Route
    app.router.add_options('/api/create_invoice', handle_options)
    app.router.add_post('/api/create_invoice', create_invoice_api)
    
    # Ad Check Route
    app.router.add_get('/api/check_ad', check_ad_eligibility)
    app.router.add_options('/api/check_ad', handle_options)

    # Lead Capture Route
    app.router.add_options('/api/save_lead', handle_options)
    app.router.add_post('/api/save_lead', save_lead_api)

    # Redemption Route
    app.router.add_options('/api/redeem_stars', handle_options)
    app.router.add_post('/api/redeem_stars', redeem_stars)

    # Name Update Route
    app.router.add_options('/api/update_name', handle_options_post)
    app.router.add_post('/api/update_name', update_name_handler)

    # Ad Reward Route (New)
    app.router.add_options('/api/reward_ad', handle_options)
    app.router.add_post('/api/reward_ad', reward_ad_api)

    # --- SERVE STATIC WEB APP (New) ---
    # Serve index.html at root "/"
    async def serve_index(request):
        return web.FileResponse('./web_app/index.html', headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        })
    
    app.router.add_get("/", serve_index)
    
    # EXPLICITLY serve app_v2.js at root so <script src="app_v2.js"> works
    async def serve_js(request):
        return web.FileResponse('./web_app/app_v2.js', headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        })
    app.router.add_get("/app_v2.js", serve_js)

    # Serve other assets if needed (e.g. css, js) - mapping /web_app/ folder
    app.router.add_static('/web_app/', path='./web_app', name='web_app')

    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render provides PORT env var. Default to 8080 if missing.
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server started on port {port}")
    return site

async def keep_alive():
    """
    Pings the web server every 10 minutes to prevent Render from sleeping.
    """
    url = "https://elevateaura-bot.onrender.com" 
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(300) # 5 minutes (Render sleeps after 15)
            try:
                async with session.get(url) as response:
                    logger.info(f"Keep-alive ping status: {response.status}")
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {e}")

# --- NEW API: Unlock Premium with Code ---
async def unlock_premium_handler(request):
    try:
        data = await request.json()
        user_id = int(data.get("user_id"))
        secret_code = data.get("code")
        
        # Simple hardcoded check for MVP (or DB lookup)
        VALID_CODES = ["ELEVATE2025", "OFFICER", "PREMIUM7", "AURA100"]
        
        if secret_code in VALID_CODES:
            # Grant Premium
            success = await db.update_user_field(user_id, "is_premium", True)
            if success:
                 # Add 7 days to subscription
                 await db.update_subscription(user_id, 7) # hypothetical helper
                 return web.json_response({"success": True, "message": "Premium Unlocked for 7 Days!"})
        
        return web.json_response({"success": False, "error": "Invalid Code"})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

# --- NEW API: Update User Name ---
async def update_name_handler(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        new_name = data.get("full_name")
        
        if not user_id or not new_name:
             return web.json_response({"success": False, "error": "Missing Data"}, headers={"Access-Control-Allow-Origin": "*"})
             
        # Sanitize Name
        new_name = new_name.strip()[:50] # Cap at 50 chars
        
        # Update DB
        # We need to update 'full_name' in the users table
        # Using SupabaseClient's update method if available, or direct upsert
        
        # We can use the existing upsert logic, fetching current data first
        user_data = await db.get_user(user_id)
        if not user_data:
             return web.json_response({"success": False, "error": "User not found"}, headers={"Access-Control-Allow-Origin": "*"})
             
        # Preserve existing fields, update name
        user_data["full_name"] = new_name
        
        # Save back
        await db.upsert_user(user_data)
        
        return web.json_response({"success": True}, headers={"Access-Control-Allow-Origin": "*"})
        
    except Exception as e:
        print(f"Update Name API Error: {e}")
        return web.json_response({"success": False, "error": str(e)}, headers={"Access-Control-Allow-Origin": "*"})

# --- API: Get Rewarded Ad Status (Mock) ---
# --- Instance Lock ---
import os
import psutil
import socket
import sys

def prevent_multiple_instances():
    """
    Ensures only one instance of the bot is running by killing any old instances.
    """
    import psutil
    import time
    
    current_pid = os.getpid()
    killed_count = 0
    
    try:
        # Find all Python processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if it's a Python process running main.py
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('main.py' in str(arg) for arg in cmdline):
                        # Don't kill ourselves
                        if proc.info['pid'] != current_pid:
                            logger.info(f"Found old bot instance (PID: {proc.info['pid']}). Killing it...")
                            proc.kill()
                            killed_count += 1
                            time.sleep(0.5)  # Give it time to die
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.warning(f"Error while checking for old instances: {e}")
    
    if killed_count > 0:
        logger.info(f"✅ Killed {killed_count} old bot instance(s)")
    
    # Now acquire the lock
    try:
        # Create a socket that binds to localhost:12345
        # This global variable prevents the socket from being garbage collected
        global _lock_socket
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _lock_socket.bind(('127.0.0.1', 12345))
        logger.info("Instance Lock Acquired on Port 12345")
    except socket.error:
        print("\n\n❌ ERROR: Could not acquire instance lock (port 12345 still in use)")
        print("Waiting 2 seconds and retrying...\n")
        time.sleep(2)
        try:
            _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _lock_socket.bind(('127.0.0.1', 12345))
            logger.info("Instance Lock Acquired on Port 12345 (retry successful)")
        except socket.error:
            print("❌ ERROR: Still cannot acquire lock. Please manually kill old processes.\n")
            sys.exit(1)

# --- Main Entry Point ---
async def main():
    # 0. Acquire Lock
    prevent_multiple_instances()
    
    print("--- 🚀 BOT RELOADED! New Session Logic Active ---")
    logger.info("Starting Elevate Aura Bot v2.0 - With AI Coach...")
    print("Starting Elevate Aura Bot v2.0 - With AI Coach...")
    
    # Start Dummy Web Server (For Render) - Start this FIRST to satisfy port binding check
    web_site_ref = await start_web_server()
    
    # Start Keep-Alive Background Task
    asyncio.create_task(keep_alive())
    
    # Start Weekly Rewards Scheduler
    from bot.handlers.weekly_rewards import start_weekly_scheduler
    asyncio.create_task(start_weekly_scheduler(bot))
    logger.info("Weekly rewards scheduler started")
    
    # Start Subscription Notification Scheduler
    from bot.handlers.subscription_scheduler import start_subscription_notification_scheduler
    asyncio.create_task(start_subscription_notification_scheduler(bot))
    logger.info("Subscription notification scheduler started")
    
    # Verify DB connection
    connected = await db.connect()
    if not connected:
        logger.error("Failed to connect to Supabase. Check credentials.")

    logger.info("Bot is polling...")
    
    # Force logout any existing bot sessions (prevents Telegram conflicts)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Force logout successful - any zombie bot instances have been disconnected")
    except Exception as e:
        logger.warning(f"Could not force logout (may not be an issue): {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in .env file!")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
