# Elevate Aura Bot - Technical & Functional Documentation

## 1. Project Overview
**Elevate Aura** is a high-performance, gamified Telegram bot designed for competitive exam aspirants (SSC, RRB, Banking). It combines daily practice quizzes with a "Smart Rivalry" leaderboard system, an AI Performance Coach, and a virtual economy to drive engagement and sustainable monetization.

- **Bot Username:** `@ElevateAura_Bot`
- **Primary Goal:** Convert free users to Premium subscribers through "Smart FOMO" and tangible value (AI insights, Ad-free experience).
- **Languages:** English, Hindi (Bilingual Support).

---

## 2. Technical Architecture

### Core Stack
- **Languages:** Python 3.12+
- **Framework:** `Aiogram 3.x` (Asynchronous Telegram handling)
- **Database:** `Supabase` (PostgreSQL)
- **Web Server:** `aiohttp` (For Web App API, Health Checks, and Razorpay Webhooks)
- **Frontend:** HTML5, TailwindCSS, Vanilla JS (Telegram Mini App)

### Directory Structure
- `bot/handlers/`: Feature-specific logic (Quiz, Payment, AI, Ads).
- `bot/services/`: Core business logic (Rank Engine, Ad Service, Subscription).
- `database/`: SQL schemas and `SupabaseClient` wrapper.
- `assets/`: JSON question banks and static resources.
- `web_app/`: Frontend code for the Leaderboard/Dashboard Mini App.

---

## 3. Core Feature Analysis

### A. The Quiz Engine (`bot/handlers/quiz.py`)
The heart of the bot. Uniquely designed to prevent burnout while ensuring daily habits.
- **Daily Limit:** Strict cap of **60 Questions (6 Tests)** per day for ALL users to maintain quality over quantity.
- **Freemium Limit:** Free users are hard-stopped after **3 Lifetime Tests** (30 questions). They *must* upgrade to continue.
- **Scoring:** 
  - +10 Points per correct answer.
  - Time taken is tracked to milliseconds for "Pace" calculation.
- **Data Source:** Questions loaded from optimized JSON files in `assets/questions` via `QuestionLoader`.

### B. "Smart Rivalry" Rank Engine (`bot/services/rank_engine.py`)
A sophisticated pseudo-multiplayer engine that creates a lively, competitive environment without needing thousands of concurrent users.
- **Ghost Players:** The system generates 49 "Ghost" profiles to populate the leaderboard.
- **Realistic Activity:** Ghosts follow a "Daily Slot Progress" (e.g., they are less active at 4 AM, highly active at 8 PM).
- **Psychological Hooks:**
  - **God Mode:** Top 3 ghosts are sometimes unbeatable to prevent easy wins.
  - **Hope Spot:** If a user is losing badly, ghosts "slow down" significantly to keep the user engaged.
  - **Rivalry:** Ghosts specifically target the user's score to stay "neck-and-neck".

### C. Subscription & Economy (`bot/services/subscription_service.py`)
A comprehensive monetization layer built around "Aura Stars" (Virtual Currency).
- **Plans:** 
  - Monthly: ₹99 (99 Stars)
  - Yearly: ₹999 (999 Stars)
- **Wallet System:** Users earn Stars via referrals or weekly wins.
- **Loyalty Discount:** Users can use their Wallet Balance to get up to **50% OFF** on renewals.
- **Expiry Logic:** Strict 30-day cycle. 
  - **Warning:** Automated message sent 24 hours before expiry.
  - **Downgrade:** Instant switch to Free tier (Ads enabled, AI disabled) upon expiry.

### D. AI Performance Coach (`bot/services/ai_service.py`)
Premium-exclusive feature providing actionable insights.
- **Intelligence Gap:** logic identifies "weak spots" (e.g., Geometry, Syllogisms) based on quiz performance.
- **Advice Bank:** Delivers specific "Shortcuts", "Common Mistakes", and "Psychological Hacks" mapped to the user's weak topics.
- **Local Database:** Uses `integrated_ai_data.json` for rapid, offline-capable responses.

### E. Ad Monetization (`bot/services/ad_service.py`)
Hybrid ad system using **Monetag**.
- **Placements:** 
  - Post-Quiz (Interstitial text/link).
  - Pre-Leaderboard (Web App Interstitial).
- **Rules:** 
  - **Premium users NEVER see ads.**
  - Frequency capping (Max 6 ads/day).
  - Global cooldowns (Minimum 2 minutes between ads).

---

## 4. User Journeys

### The "Freemium Trap" (Conversion Path)
1. **Acquisition:** User starts bot, takes 1st Quiz. (Delight phase).
2. **Habit:** Completes 3rd Quiz. (Hook phase).
3. **Wall:** Attempts 4th Quiz → **Paywall Triggered**.
   - *Message:* "You've hit your limit! 500+ students are racing ahead."
   - *Social Proof:* "Top player just won ₹600."
4. **Action:** User pays ₹99 via Razorpay.
5. **Reward:** Instant unlock + "Welcome Bonus" (Scholarship Ticket).

### The "Weekly Grand Prix" (Retention Path)
1. **Monday:** Leaderboard resets. Everyone starts at 0.
2. **Mon-Sat:** Users grind quizzes to build "Weekly Score".
3. **Sunday 10 PM:** Top 10 winners announced.
4. **Prize:** Top 3 get "Virtual Cash" (e.g., ₹600 credits) usable *only* for subscription renewals.
   - *Legal Safety:* Credits assume no real-world monetary value, ensuring compliance with gambling laws (similar to Dream11 free leagues).

---

## 5. Web App & Frontend (`web_app/index.html`)

The Mini App serves as the user's dashboard.
- **Intelligence Gap Analysis:** Visualizes "Current Score" vs "True Potential" to highlight missed opportunities.
- **Lead Capture:** "Elite Scholar Detected" modal activates for top 15% users to collect high-quality leads (Phone, Exam Goal) for coaching upsells.
- **Wallet Vault:** Displays virtual balance and offers "Withdrawal" (paused for compliance) and "Redeem Premium" options.

---

## 6. Key Value Propositions (Use in Marketing)

1.  **"Stop Guessing. Start Competing."**
    *   *Why:* The Smart Rivalry engine makes practice feel like a sport.
2.  **"Your Personal AI Coach"**
    *   *Why:* It doesn't just grade you; it tells you *how* to fix your specific mistakes.
3.  **"Earn Your Subscription"**
    *   *Why:* The Weekly Grand Prix allows skilled users to effectively use the platform for free by winning renewals.
4.  **"Bilingual seamlessness"**
    *   *Why:* Switch languages instantly without losing progress.

---

## 7. Deployment Notes

- **Environment Variables:** Requires `BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`.
- **Database:** Requires Supabase with `users`, `quiz_sessions`, `payment_orders`, `ghost_profiles`, and `ad_impressions` tables.
- **Hosting:** Python bot on Render/Heroku + Static Web App (GitHub Pages or similar).
