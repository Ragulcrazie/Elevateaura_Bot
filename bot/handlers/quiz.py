from aiogram import Router, types, F
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import asyncio
import random
import time
import uuid
import re
from database.db_client import SupabaseClient

router = Router()

def format_explanation(text: str) -> str:
    """
    Formats the explanation by adding newlines and bolding 'Step X'.
    """
    if not text: return "No explanation available."
    # Regex: Find 'Step <number>:' and replace with '\n\n**Step <number>:**'
    # We use a lambda to process the match if needed, but simple substitution works here.
    # The pattern (Step \d+:) captures the whole string.
    formatted = re.sub(r'(Step \d+:)', r'\n\n**\1**', text)
    
    # Remove duplicate numbering pattern like "**Step 1:** 1:" -> "**Step 1:**"
    formatted = re.sub(r'(\*\*Step \d+:\*\*) \d+:', r'\1', formatted)
    
    # If no steps were found (formatting didn't change length significantly), 
    # try splitting by sentences for readability.
    if len(formatted) == len(text):
        # Replace ". " with ".\n\n" using regex to handle spacing
        formatted = re.sub(r'\. +', '.\n\n', text)
        
    return formatted.strip()

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
# State management (Hybrid: RAM + DB persistence)
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
from bot.services.session_manager import session_manager
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

    # 0. Check Daily Limit (Robust JSONB Logic)
    quiz_state = user.get("quiz_state") or {}
    saved_stats = quiz_state.get("stats", {})
    
    # Priority: JSONB > Schema > Score-Derivation
    q_answered_json = saved_stats.get("questions_answered")
    
    if q_answered_json is not None:
        # Trust the JSON value (even if 0, trust it!)
        q_answered = q_answered_json
    else:
        # Fallback: Check old columns or derive from score
        db_val = user.get("questions_answered")
        if db_val:
            q_answered = db_val
        else:
             # Last Resort: Derive from Score (Migration for old users)
             q_answered = int(user.get("current_streak", 0) / 10)
    
    # Check Date from JSONB or Metadata
    metadata = user.get("metadata", {}) or {}
    last_active = saved_stats.get("last_active_date") or metadata.get("last_active_date", "")
    
    today_str = db.get_ist_date()
    
    if last_active != today_str:
        # It's a new day, so 0 questions answered today
        q_answered = 0

    remaining = 60 - q_answered
    if remaining <= 0:
        await message.answer("🛑 **Daily Limit Reached!**\n\nYou have completed your 60 questions for today. Come back tomorrow for a fresh leaderboard challenge!", parse_mode="Markdown")
        return

    # Cap at 10 or remaining quota
    questions_to_load = min(10, remaining)

    # Fetch real questions
    questions = loader.get_questions(count=questions_to_load, lang=lang, category=cat)
    
    if not questions:
        await message.answer(f"⚠️ No questions found for {lang.title()} {cat.title()}. Switching to English Aptitude.")
        questions = loader.get_questions(count=min(5, remaining), lang="english", category="aptitude")

    print(f"DEBUG: Initializing session for {user_id}")
    
    # 0.5 Kill Zombie Timers (Safety First)
    if user_id in timer_tasks:
        timer_tasks[user_id].cancel()
        del timer_tasks[user_id]
        print(f"DEBUG: Cancelled existing timer for {user_id}")
    
    # 1. Initialize Session
    session_id = str(uuid.uuid4())[:8] # Short 8-char ID
    state = {
        "score": 0,
        "current_q_index": 0,
        "questions": questions,
        "question_start_time": 0,
        "questions_answered_baseline": q_answered, # Snapshot of DB at start
        "session_id": session_id
    }
    
    # Save State to Disk (Robust Persistence)
    await session_manager.save_session(user_id, state)
    
    start_range = q_answered + 1
    end_range = min(q_answered + len(questions), 60)
    await message.answer(f"🚀 **Starting Daily Quiz!**\n\n📝 **Topic**: {cat.title()} ({lang.title()})\n⏱️ **Questions**: {len(questions)} (Progress: {start_range}-{end_range} / 60)", parse_mode="Markdown")
    await asyncio.sleep(1)
    print(f"DEBUG: Calling send_question for {user_id}")
    await send_question(message, user_id)

async def update_timer_loop(message: types.Message, user_id: int, q_text: str, markup, options_str: str, q_index: int, mode="Markdown"):
    """
    Updates the message at intervals. Checks DB/Session state to self-destruct if obsolete.
    """
    try:
        # Helper to check if we should stop
        async def should_stop():
            state = await session_manager.get_session(user_id)
            if not state: return True
            # If user has moved to next question (index changed), we are obsolete
            if state.get("current_q_index") != q_index:
                print(f"DEBUG: Smart Timer for Q{q_index+1} self-destructing (Current: {state.get('current_q_index')})")
                return True
            return False

        # Phase 1: 15s elapsed (30s left)
        await asyncio.sleep(15)
        if await should_stop(): return
        
        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 30s Left) 🟨🟨🟨⬜⬜\n{options_str}" if mode else f"Q: {q_text}\n\n(⏱️ 30s Left) 🟨🟨🟨⬜⬜\n{options_str}",
            reply_markup=markup,
            parse_mode=mode
        )
        
        # Phase 2: 30s elapsed (15s left)
        await asyncio.sleep(15)
        if await should_stop(): return

        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 15s Left) 🟧🟧⬜⬜⬜\n{options_str}" if mode else f"Q: {q_text}\n\n(⏱️ 15s Left) 🟧🟧⬜⬜⬜\n{options_str}",
            reply_markup=markup,
            parse_mode=mode
        )
        
        # Phase 3: 40s elapsed (5s left)
        await asyncio.sleep(10)
        if await should_stop(): return

        await message.edit_text(
            f"**Q**: {q_text}\n\n(⏱️ 5s Left) 🟥⬜⬜⬜⬜\n⚡ **HURRY!**\n{options_str}" if mode else f"Q: {q_text}\n\n(⏱️ 5s Left) 🟥⬜⬜⬜⬜\n⚡HURRY!\n{options_str}",
            reply_markup=markup,
            parse_mode=mode
        )
        
        # Phase 4: Time Up
        await asyncio.sleep(5)
        if await should_stop(): return

        # Remove buttons (None markup)
        await message.edit_text(
            f"**Q**: {q_text}\n\n(❌ TIME UP) ⬛⬛⬛⬛⬛\n{options_str}" if mode else f"Q: {q_text}\n\n(❌ TIME UP) ⬛⬛⬛⬛⬛\n{options_str}",
            reply_markup=None,
            parse_mode=mode
        )
        
        # Trigger Timeout Logic
        await handle_timeout(message, user_id)

    except asyncio.CancelledError:
        # Task was cancelled (User Answered), do nothing
        pass
    except Exception as e:
        print(f"Timer Error: {e}")

async def handle_timeout(message: types.Message, user_id: int):
    """
    Handles logic when user fails to answer in time.
    """
    # 1. Clear task reference
    if user_id in timer_tasks:
        del timer_tasks[user_id]
        
    # state = user_states.get(user_id)
    state = await session_manager.get_session(user_id)
    
    if not state: return

    # 2. Get Data for Feedback (Do this FIRST)
    current_q = state["questions"][state["current_q_index"]]
    correct_idx = current_q["answer_index"]
    
    # 3. Send Feedback (UI Priority)
    try:
        # ALWAYS use explanation_full, NEVER use short explanation
        raw_expl = current_q.get("explanation_full", "")
        if not raw_expl or len(raw_expl.strip()) == 0:
            raw_expl = "[ERROR: Full explanation missing for this question. Please report this issue.]"
        expl = format_explanation(raw_expl)
        
        # DEBUG: Log which field was used
        with open('explanation_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"\n=== TIMEOUT - Q ID: {current_q.get('id')} ===\n")
            f.write(f"  explanation_full length: {len(current_q.get('explanation_full', ''))}\n")
            f.write(f"  explanation length: {len(current_q.get('explanation', ''))}\n")
            f.write(f"  raw_expl length: {len(raw_expl)}\n")
            f.write(f"  Formatted length: {len(expl)}\n")
            f.write(f"  Full content (first 500 chars):\n{expl[:500]}\n")


        try:
            await message.answer(
                f"❌ **Time Up!**\nCorrect: {current_q['options'][correct_idx]}\n\n"
                f"💡 **Explanation**: {expl}",
                parse_mode="Markdown"
            )
        except Exception as markdown_error:
            # Markdown parsing failed, try plain text
            print(f"Markdown error (timeout) for Q{current_q.get('id')}: {markdown_error}")
            with open('explanation_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"  MARKDOWN ERROR (TIMEOUT): {str(markdown_error)}\n")
            
            try:
                # Retry without Markdown
                await message.answer(
                    f"✗ Time Up!\nCorrect: {current_q['options'][correct_idx]}\n\n"
                    f"Explanation: {expl.replace('**', '')}",
                    parse_mode=None
                )
            except Exception as plain_error:
                print(f"Plain text also failed (timeout): {plain_error}")
                # Last resort
                await message.answer(
                    f"Time up! Correct answer: {current_q['options'][correct_idx]}\n"
                    f"Explanation: {expl.replace('**', '')}",
                    parse_mode=None
                )
    except Exception as e:
        print(f"Feedback Error: {e}")

    # 4. Update DB (Backend - Try/Except to not block flow)
    # 4. Update DB (Backend - Try/Except to not block flow)
    try:
        # Calculate Forced Count
        baseline = state.get("questions_answered_baseline", 0)
        forced_count = baseline + state["current_q_index"] + 1

        db = SupabaseClient()
        await db.connect()
        new_stats = await db.update_user_stats(user_id, is_correct=False, time_taken=45.0, forced_count=forced_count)
        if new_stats:
             state["stats"] = new_stats
    except Exception as e:
        print(f"DB Error in Timeout: {e}")
    
    # 5. Next Question (Always Proceed)
    state["current_q_index"] += 1
    await session_manager.save_session(user_id, state)
    
    await asyncio.sleep(1.5)
    await send_question(message, user_id, state=state)

async def send_question(message: types.Message, user_id: int, state: dict = None):
    # Retrieve State (if not provided)
    if not state:
        state = await session_manager.get_session(user_id)
    
    if not state: 
        print(f"DEBUG: No session found for {user_id}")
        return

    idx = state["current_q_index"]
    print(f"DEBUG: Current Index: {idx}")
    questions = state["questions"]

    # End of Quiz
    if idx >= len(questions):
        await finish_quiz(message, user_id, state=state)
        return

    q = questions[idx]
    
    # Build Options Text
    options_str = ""
    for i, opt in enumerate(q["options"]):
        options_str += f"\n{i+1}. {opt}"

    # Build Keyboard (1, 2, 3, 4)
    builder = InlineKeyboardBuilder()
    current_session_id = state.get("session_id", "nosession")
    for i in range(len(q["options"])):
        # Callback data format: "ans:index:session_id"
        builder.button(text=f"{i+1}", callback_data=f"ans:{i}:{current_session_id}")
    builder.adjust(4) # Equal width buttons

    # Start Timer
    state["question_start_time"] = time.time()
    await session_manager.save_session(user_id, state)

    msg = None
    used_mode = "Markdown"
    try:
        # Try sending with Markdown
        msg = await message.answer(
            f"**Q{idx+1}: {q['question']}**\n(⏱️ 45s) 🟩🟩🟩🟩🟩\n{options_str}",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"DEBUG: Markdown send failed: {e}. Retrying plain text.")
        try:
            # Fallback to Plain Text (removes ** bolding)
            fallback_text = f"Q{idx+1}: {q['question']}\n(⏱️ 45s) 🟩🟩🟩🟩🟩\n{options_str}"
            msg = await message.answer(
                fallback_text,
                reply_markup=builder.as_markup(),
                parse_mode=None
            )
            used_mode = None
        except Exception as e2:
             print(f"DEBUG: Plain text send failed: {e2}")
             return

    # Allow msg to catch the new message object
    if not msg: return
    
    # Start Background Timer Task
    # Cancel previous if exists (safety)
    if user_id in timer_tasks:
        timer_tasks[user_id].cancel()
        
    task = asyncio.create_task(update_timer_loop(msg, user_id, f"Q{idx+1}: {q['question']}", builder.as_markup(), options_str, q_index=idx, mode=used_mode))
    timer_tasks[user_id] = task

# Lock to prevent rapid double-clicks
processing_lock = set()

@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in processing_lock:
        print(f"DEBUG: Ignoring double-click from {user_id}")
        return

    processing_lock.add(user_id)
    try:
        # 1. Stop Loading Spinner Immediately
        await callback.answer()
        
        print(f"DEBUG: Handling answer for {callback.from_user.id}")
        
        # Cancel Timer Task immediately
        if user_id in timer_tasks:
            timer_tasks[user_id].cancel()
            del timer_tasks[user_id]
            print(f"DEBUG: Timer cancelled for {user_id}")
            
        # Retrieve State
        print(f"DEBUG: Fetching session for {user_id}")
        state = await session_manager.get_session(user_id)
        if not state:
            # Debugging Info for User
            debug_info = f"ID: {user_id}\nDB Check Failed (Start a new quiz with /quiz)"
            print(f"DEBUG: Session Lookup Failed. {debug_info}")
            await callback.answer(f"Session Error:\n{debug_info}", show_alert=True)
            return
        
        print(f"DEBUG: Session found for {user_id}")

        # Check for TIMEOUT (Logical Check)
        start_time = state.get("question_start_time", 0)
        # Allow 2s grace for network latency
        if time.time() - start_time > 47: 
            await callback.answer("Time limit exceeded!", show_alert=True)
            await handle_timeout(callback.message, user_id)
            return

        # Parse Call Data
        parts = callback.data.split(":")
        
        # Session Validation (Zombie Check 🧟)
        if len(parts) == 3:
            incoming_sid = parts[2]
            current_sid = state.get("session_id")
            if current_sid and incoming_sid != current_sid:
                print(f"DEBUG: Session mismatch for {user_id}. Incoming: {incoming_sid}, Current: {current_sid}")
                await callback.answer("⚠️ Session Expired!\nYou have a newer quiz active.", show_alert=True)
                return
        
        # Parse Answer
        selected_idx = int(parts[1])
        current_q = state["questions"][state["current_q_index"]]
        # DEBUG: Print keys to verify data availability
        print(f"DEBUG ANSWER KEYS: {list(current_q.keys())}")
        print(f"DEBUG EXPLANATION FULL: {current_q.get('explanation_full', 'MISSING')[:20]}...")
        
        correct_idx = current_q["answer_index"]

        # Logic
        is_correct = (selected_idx == correct_idx)
        if is_correct:
            state["score"] += 10 # 10 Points per question
            feedback = "✅ **Correct!**"
        else:
            feedback = f"❌ **Wrong!**\nCorrect: {current_q['options'][correct_idx]}"

        # Update State in DB
        state["current_q_index"] += 1
        
        # Calculate Time Taken
        start_time = state.get("question_start_time", time.time())
        time_taken = time.time() - start_time
        
        # Calculate Forced Count (Session Truth)
        baseline = state.get("questions_answered_baseline", 0)
        # We are answering the question at 'current_q_index'. 
        # Example: Baseline 10. Index 0 (Q1). Count = 10 + 0 + 1 = 11.
        forced_count = baseline + state["current_q_index"] + 1

        # Update DB Stats & Sync to Session
        db = SupabaseClient()
        await db.connect()
        new_stats = await db.update_user_stats(user_id, is_correct, time_taken, forced_count=forced_count)
        
        if new_stats:
            state["stats"] = new_stats
        
        # Update Session
        await session_manager.save_session(user_id, state)

        # Edit message to show result (Instant Feedback)
        # ALWAYS use explanation_full, NEVER use short explanation
        raw_expl = current_q.get("explanation_full", "")
        if not raw_expl or len(raw_expl.strip()) == 0:
            raw_expl = "[ERROR: Full explanation missing for this question. Please report this issue.]"
        expl = format_explanation(raw_expl)
        
        # DEBUG: Log which field was used
        with open('explanation_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"\n=== ANSWER - Q ID: {current_q.get('id')} ===\n")
            f.write(f"  explanation_full length: {len(current_q.get('explanation_full', ''))}\n")
            f.write(f"  explanation length: {len(current_q.get('explanation', ''))}\n")
            f.write(f"  raw_expl length: {len(raw_expl)}\n")
            f.write(f"  Formatted length: {len(expl)}\n")
            f.write(f"  Full content (first 500 chars):\n{expl[:500]}\n")


        try:
            await callback.message.edit_text(
                f"**Q{state['current_q_index']}: {current_q['question']}**\n\n"
                f"{feedback}\n\n"
                f"💡 **Explanation**: {expl}",
                parse_mode="Markdown"
            )
        except Exception as markdown_error:
            # Markdown parsing failed, try plain text
            print(f"Markdown error for Q{current_q.get('id')}: {markdown_error}")
            with open('explanation_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"  MARKDOWN ERROR: {str(markdown_error)}\n")
            
            try:
                # Retry without Markdown
                await callback.message.edit_text(
                    f"Q{state['current_q_index']}: {current_q['question']}\n\n"
                    f"{feedback.replace('**', '').replace('✅', '✓').replace('❌', '✗')}\n\n"
                    f"Explanation: {expl.replace('**', '')}",
                    parse_mode=None
                )
            except Exception as plain_error:
                print(f"Plain text also failed: {plain_error}")
                # Last resort: show minimal message
                await callback.message.edit_text(
                    f"Answer recorded. See explanation in next message."
                )
                # Send explanation as separate message
                await callback.message.answer(
                    f"Explanation for Q{state['current_q_index']}:\n{expl.replace('**', '')}",
                    parse_mode=None
                )

        # Next Question
        await asyncio.sleep(1.5) # Pause to read explanation
        # Note: We need the original 'message' object to send a new message.
        # callback.message is the message we just edited.
        await send_question(callback.message, user_id, state=state)
        # await callback.answer() # Moved to top
        
    except Exception as e:
        print(f"CRITICAL ERROR in handle_answer: {e}")
        import traceback
        traceback.print_exc()
        try:
            await callback.answer(f"Bot Error: {e}", show_alert=True)
        except:
             pass
    finally:
        processing_lock.remove(user_id)

async def finish_quiz(message: types.Message, user_id: int, state: dict = None):
    if not state:
        state = await session_manager.get_session(user_id)
    if not state: return

    score = state["score"]
    total = len(state["questions"])
    
    # Calculate Percentage (Score is now out of 100 for 10 Qs)
    # Total Score Possible = 10 * 10 = 100
    percent = (score/100) * 100 
    if percent > 100: percent = 100 # Safety
    
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
        f"🏆 **Your Score**: {score} pts ({int(percent)}%)\n"
        f"👥 **Community Average**: {competitor_avg}%\n\n"
        f"{verdict}\n\n"
        f"**What's Next?** 👇"
    )

    # Post-Quiz Navigation
    # Dynamic Web App URL
    from urllib.parse import quote
    full_name = message.from_user.full_name # Get full_name from the message object
    name_param = quote(full_name) if full_name else "Fighter"
    web_app_url = f"https://ragulcrazie.github.io/Elevateaura_Bot/web_app/?user_id={user_id}&name={name_param}"

    # Dynamic Button Label & Final Consistency Check
    # We calculate true total locally to ignore any last-moment DB failures
    baseline = state.get("questions_answered_baseline", 0)
    final_q_answered = baseline + total
    
    # Force update the stats object to ensure next session picks up where we left off
    if "stats" not in state: state["stats"] = {}
    state["stats"]["questions_answered"] = final_q_answered
    
    # Calculate next range
    next_start = final_q_answered + 1
    next_end = final_q_answered + 10
    
    start_btn_text = f"🔄 Next: Q{next_start}-{next_end} / 60"
    if final_q_answered >= 60:
        start_btn_text = "✅ Daily Goal Completed"

    builder = InlineKeyboardBuilder()
    builder.button(text=start_btn_text, callback_data="start_quiz_cmd")
    builder.button(text="⚙️ Change Topic", callback_data="settings")
    builder.button(text="🔥 Leaderboard", web_app=WebAppInfo(url=web_app_url))
    builder.adjust(1)

    await message.answer(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")
    
    # Cleanup - Pass the corrected stats
    await session_manager.delete_session(user_id, keep_stats=state["stats"])
