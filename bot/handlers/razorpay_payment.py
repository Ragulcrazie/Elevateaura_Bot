"""
Razorpay Payment Handler - Replaces Telegram Stars
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.razorpay_service import RazorpayService
from database.db_client import SupabaseClient
from bot.utils.logger import logger
import time

router = Router()
razorpay_service = RazorpayService()

@router.message(F.text == "/upgrade")
async def cmd_upgrade(message: Message):
    """
    Shows premium upgrade options with Razorpay payment links.
    """
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Monthly Premium (₹99)", callback_data="razorpay_monthly")],
        [InlineKeyboardButton(text="🔥 Yearly Premium (₹999)", callback_data="razorpay_yearly")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
    ])
    
    await message.answer(
        "🚀 **Unlock Premium Features!**\n\n"
        "✅ Ad-Free Experience\n"
        "✅ AI Performance Coach\n"
        "✅ Detailed Analytics\n"
        "✅ Priority Support\n\n"
        "**Choose your plan:**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "razorpay_monthly")
async def process_monthly_payment(callback: CallbackQuery):
    """Generates Razorpay link for monthly subscription"""
    await callback.answer()
    await _generate_payment_link(callback, plan="monthly", amount=9900, description="Monthly Premium")

@router.callback_query(F.data == "razorpay_yearly")
async def process_yearly_payment(callback: CallbackQuery):
    """Generates Razorpay link for yearly subscription"""
    await callback.answer()
    await _generate_payment_link(callback, plan="yearly", amount=99900, description="Yearly Premium")

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    """Cancels the payment flow"""
    await callback.answer("Payment cancelled", show_alert=True)
    await callback.message.delete()

async def _generate_payment_link(callback: CallbackQuery, plan: str, amount: int, description: str):
    """
    Helper function to generate Razorpay payment link and save order to database.
    
    Args:
        callback: Callback query
        plan: "monthly" or "yearly"
        amount: Amount in paise
        description: Payment description
    """
    user_id = callback.from_user.id
    
    # Check if Razorpay is configured
    if not razorpay_service.client:
        await callback.message.edit_text(
            "⚠️ **Payment System Unavailable**\n\n"
            "Please contact support.",
            parse_mode="Markdown"
        )
        return
    
    # Generate unique reference ID
    reference_id = f"user_{user_id}_{int(time.time())}"
    
    # Create payment link
    link_data = razorpay_service.create_payment_link(
        user_id=user_id,
        amount=amount,
        description=f"Elevate Aura {description}",
        reference_id=reference_id
    )
    
    if not link_data or not link_data.get("short_url"):
        await callback.message.edit_text(
            "❌ **Failed to generate payment link**\n\n"
            "Please try again later.",
            parse_mode="Markdown"
        )
        return
    
    payment_url = link_data.get("short_url")
    order_id = link_data.get("id")
    
    # Save order to database
    db = SupabaseClient()
    await db.connect()
    
    order_record = {
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "currency": "INR",
        "status": "created",
        "plan_type": plan
    }
    
    await db.create_payment_order(order_record)
    
    # Send payment link to user
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay Now", url=payment_url)],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
    ])
    
    await callback.message.edit_text(
        f"🔐 **Secure Payment Link Generated**\n\n"
        f"**Plan:** {description}\n"
        f"**Amount:** ₹{amount/100:.0f}\n\n"
        f"Click the button below to complete your payment securely via Razorpay.\n\n"
        f"✅ Your subscription will be activated automatically once payment is confirmed.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    logger.info(f"💳 Payment link generated for user {user_id}: {plan} (₹{amount/100})")
