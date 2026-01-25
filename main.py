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
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Check Leaderboard (Web App)", web_app=WebAppInfo(url="https://ragulcrazie.github.io/Elevateaura_Bot/web_app/"))
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
            
            return web.json_response({
                "full_name": user_data.get("full_name", "Unknown Aspirant"),
                "total_score": user_data.get("current_streak", 0), # Score is now stored accurately
                "questions_answered": user_data.get("questions_answered", 0),
                "pack_id": pack_id,
                "average_pace": user_data.get("average_pace", 0) # Format: 12.5
            }, headers={"Access-Control-Allow-Origin": "*"})
        else:
            return web.json_response({"error": "User not found"}, status=404, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logger.error(f"API Error: {e}")
        return web.json_response({"error": "Internal Server Error"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/api/user_data", get_user_data)
    app.router.add_options("/api/user_data", handle_options)
    
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

# --- Main Entry Point ---
async def main():
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
