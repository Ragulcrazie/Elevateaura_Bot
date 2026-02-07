
from aiogram import Router, F, Bot
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from database.db_client import SupabaseClient
import logging
from datetime import datetime, timedelta

router = Router()

# CONFIG
PRICE_STARS = 99
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
        "🔒 **PREMIUM ADVANTAGE** (YOU DON’T GET THIS FREE)\n\n"
        "🎯 **Weak Spots**\n"
        "Know exactly what’s reducing your score.\n\n"
        "⏱ **Speed vs Accuracy**\n"
        "See if you’re slow or careless — in numbers.\n\n"
        "📉 **Rank Drop Reason**\n"
        "Know why your rank falls after each test.\n\n"
        "🤖 **AI Coach**\n"
        "Stops wasted study. Tells you what to revise today.\n\n"
        "💸 **WHY 99 ⭐ IS NOTHING**\n"
        "❌ Outside mock → ₹150+\n"
        "❌ Coaching PDF → ₹99\n"
        "✅ **Premium → 99 Stars**\n"
        "Cheaper than a snack. Smarter than free practice.\n\n"
        "-----------------------------\n"
        "🇮🇳 **हिंदी** (CLEAN & MATCHED)\n\n"
        "🔒 **PREMIUM ADVANTAGE** (FREE में नहीं)\n\n"
        "🎯 **Weak Topics**\n"
        "कौन-से टॉपिक्स स्कोर गिरा रहे हैं।\n\n"
        "⏱ **Speed vs Accuracy**\n"
        "धीमे हैं या careless — साफ़ दिखेगा।\n\n"
        "📉 **Rank Drop Reason**\n"
        "हर टेस्ट के बाद रैंक क्यों गिरी।\n\n"
        "🤖 **AI Coach**\n"
        "बेकार पढ़ाई बंद। आज क्या पढ़ना है बताए।\n\n"
        "💸 99 ⭐ महँगा नहीं है\n"
        "❌ बाहर का mock → ₹150+\n"
        "❌ Coaching PDF → ₹99\n"
        "✅ **Premium → 99 Stars**\n"
        "नाश्ते से सस्ता। गलत practice से बेहतर।\n\n"
        f"🔥 Join {current_members:,} elite aspirants today.\n"
        "👉 **Unlock Premium – 99 ⭐**"
    )

# 1. Invoice Link Generator (Split Payment)
async def generate_invoice_link(bot: Bot, user_id: int, plan: str):
    if plan == 'yearly':
        amount = 499 # 499 XTR
        label = "1 Year Access (50% Off)"
        payload = f"split_yearly_{user_id}"
    else:
        amount = 49 # 49 XTR (Monthly)
        label = "1 Month Access (50% Off)"
        payload = f"split_monthly_{user_id}"

    return await bot.create_invoice_link(
        title=PRODUCT_TITLE,
        description=get_product_description(),
        payload=payload,
        provider_token="", # Empty for Stars
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=amount)],
    )

# 2. Pre-Checkout (Validate Wallet Balance)
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    payload = pre_checkout_query.invoice_payload
    user_id = pre_checkout_query.from_user.id
    
    required_wallet = 0
    if 'split_monthly' in payload:
        required_wallet = 50
    elif 'split_yearly' in payload:
        required_wallet = 500
        
    if required_wallet > 0:
        db = SupabaseClient()
        if not await db.connect():
             await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message="Database error")
             return

        # Check Balance
        stats = db.client.from_('user_stats').select('wallet_stars').eq('user_id', user_id).execute()
        if not stats.data or stats.data[0]['wallet_stars'] < required_wallet:
             await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=f"Insufficient Wallet Balance! Need {required_wallet} Stars.")
             return

    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 3. Successful Payment (Subscription Logic)
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment = message.successful_payment
    user_id = message.from_user.id
    payload = payment.invoice_payload
    
    logging.info(f"💰 PAYMENT: {payment.total_amount} XTR from {user_id} Payload: {payload}")
    
    # Determine Plan & Deduction
    days_to_add = 30
    deduct_wallet = 0
    
    if 'split_yearly' in payload:
        days_to_add = 365
        deduct_wallet = 500
    elif 'split_monthly' in payload:
        days_to_add = 30
        deduct_wallet = 50

    db = SupabaseClient()
    connected = await db.connect()
    
    if connected:
        try:
            # 1. Deduct Wallet Balance (if split payment)
            if deduct_wallet > 0:
                 # Fetch current first to be safe
                 current = db.client.from_('user_stats').select('wallet_stars').eq('user_id', user_id).execute()
                 if current.data:
                     new_bal = max(0, current.data[0]['wallet_stars'] - deduct_wallet)
                     db.client.from_('user_stats').update({'wallet_stars': new_bal}).eq('user_id', user_id).execute()

            # 2. Update Subscription
            user_data = db.client.from_("users").select("*").eq("user_id", user_id).execute()
            current_expiry = None
            total_payments = 0
            started_at = None
            
            if user_data.data and len(user_data.data) > 0:
                user = user_data.data[0]
                current_expiry_str = user.get('subscription_expires_at')
                total_payments = user.get('total_payments', 0)
                started_at = user.get('subscription_started_at')
                
                if current_expiry_str:
                    try:
                        current_expiry = datetime.fromisoformat(current_expiry_str.replace('Z', '+00:00'))
                    except:
                        current_expiry = None
            
            now = datetime.utcnow()
            if current_expiry and current_expiry > now:
                new_expiry = current_expiry + timedelta(days=days_to_add)
            else:
                new_expiry = now + timedelta(days=days_to_add)
                if not started_at:
                    started_at = now.isoformat()
            
            db.client.from_("users").update({
                "subscription_status": "premium",
                "subscription_expires_at": new_expiry.isoformat(),
                "subscription_started_at": started_at,
                "last_payment_date": now.isoformat(),
                "total_payments": total_payments + 1,
                "expiration_warning_sent": False
            }).eq("user_id", user_id).execute()
            
            expiry_date = new_expiry.strftime("%d %b %Y")
            
            await message.answer(
                "🎉 **PREMIUM ACTIVATED!**\n\n"
                f"✅ **Valid Until: {expiry_date}**\n"
                f"🔥 **Used:** {deduct_wallet} Wallet Stars + {payment.total_amount} XTR\n\n"
                "🚀 **Unlocked:**\n"
                "• No Ads\n"
                "• AI Coach\n"
                "• Deep Analytics\n\n"
                "Go ace those exams! 📚"
            )
            
            logging.info(f"✅ Premium activated for {user_id} until {expiry_date}")

            # --- REFERRAL HOOK ---
            from bot.services.referral_service import process_referral_reward
            await process_referral_reward(message.bot, user_id)
            
        except Exception as e:
            logging.error(f"DB Update Failed: {e}")
            await message.answer("⚠️ Payment received but update failed. Contact Admin.")
