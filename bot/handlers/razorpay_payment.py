"""
Razorpay Payment Handler - Replaces Telegram Stars
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.razorpay_service import RazorpayService
from database.db_client import SupabaseClient
import logging
import time

logger = logging.getLogger(__name__)

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
    user_id = callback.from_user.id
    
    # Check if first-time or renewal
    db = SupabaseClient()
    await db.connect()
    user_data = await db.get_user(user_id)
    
    is_first_time = not user_data.get("last_payment_date")
    wallet_balance = user_data.get("wallet_stars", 0) or 0
    
    # Monthly: Need ₹50 wallet for 50% discount
    can_use_discount = (not is_first_time) and (wallet_balance >= 50)
    
    if can_use_discount:
        # Renewal with 50% discount
        amount = 4900  # ₹49
        description = "Monthly Premium (50% OFF)"
        wallet_to_deduct = 50
        await _generate_payment_link(callback, plan="monthly", amount=amount, description=description, 
                                     wallet_bonus=wallet_to_deduct, original_price=99)
    else:
        # First-time or insufficient wallet
        amount = 9900  # ₹99
        if is_first_time:
            description = "Monthly Premium (First Month)"
            message_suffix = "\n\n💡 **Next renewal:** Earn ₹50 in wallet for 50% OFF!"
        else:
            description = "Monthly Premium"
            needed = 50 - wallet_balance
            message_suffix = f"\n\n💡 **Tip:** Earn ₹{needed} more for 50% OFF next time!"
        
        await _generate_payment_link(callback, plan="monthly", amount=amount, description=description, 
                                     wallet_bonus=0, original_price=99, extra_message=message_suffix)

@router.callback_query(F.data == "razorpay_yearly")
async def process_yearly_payment(callback: CallbackQuery):
    """Generates Razorpay link for yearly subscription"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Check if first-time or renewal
    db = SupabaseClient()
    await db.connect()
    user_data = await db.get_user(user_id)
    
    is_first_time = not user_data.get("last_payment_date")
    wallet_balance = user_data.get("wallet_stars", 0) or 0
    
    # Yearly: Need ₹500 wallet for 50% discount
    can_use_discount = (not is_first_time) and (wallet_balance >= 500)
    
    if can_use_discount:
        # Renewal with 50% discount
        amount = 49900  # ₹499
        description = "Yearly Premium (50% OFF)"
        wallet_to_deduct = 500
        await _generate_payment_link(callback, plan="yearly", amount=amount, description=description, 
                                     wallet_bonus=wallet_to_deduct, original_price=999)
    else:
        # First-time or insufficient wallet
        amount = 99900  # ₹999
        if is_first_time:
            description = "Yearly Premium (First Year)"
            message_suffix = "\n\n💡 **Next renewal:** Earn ₹500 in wallet for 50% OFF!"
        else:
            description = "Yearly Premium"
            needed = 500 - wallet_balance
            message_suffix = f"\n\n💡 **Tip:** Earn ₹{needed} more for 50% OFF next time!"
        
        await _generate_payment_link(callback, plan="yearly", amount=amount, description=description, 
                                     wallet_bonus=0, original_price=999, extra_message=message_suffix)


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    """Cancels the payment flow"""
    await callback.answer("Payment cancelled", show_alert=True)
    await callback.message.delete()

async def _generate_payment_link(callback: CallbackQuery, plan: str, amount: int, description: str, 
                                 wallet_bonus: int = 0, original_price: int = 0, extra_message: str = ""):
    """
    Helper function to generate Razorpay payment link and save order to database.
    
    Args:
        callback: Callback query
        plan: "monthly" or "yearly"
        amount: Amount in paise (what user pays via Razorpay)
        description: Payment description
        wallet_bonus: Amount to deduct from wallet (in rupees, not paise)
        original_price: Original price before discount (for display)
        extra_message: Additional message to show user
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
        "plan_type": plan,
        "wallet_bonus_used": wallet_bonus  # Store for webhook processing
    }
    
    await db.create_payment_order(order_record)
    
    # Send payment link to user
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay Now", url=payment_url)],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
    ])
    
    # Build message based on discount
    if wallet_bonus > 0:
        message = (
            f"🎉 **{description}**\n\n"
            f"**Original Price:** ~₹{original_price}~ ₹{original_price}\n"
            f"**Razorpay Payment:** ₹{amount/100:.0f}\n"
            f"**Wallet Bonus:** -₹{wallet_bonus}\n"
            f"**Total Savings:** ₹{wallet_bonus} (50% OFF!)\n\n"
            f"Click below to pay ₹{amount/100:.0f} via Razorpay.\n"
            f"₹{wallet_bonus} will be deducted from your wallet automatically.\n\n"
            f"✅ Premium activates instantly after payment!"
        )
    else:
        message = (
            f"🔐 **Secure Payment Link Generated**\n\n"
            f"**Plan:** {description}\n"
            f"**Amount:** ₹{amount/100:.0f}\n\n"
            f"Click the button below to complete your payment securely via Razorpay.\n\n"
            f"✅ Your subscription will be activated automatically once payment is confirmed."
            f"{extra_message if extra_message else ''}"
        )
    
    await callback.message.edit_text(
        message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    logger.info(f"💳 Payment link: user {user_id}, {plan}, ₹{amount/100} (wallet: ₹{wallet_bonus})")
