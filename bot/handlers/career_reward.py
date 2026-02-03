"""
Career Consultation Reward System
Pay-per-lead generation through voluntary user data collection
"""

import logging
from aiogram import Router, types, F
from aiogram.types import CallbackQuery
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
async def collect_exam_category(callback: CallbackQuery):
    """
Step 2: Collect exam category, ask for SPECIFIC exam details (text input)
    """
    await callback.answer()
    
    exam_category = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # Store category in database
    db = SupabaseClient()
    await db.connect()
    metadata = {"career_form_state": {"exam_category": exam_category, "step": "awaiting_exam_details"}}
    await db.upsert_user({"user_id": user_id, "metadata": metadata})
    
    # Show examples based on category
    examples = {
        "SSC": "• SSC CGL Tier 1 2026\n• SSC CHSL 2026\n• SSC MTS Group C\n• SSC GD Constable",
        "RRB": "• RRB NTPC 2026\n• RRB Group D\n• RRB JE (Junior Engineer)\n• RRB ALP Technician",
        "BANK": "• IBPS PO Prelims 2026\n• SBI Clerk Mains\n• RBI Grade B Phase 1\n• IBPS RRB Officer",
        "POLICE": "• UP Police Constable 2026\n• SSC CPO SI 2026\n• Delhi Police Head Constable\n• CAPF Assistant Commandant",
        "OTHER": "• UPSC Prelims 2026\n• State PSC Exam\n• Teaching Exam (CTET/TET)\n• Any other competitive exam"
    }
    
    example_text = examples.get(exam_category, "• Specify your target exam")
    
    await callback.message.answer(
        f"📝 **Step 2/6: Specific Exam Details**\n\n"
        f"You selected: **{exam_category}**\n\n"
        f"Please type the **exact exam** you're preparing for:\n\n"
        f"**Examples:**\n{example_text}\n\n"
        f"💡 Include year and tier/stage if applicable\n"
        f"💡 Mention if it's your 1st or repeat attempt",
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("pref:"))
async def collect_preference(callback: CallbackQuery):
    """
    Step 4: Collect coaching preference, ask for city
    """
    await callback.answer()
    
    parts = callback.data.split(":")
    preference = parts[1]
    
    # Get existing form state
    db = SupabaseClient()
    await db.connect()
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.message.answer("❌ Error: User not found.")
        return
    
    metadata = user.get("metadata", {}) or {}
    form_state = metadata.get("career_form_state", {})
    form_state["preference"] = preference
    form_state["step"] = "awaiting_city"
    metadata["career_form_state"] = form_state
    await db.upsert_user({"user_id": user_id, "metadata": metadata})
    
    await callback.message.answer(
        "📍 **Step 5/6: Your Location**\n\n"
        "Please type your **city name** in the chat.\n\n"
        "Example: Mumbai, Delhi, Bangalore, etc.",
        parse_mode="Markdown"
    )


@router.message(F.text)
async def collect_text_inputs(message: types.Message):
    """
    Handle all text inputs: exam details, city, and phone number
    """
    user_id = message.from_user.id
    
    db = SupabaseClient()
    await db.connect()
    user = await db.get_user(user_id)
    
    if not user:
        return
    
    metadata = user.get("metadata", {}) or {}
    form_state = metadata.get("career_form_state", {})
    current_step = form_state.get("step")
    
    # Step 1: Collect specific exam details (after category selection)
    if current_step == "awaiting_exam_details":
        exam_details = message.text.strip()
        
        # Validate minimum length
        if len(exam_details) < 5:
            await message.answer(
                "❌ Please provide more details about your exam.\n\n"
                "Example: SSC CGL Tier 1 2026"
            )
            return
        
        # Save exam details
        form_state["exam_details"] = exam_details
        form_state["step"] = "exam_details_saved"
        metadata["career_form_state"] = form_state
        await db.upsert_user({"user_id": user_id, "metadata": metadata})
        
        # Ask for coaching preference
        builder = InlineKeyboardBuilder()
        builder.button(text="💻 Online Classes", callback_data="pref:ONLINE")
        builder.button(text="🏫 Offline Classes", callback_data="pref:OFFLINE")
        builder.button(text="🔄 Hybrid (Both)", callback_data="pref:HYBRID")
        builder.adjust(1)
        
        await message.answer(
            "👨‍🏫 **Step 3/6: Coaching Preference**\n\n"
            "What type of coaching do you prefer?",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    
    # Step 2: Collect city
    elif current_step == "awaiting_city":
        city = message.text.strip()
        
        # Validate city name
        if len(city) < 2:
            await message.answer(
                "❌ Please enter a valid city name.\n\n"
                "Example: Mumbai, Delhi, Bangalore"
            )
            return
        
        # Update state
        form_state["city"] = city
        form_state["step"] = "awaiting_phone"
        metadata["career_form_state"] = form_state
        await db.upsert_user({"user_id": user_id, "metadata": metadata})
        
        await message.answer(
            "📞 **Step 6/6: Contact Number**\n\n"
            "Please enter your **10-digit mobile number**.\n\n"
            "This will be used ONLY for career consultation callback.\n\n"
            "Example: 9876543210",
            parse_mode="Markdown"
        )
    
    # Step 3: Collect phone number
    elif current_step == "awaiting_phone":
        phone = message.text.strip()
        
        # Validate phone number (basic check)
        if not phone.isdigit() or len(phone) != 10:
            await message.answer(
                "❌ Invalid phone number. Please enter a valid 10-digit number.\n\n"
                "Example: 9876543210"
            )
            return
        
        # Show consent with all collected data
        builder = InlineKeyboardBuilder()
        builder.button(
            text="✅ I Agree - Submit Details",
            callback_data=f"consent_submit"  # We'll get data from database
        )
        builder.button(text="❌ Cancel", callback_data="cancel_reward")
        builder.adjust(1)
        
        # Store phone temporarily
        form_state["phone"] = phone
        metadata["career_form_state"] = form_state
        await db.upsert_user({"user_id": user_id, "metadata": metadata})
        
        await message.answer(
            "📋 **Final Step: Your Consent**\n\n"
            "**Summary of Details:**\n"
            f"• Exam Category: {form_state.get('exam_category', 'N/A')}\n"
            f"• Specific Exam: {form_state.get('exam_details', 'N/A')}\n"
            f"• Preference: {form_state.get('preference', 'N/A')}\n"
            f"• City: {form_state.get('city', 'N/A')}\n"
            f"• Phone: {phone}\n\n"
            "─────────────────────────────\n\n"
            "☐ **I agree to:**\n"
            "• Share my details with ElevateAura's coaching partners\n"
            "• Receive calls/messages for career guidance\n"
            "• Receive exclusive coaching offers and discounts\n\n"
            "✅ By clicking \"I Agree\", you consent to our Privacy Policy.\n\n"
            "Your data will be shared ONLY with verified educational institutes.",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "consent_submit")
async def save_lead_data(callback: CallbackQuery):
    """
    Final step: Save lead data to database with consent
    """
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Get all data from database
    db = SupabaseClient()
    await db.connect()
    
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("❌ Error: User not found.")
        return
    
    metadata = user.get("metadata", {}) or {}
    form_state = metadata.get("career_form_state", {})
    
    # Extract all collected data
    exam_category = form_state.get("exam_category", "")
    exam_details = form_state.get("exam_details", "")
    preference = form_state.get("preference", "")
    city = form_state.get("city", "")
    phone = form_state.get("phone", "")
    
    # Validate all fields are present
    if not all([exam_category, exam_details, preference, city, phone]):
        await callback.message.answer("❌ Error: Missing data. Please try again from the start.")
        return
    
    # Update metadata with lead submission
    metadata["lead_submitted"] = True
    metadata["lead_data"] = {
        "exam_category": exam_category,  # For categorization (SSC/Banking/etc)
        "exam_details": exam_details,     # Detailed exam info (SSC CGL Tier 1 2026)
        "preference": preference,
        "city": city,
        "phone": phone,
        "submitted_at": datetime.utcnow().isoformat(),
        "consent_given": True
    }
    metadata["career_form_state"] = {}  # Clear form state
    
    await db.upsert_user({"user_id": user_id, "metadata": metadata})
    
    logger.info(f"✅ Lead submitted by user {user_id}: {exam_category} -> {exam_details}, {preference}, {city}, {phone}")
    
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
