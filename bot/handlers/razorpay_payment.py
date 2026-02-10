from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bot.services.razorpay_service import RazorpayService
from database.db_client import SupabaseClient
import logging
import uuid

router = Router()
logger = logging.getLogger(__name__)

# Initialize Service
razorpay_service = RazorpayService()

@router.message(Command("upgrade"))
async def cmd_upgrade(message: Message):
    """
    Show Premium Plans with Razorpay options.
    """
    text = (
        "💎 **ELEVATE AURA PREMIUM**\n\n"
        "Unlock the ultimate advantage:\n"
        "✅ **Detailed Analytics:** Know your weak spots.\n"
        "✅ **AI Coach:** Personalized daily study plans.\n"
        "✅ **Rank Insights:** See why you dropped.\n"
        "✅ **Zero Ads:** Pure focus.\n\n"
        "**Choose your plan:**"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Monthly Access - ₹99", callback_data="buy_premium_monthly")],
        [InlineKeyboardButton(text="🏆 Yearly Access - ₹999", callback_data="buy_premium_yearly")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("buy_premium_"))
async def cb_buy_premium(callback: CallbackQuery):
    """
    Generate Razorpay Link and show 'Pay Now' button.
    """
    user_id = callback.from_user.id
    plan_type = callback.data.split("_")[-1]  # monthly or yearly
    
    # Pricing
    if plan_type == "monthly":
        amount_paise = 9900  # ₹99.00
        desc = "Elevate Aura Premium - 1 Month"
    else:
        amount_paise = 99900 # ₹999.00
        desc = "Elevate Aura Premium - 1 Year"
        
    await callback.message.edit_text("🔄 **Generating secure payment link...**")
    
    # 1. Create unique internal order ID
    internal_ref = f"order_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # 2. Call Razorpay
    if not razorpay_service.client:
        await callback.message.edit_text("⚠️ Payment system is currently under maintenance. Please try again later.")
        return

    link_data = razorpay_service.create_payment_link(
        user_id=user_id,
        amount=amount_paise,
        description=desc,
        reference_id=internal_ref
    )
    
    if link_data and link_data.get("short_url"):
        payment_url = link_data.get("short_url")
        order_id = link_data.get("id") # Razorpay's link ID (plink_...)
        
        # 3. Save Order to DB
        db = SupabaseClient()
        await db.connect()
        
        order_record = {
            "order_id": order_id, # We use plink_ID as the primary key/order_id for tracking
            "user_id": user_id,
            "amount": amount_paise,
            "currency": "INR",
            "status": "created",
            "plan_type": plan_type
        }
        await db.create_payment_order(order_record)
        
        # 4. Show Payment Button
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Pay ₹{amount_paise/100:.0f} Securely", url=payment_url)],
            [InlineKeyboardButton(text="🔙 Cancel", callback_data="upgrade")]
        ])
        
        await callback.message.edit_text(
            f"✅ **Link Ready!**\n\n"
            f"Click below to pay via **UPI, Google Pay, PhonePe, or Card**.\n"
            f"_(The link opens in your secure browser)_\n\n"
            f"**Plan:** {desc}",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text("❌ Failed to generate link. Please contact support.")

