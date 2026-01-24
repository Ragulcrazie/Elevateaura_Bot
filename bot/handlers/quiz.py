from aiogram import Router, types, F
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import asyncio
import random
import time
from database.db_client import SupabaseClient

router = Router()

# MOCK DATA (Ideally loaded from DB or JSON file)
SAMPLE_QUESTIONS = [
    {
        "id": "q1",
        "question": "Only Conclusion I follows",
        "options": ["Only I", "Only II", "Both", "None"],
        "answer_index": 0,
        "explanation": "Simple logic..."
    },
    {
        "id": "q2",
        "question": "What is 20% of 500?",
        "options": ["50", "100", "200", "20"],
        "answer_index": 1,
        "explanation": "20% = 1/5. 500/5 = 100."
    }
]

# State management (Simple Dict for MVP - Use Redis/DB for Prod)
# State management (Simple Dict for MVP - Use Redis/DB for Prod)
user_states = {}
timer_tasks = {} # Stores asyncio tasks for timers

@router.message(Command("quiz"))
async def start_quiz_command(message: types.Message):
    await start_new_quiz_session(message, message.from_user.id)

@router.callback_query(F.data == "start_quiz_cmd")
async def start_quiz_callback(callback: types.CallbackQuery):
    await callback.answer()
    await start_new_quiz_session(callback.message, callback.from_user.id)

from bot.services.question_loader import loader
from database.db_client import SupabaseClient

async def start_new_quiz_session(message: types.Message, user_id: int):
    """
    Starts a daily quiz session.
    """
    # Fetch User Prefs
    db = SupabaseClient()
    await db.connect()
    user = await db.get_user(user_id)
    
    lang = "english"
    cat = "aptitude"
    
    if user:
        lang = user.get("language_pref", "english")
        # Ensure exam_category maps to our file keys (aptitude/reasoning/gk)
        user_cat = user.get("exam_category", "aptitude")
        if user_cat and user_cat.lower() in ["reasoning", "gk", "aptitude"]:
            cat = user_cat.lower()
        else:
            cat = "aptitude"

    # Fetch real questions
    questions = loader.get_questions(count=5, lang=lang, category=cat)
    
    if not questions:
        await message.answer(f"⚠️ No questions found for {lang.title()} {cat.title()}. Switching to English Aptitude.")
        questions = loader.get_questions(count=5, lang="english", category="aptitude")

    # 1. Initialize Session
    user_states[user_id] = {
        "score": 0,
        "current_q_index": 0,
        "questions": questions
    }
    
    await message.answer(f"🚀 **Starting Daily Quiz!**\n\n📝 **Topic**: {cat.title()} ({lang.title()})\n⏱️ **Questions**: 5", parse_mode="Markdown")
    await asyncio.sleep(1)
    await send_question(message, user_id)

async def update_timer_loop(message: types.Message, user_id: int, q_text: str, markup, options_str: str):
    """
    Updates the message at intervals to show visual timer.
    """
    try:
        # Phase 1: 15s elapsed (30s left)
        await asyncio.sleep(15)
        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 30s Left) 🟨🟨🟨⬜⬜\n{options_str}",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # Phase 2: 30s elapsed (15s left)
        await asyncio.sleep(15)
        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 15s Left) 🟧🟧⬜⬜⬜\n{options_str}",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # Phase 3: 40s elapsed (5s left)
        await asyncio.sleep(10)
        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 5s Left) 🟥⬜⬜⬜⬜\n⚡ **HURRY!**\n{options_str}",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # Phase 4: Time Up
        await asyncio.sleep(5)
        await message.edit_text(
            f"**Q**: {q_text}\n\n(❌ TIME UP) ⬛⬛⬛⬛⬛\n{options_str}",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except asyncio.CancelledError:
        # Task was cancelled (User Answered), do nothing
        pass
    except Exception as e:
        print(f"Timer Error: {e}")

async def send_question(message: types.Message, user_id: int):
    state = user_states.get(user_id)
    if not state: return

    idx = state["current_q_index"]
    questions = state["questions"]

    # End of Quiz
    if idx >= len(questions):
        await finish_quiz(message, user_id)
        return

    q = questions[idx]
    
    # Build Options Text
    options_str = ""
    for i, opt in enumerate(q["options"]):
        options_str += f"\n{i+1}. {opt}"

    # Build Keyboard (1, 2, 3, 4)
    builder = InlineKeyboardBuilder()
    for i in range(len(q["options"])):
        # Callback data format: "ans:index"
        builder.button(text=f"{i+1}", callback_data=f"ans:{i}")
    builder.adjust(4) # Equal width buttons

    # Start Timer
    state["question_start_time"] = time.time()

    msg = await message.answer(
        f"**Q{idx+1}: {q['question']}**\n(⏱️ 45s) 🟩🟩🟩🟩🟩\n{options_str}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

    # Allow msg to catch the new message object
    
    # Start Background Timer Task
    # Cancel previous if exists (safety)
    if user_id in timer_tasks:
        timer_tasks[user_id].cancel()
        
    task = asyncio.create_task(update_timer_loop(msg, user_id, f"Q{idx+1}: {q['question']}", builder.as_markup(), options_str))
    timer_tasks[user_id] = task

@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Cancel Timer Task immediately
    if user_id in timer_tasks:
        timer_tasks[user_id].cancel()
        del timer_tasks[user_id]
        
    state = user_states.get(user_id)
    if not state:
        await callback.answer("Session expired.", show_alert=True)
        return

    # Parse Answer
    selected_idx = int(callback.data.split(":")[1])
    current_q = state["questions"][state["current_q_index"]]
    correct_idx = current_q["answer_index"]

    # Logic
    is_correct = (selected_idx == correct_idx)
    if is_correct:
        state["score"] += 1
        feedback = "✅ **Correct!**"
    else:
        feedback = f"❌ **Wrong!**\nCorrect: {current_q['options'][correct_idx]}"

    # Update State
    state["current_q_index"] += 1
    
    # Calculate Time Taken
    start_time = state.get("question_start_time", time.time())
    time_taken = time.time() - start_time
    
    # Update DB (Async)
    db = SupabaseClient()
    await db.connect()
    # Ensure we don't block the UI response too much, but for now await is fine
    await db.update_user_stats(user_id, is_correct, time_taken)

    # Edit message to show result (Instant Feedback)
    await callback.message.edit_text(
        f"**Q{state['current_q_index']}: {current_q['question']}**\n\n"
        f"{feedback}\n\n"
        f"💡 **Explanation**: {current_q['explanation']}",
        parse_mode="Markdown"
    )

    # Next Question
    await asyncio.sleep(1.5) # Pause to read explanation
    # Note: We need the original 'message' object to send a new message.
    # callback.message is the message we just edited.
    await send_question(callback.message, user_id)
    await callback.answer()

async def finish_quiz(message: types.Message, user_id: int):
    state = user_states.get(user_id)
    score = state["score"]
    total = len(state["questions"])
    
    # Calculate Percentage
    percent = (score/total) * 100
    
    # Mock Competition Logic (The Illusion)
    # In real version, we query DB for specific ghost scores
    competitor_avg = random.randint(55, 75)
    beats_percentage = 0
    
    if percent > competitor_avg:
        beats_percentage = random.randint(80, 99)
        verdict = f"🌟 **Exceptional! You are in the top {100-beats_percentage}% of students.**"
    elif percent == competitor_avg:
        verdict = "📊 **Good job! You are at the industry average.**"
    else:
        verdict = "📉 **Below Average. The competition is tough today.**"

    msg = (
        f"🏁 **Quiz Finished!**\n\n"
        f"🏆 **Your Score**: {score}/{total} ({int(percent)}%)\n"
        f"👥 **Community Average**: {competitor_avg}%\n\n"
        f"{verdict}\n\n"
        f"**What's Next?** 👇"
    )

    # Post-Quiz Navigation
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Play Again", callback_data="start_quiz_cmd")
    builder.button(text="⚙️ Change Topic", callback_data="settings")
    # GitHub Pages URL (Case sensitive matches Repo Name)
    builder.button(text="🔥 Leaderboard", web_app=WebAppInfo(url="https://ragulcrazie.github.io/Elevateaura_Bot/"))
    builder.adjust(1)

    await message.answer(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")
    
    # Cleanup
    del user_states[user_id]
