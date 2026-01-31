
from aiogram import Router, F, Bot
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from database.db_client import SupabaseClient
import logging
from datetime import datetime, timedelta

router = Router()

# CONFIG
PRICE_STARS = 89
PRODUCT_TITLE = "Elevate Aura Premium"

# Dynamic Description Logic
def get_product_description():
    import random
    # Base count 5291, add randomness to simulate live activity
    base_members = 5291
    # Simple consistent pseudo-randomness based on hour to slow-grow it
    growth = (datetime.now().day * 10) + datetime.now().hour
    current_members = base_members + growth
    
    return (
        "🔒 **WHAT PREMIUM USERS GET** (You Don't):\n\n"
        "🎯 **Exact Weak Spots** (स्किल गैप एनालिसिस)\n"
        "→ Know exactly which topics are killing your score.\n\n"
        "⏱ **Speed vs Accuracy** (Speed Analysis)\n"
        "→ Are you slow or just careless? See exact numbers.\n\n"
        "📉 **Rank Drop Reason** (रैंक क्यों गिरी?)\n"
        "→ Understand why your rank fell after every test.\n\n"
        "🤖 **24/7 AI Coach** (आपका पर्सनल मेंटर)\n"
        "→ Tells you what to revise TODAY, not someday.\n\n"
        "-----------------------------\n\n"
        "💸 **WHY 89 ⭐ IS NOTHING**:\n\n"
        "Let’s be honest (सच मानिए):\n"
        "❌ 1 Mock Test outside → ₹150+\n"
        "❌ 1 Coaching PDF → ₹99\n"
        "❌ Tea + Snack (चाय-नाश्ता) → ₹50\n\n"
        "✅ **Elevate Aura Premium → Only 89 Stars**\n"
        "👉 Less than a snack, but builds your career.\n\n"
        f"🔥 Join {current_members:,} elite aspirants now."
    )

# 1. Invoice Link Generator
async def generate_invoice_link(bot: Bot, user_id: int):
    return await bot.create_invoice_link(
        title=PRODUCT_TITLE,
        description=get_product_description(),
        payload=f"sub_1m_{user_id}",
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=[LabeledPrice(label="1 Month Access", amount=PRICE_STARS)],
    )

# 2. Pre-Checkout
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 3. Successful Payment (Subscription Logic)
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment = message.successful_payment
    user_id = message.from_user.id
    
    logging.info(f"💰 PAYMENT: {payment.total_amount} XTR from {user_id}")
    
    db = SupabaseClient()
    connected = await db.connect()
    
    if connected:
        # Calculate Expiry (Now + 30 Days)
        # In a real app, strict timezone handling is needed. simplified here.
        new_expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        # Update DB
        # We save 'premium' status AND the expiry date
        # If column doesn't exist yet, this might error, but we asked user to run SQL.
        try:
            db.client.from_("users").update({
                "subscription_status": "premium",
                "subscription_expiry": new_expiry
            }).eq("user_id", user_id).execute()
            
            await message.answer(
                "🎉 **PAYMENT SUCCESSFUL!**\n\n"
                "✅ **Premium Activated for 30 Days**\n"
                "Your access is valid until next month.\n\n"
                "Launch the Dashboard to see your new powers! 🚀"
            )
        except Exception as e:
            logging.error(f"DB Update Failed: {e}")
            await message.answer("⚠️ Payment received, but we couldn't update your status instantly. Contact Admin.")
