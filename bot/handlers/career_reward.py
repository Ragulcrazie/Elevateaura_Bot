"""
Career Consultation Reward System
Pay-per-lead generation through voluntary user data collection
"""

import logging
from aiogram import Router, types, F
from aiogram.filters.callback_query import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db_client import SupabaseClient
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

# --- TRIGGER LOGIC ---

async def check_reward_eligibility(user_id: int, score: int, total_questions: int) -> bool:
    """
    Check if user qualifies for career consultation reward.
    
    Criteria:
    - Score >= 8/10 (80%)
    - Has NOT already claimed reward
    
    Returns: True if eligible, False otherwise
    """
    db = SupabaseClient()
    await db.connect()
    
    user = await db.get_user(user_id)
    if not user:
        return False
    
    # Check if already claimed
    metadata = user.get("metadata", {}) or {}
    already_claimed = metadata.get("lead_submitted", False)
    
    if already_claimed:
        return False
    
    # Check score threshold (80% or higher)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    if percentage >= 80:
        logger.info(f"User {user_id} qualifies for reward! Score: {score}/{total_questions} ({percentage}%)")
        return True
    
    return False


async def show_reward_notification(message: types.Message, user_id: int):
    """
    Show persistent reward notification to eligible users.
    Called after quiz completion when user qualifies.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🎁 Claim Your Reward", callback_data=f"claim_reward:{user_id}")
    
    await message.answer(
        "🏆 **CONGRATULATIONS!**\n\n"
        "🎉 You've unlocked a **CAREER CONSULTATION REWARD** for being a top performer!\n\n"
        "**Your Reward Includes:**\n"
        "✅ FREE Career Guidance Session\n"
        "✅ Exclusive Coaching Discounts (up to 30%)\n"
        "✅ Priority Access to Study Materials\n"
        "✅ Free Demo Classes from Top Institutes\n\n"
        "👇 **Claim now to connect with expert mentors!**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


# --- CALLBACK HANDLERS ---

@router.callback_query(F.data.startswith("claim_reward:"))
async def start_reward_claim(callback: CallbackQuery):
    """
    Step 1: Show intro message and start data collection
    """
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Check if already claimed
    db = SupabaseClient()
    await db.connect()
    user = await db.get_user(user_id)
    
    if not user:
        await callback.message.answer("❌ Error: User not found. Please contact support.")
        return
    
    metadata = user.get("metadata", {}) or {}
    if metadata.get("lead_submitted", False):
        await callback.message.answer(
            "✅ You've already claimed your reward!\n\n"
            "Our career team will contact you soon.",
            parse_mode="Markdown"
        )
        return
    
    # Show exam selection
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 SSC", callback_data="exam:SSC")
    builder.button(text="🚂 Railway (RRB)", callback_data="exam:RRB")
    builder.button(text="🏦 Banking", callback_data="exam:BANK")
    builder.button(text="👮 Police/Defense", callback_data="exam:POLICE")
    builder.button(text="📚 Other", callback_data="exam:OTHER")
    builder.adjust(2)
    
    await callback.message.answer(
        "🎯 **Step 1/4: Target Exam**\n\n"
        "Which exam are you preparing for?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("exam:"))
async def collect_exam(callback: CallbackQuery):
    """
    Step 2: Collect target exam, ask for coaching preference
    """
    await callback.answer()
    
    exam_type = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # Store in temporary state (you can use a dict or database)
    # For now, we'll pass it forward in callback data
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💻 Online Classes", callback_data=f"pref:ONLINE:{exam_type}")
    builder.button(text="🏫 Offline Classes", callback_data=f"pref:OFFLINE:{exam_type}")
    builder.button(text="🔄 Hybrid (Both)", callback_data=f"pref:HYBRID:{exam_type}")
    builder.adjust(1)
    
    await callback.message.answer(
        "👨‍🏫 **Step 2/4: Coaching Preference**\n\n"
        "What type of coaching do you prefer?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("pref:"))
async def collect_preference(callback: CallbackQuery):
    """
    Step 3: Collect coaching preference, ask for city
    """
    await callback.answer()
    
    parts = callback.data.split(":")
    preference = parts[1]
    exam_type = parts[2]
    
    # Ask for city via text input
    builder = InlineKeyboardBuilder()
    builder.button(text="📍 Enter City", callback_data=f"ask_city:{preference}:{exam_type}")
    
    await callback.message.answer(
        "📍 **Step 3/4: Your Location**\n\n"
        "Please type your **city name** in the chat.\n\n"
        "Example: Mumbai, Delhi, Bangalore, etc.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    
    # Store state to expect city input next
    db = SupabaseClient()
    await db.connect()
    user_id = callback.from_user.id
    metadata = {"career_form_state": {"exam": exam_type, "preference": preference, "step": "awaiting_city"}}
    await db.upsert_user({"user_id": user_id, "metadata": metadata})


@router.message(F.text)
async def collect_city_and_phone(message: types.Message):
    """
    Step 4: Collect city (text input), then ask for phone
    """
    user_id = message.from_user.id
    
    db = SupabaseClient()
    await db.connect()
    user = await db.get_user(user_id)
    
    if not user:
        return
    
    metadata = user.get("metadata", {}) or {}
    form_state = metadata.get("career_form_state", {})
    
    # Check if we're expecting city input
    if form_state.get("step") == "awaiting_city":
        city = message.text.strip()
        
        # Update state
        form_state["city"] = city
        form_state["step"] = "awaiting_phone"
        metadata["career_form_state"] = form_state
        await db.upsert_user({"user_id": user_id, "metadata": metadata})
        
        await message.answer(
            "📞 **Step 4/4: Contact Number**\n\n"
            "Please enter your **10-digit mobile number**.\n\n"
            "This will be used ONLY for career consultation callback.\n\n"
            "Example: 9876543210",
            parse_mode="Markdown"
        )
    
    # Check if we're expecting phone input
    elif form_state.get("step") == "awaiting_phone":
        phone = message.text.strip()
        
        # Validate phone number (basic check)
        if not phone.isdigit() or len(phone) != 10:
            await message.answer(
                "❌ Invalid phone number. Please enter a valid 10-digit number.\n\n"
                "Example: 9876543210"
            )
            return
        
        # Show consent checkbox
        builder = InlineKeyboardBuilder()
        builder.button(
            text="✅ I Agree - Submit Details",
            callback_data=f"consent:{form_state['exam']}:{form_state['preference']}:{form_state['city']}:{phone}"
        )
        builder.button(text="❌ Cancel", callback_data="cancel_reward")
        builder.adjust(1)
        
        await message.answer(
            "📋 **Final Step: Your Consent**\n\n"
            "**Summary of Details:**\n"
            f"• Exam: {form_state.get('exam', 'N/A')}\n"
            f"• Preference: {form_state.get('preference', 'N/A')}\n"
            f"• City: {form_state.get('city', 'N/A')}\n"
            f"• Phone: {phone}\n\n"
            "─────────────────────────────\n\n"
            "☐ **I agree to:**\n"
            "• Share my details with ElevateAura's coaching partners\n"
            "• Receive calls/messages for career guidance\n"
            "• Receive exclusive coaching offers and discounts\n\n"
            "✅ By clicking \"I Agree\", you consent to our [Privacy Policy](/privacy).\n\n"
            "Your data will be shared ONLY with verified educational institutes.",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("consent:"))
async def save_lead_data(callback: CallbackQuery):
    """
    Final step: Save lead data to database with consent
    """
    await callback.answer()
    
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    
    if len(parts) < 5:
        await callback.message.answer("❌ Error: Invalid data. Please try again.")
        return
    
    exam = parts[1]
    preference = parts[2]
    city = parts[3]
    phone = parts[4]
    
    # Save to database
    db = SupabaseClient()
    await db.connect()
    
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("❌ Error: User not found.")
        return
    
    # Update metadata with lead submission
    metadata = user.get("metadata", {}) or {}
    metadata["lead_submitted"] = True
    metadata["lead_data"] = {
        "exam": exam,
        "preference": preference,
        "city": city,
        "phone": phone,
        "submitted_at": datetime.utcnow().isoformat(),
        "consent_given": True
    }
    metadata["career_form_state"] = {}  # Clear form state
    
    await db.upsert_user({"user_id": user_id, "metadata": metadata})
    
    logger.info(f"✅ Lead submitted by user {user_id}: {exam}, {preference}, {city}, {phone}")
    
    # Success message
    await callback.message.answer(
        "🎉 **REWARD CLAIMED SUCCESSFULLY!**\n\n"
        "✅ Your details have been submitted.\n\n"
        "**What Happens Next:**\n"
        "📞 Our career team will contact you within 24-48 hours\n"
        "🎓 You'll receive personalized coaching recommendations\n"
        "💰 Exclusive discounts (up to 30% off)\n"
        "🆓 Free demo class invitations\n\n"
        "**Note:** If you wish to stop receiving calls, contact us at /support\n\n"
        "Thank you for being a top performer! 🏆",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "cancel_reward")
async def cancel_reward_claim(callback: CallbackQuery):
    """
    Cancel the reward claim process
    """
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Clear form state
    db = SupabaseClient()
    await db.connect()
    user = await db.get_user(user_id)
    
    if user:
        metadata = user.get("metadata", {}) or {}
        metadata["career_form_state"] = {}
        await db.upsert_user({"user_id": user_id, "metadata": metadata})
    
    await callback.message.answer(
        "❌ Reward claim cancelled.\n\n"
        "You can claim it anytime by scoring 8/10 or higher in a quiz!",
        parse_mode="Markdown"
    )
