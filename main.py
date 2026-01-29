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
dp.include_router(quiz_router)
dp.include_router(payment_router)
dp.include_router(prefs_router)
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
    await db.upsert_user(user_data)
    
    # 2. Send Welcome Message
    # Create Layout
    from urllib.parse import quote
    safe_name = quote(full_name)
    import time
    timestamp = int(time.time())
    web_app_url = f"https://ragulcrazie.github.io/Elevateaura_Bot/web_app/?user_id={user_id}&name={safe_name}&v={timestamp}"

    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Check Leaderboard (v54)", web_app=WebAppInfo(url=web_app_url))
    builder.button(text="📝 Start Quiz", callback_data="start_quiz_cmd") # Shortcuts
    builder.button(text="⚙️ Language & Topic", callback_data="settings")
    builder.adjust(1)
    
    await message.answer(
        f"👋 **Hello {full_name}! Welcome to Elevate Aura.**\n\n"
        "🚀 **Your Goal**: Prove your worth in the Daily Quiz Arena.\n"
        "⚔️ **Your Competition**: 500+ Active Aspirants are competing right now.\n\n"
        "👇 **Open your Dashboard to see Ranks & Stats:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
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
        user_data = await db.get_user(int(user_id))
        if user_data:
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
            
            # --- DAILY RESET LOGIC (VIEW ONLY) ---
            if last_active != today_str:
                # New day, but user hasn't played yet. Return 0 stats.
                derived_q_answered = 0
                db_pace = 0
                daily_score = 0
                weak_spots = {}
                potential_score = 0
            else:
                # Same day, use saved stats
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
            final_weak_spots = processed_weak_spots if (last_active == today_str) else []
            
            return web.json_response({
                "full_name": user_data.get("full_name", "Unknown Aspirant"),
                "total_score": daily_score, 
                "questions_answered": derived_q_answered,
                "pack_id": pack_id,
                "average_pace": db_pace,
                "subscription_status": user_data.get("subscription_status", "free"),
                "language": user_data.get("language_pref", "english"),
                "potential_score": potential_score,
                "weak_spots": final_weak_spots
            }, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "User not found"}, status=404, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logger.error(f"API Error: {e}")
        return web.json_response({"error": "Internal Server Error"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def get_ghosts_for_pack(request):
    try:
        pack_id = request.query.get("pack_id")
        user_id_str = request.query.get("user_id")
        
        if not pack_id:
            return web.json_response({"error": "Missing pack_id"}, status=400, headers={"Access-Control-Allow-Origin": "*"})
        
        # 1. Fetch User Score for "Psychological" Logic
        user_score = 0
        if user_id_str:
            try:
                user_data = await db.get_user(int(user_id_str))
                if user_data:
                    # Check if score is from today
                    today_str = db.get_ist_date()
                    quiz_state = user_data.get("quiz_state") or {}
                    saved_stats = quiz_state.get("stats", {})
                    if saved_stats.get("last_active_date") == today_str:
                        user_score = saved_stats.get("daily_score", 0)
            except:
                pass # Fail silently, treat as 0

        # 2. Fetch Raw Ghosts (Seed based)
        import datetime
        # Use IST day for seeding to keep ghosts consistent for the whole day
        now = rank_engine.get_ist_time()
        # Seed key: Year + DayOfYear + PackID
        # We rotate ghosts daily now instead of weekly to ensure "fresh" feeling?
        # User said "everyday midnight 00:00 the leader board should refresh".
        # If we keep same ghosts for week, their scores reset daily. That's fine.
        week_num = now.isocalendar()[1]
        year = now.year
        
        seed_val = int(f"{year}{week_num}{pack_id}")
        
        TOTAL_GHOSTS = 10000 
        start_index = seed_val % (TOTAL_GHOSTS - 60)
        
        response = db.client.table("ghost_profiles").select("*").range(start_index, start_index + 48).execute()
        raw_ghosts = response.data if response.data else []
        
        # 3. Process Scores via RankEngine
        processed_ghosts = rank_engine.generate_ghost_data(raw_ghosts, user_score)
        
        return web.json_response({"ghosts": processed_ghosts}, headers={"Access-Control-Allow-Origin": "*"})
        
    except Exception as e:
        logger.error(f"Failed to fetch ghosts: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})

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

async def handle_options_post(request):
     return web.Response(headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/api/user_data", get_user_data)
    app.router.add_options("/api/user_data", handle_options)
    app.router.add_get("/api/ghosts", get_ghosts_for_pack)
    app.router.add_options("/api/ghosts", handle_options)
    
    # Dummy Payment Route
    app.router.add_post("/api/simulate_payment", simulate_payment)
    app.router.add_options("/api/simulate_payment", handle_options_post)
    
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
    logger.info("Starting Elevate Aura Bot...")
    
    # Start Dummy Web Server (For Render) - Start this FIRST to satisfy port binding check
    web_site_ref = await start_web_server()
    
    # Start Keep-Alive Background Task
    asyncio.create_task(keep_alive())
    
    # Verify DB connection
    connected = await db.connect()
    if not connected:
        logger.error("Failed to connect to Supabase. Check credentials.")

    logger.info("Bot is polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in .env file!")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
