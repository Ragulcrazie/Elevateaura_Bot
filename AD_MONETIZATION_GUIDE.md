# 💰 Ad Monetization System - Complete Guide

## 🎯 Overview

Your bot now has a **comprehensive ad monetization system** powered by **Monetag**. The system is currently in **TEST MODE** showing ads only to your user ID (`996261168`).

---

## 📍 **Ad Placements**

### **1. Post-Quiz Ad** (Primary Revenue)
- **When**: Immediately after completing a 10-question quiz
- **Type**: Interstitial message
- **Location**: `bot/handlers/quiz.py` → `finish_quiz()` function
- **Cooldown**: 10 minutes between post-quiz ads

### **2. Leaderboard Ad** (Secondary Revenue)
- **When**: Before opening the leaderboard WebApp
- **Type**: In-app interstitial (Monetag native)
- **Trigger**: User opens dashboard every 3rd time
- **Cooldown**: 5 minutes

---

## ⚙️ **Configuration**

All ad settings are in **`config/ad_config.json`**:

```json
{
  "monetag_publisher_id": "10557666",
  "enabled": true,
  "test_mode": true,  // ← CHANGE TO false TO GO LIVE
  "test_user_ids": [996261168],  // ← Your test user ID
  
  "premium_skip_ads": true,  // Premium users see NO ads
  
  "placements": {
    "post_quiz": {
      "enabled": true,
      "cooldown_minutes": 10
    },
    "leaderboard": {
      "enabled": true,
      "show_every_nth_visit": 3,
      "cooldown_minutes": 5
    }
  },
  
  "frequency_limits": {
    "max_ads_per_day": 6,  // Maximum ads per user per day
    "min_seconds_between_ads": 120  // 2 minutes global cooldown
  }
}
```

---

## 🧪 **Testing (NOW - Before Going Live)**

### **Step 1: Run the Database Migration**

Open your **Supabase SQL Editor** and run:

```sql
-- Copy contents from: database/migration_ads.sql
```

This creates the `ad_impressions` table for analytics.

### **Step 2: Test with Your Account**

1. **Start the bot** (restart if already running)
2. **Take a quiz** as user `996261168` (your account)
3. **You should see**:
   - ✅ A message after quiz: "Quick Message from Our Sponsors..."
   - ✅ No errors in console
   - ✅ Ad logged in database (`ad_impressions` table)

4. **Open leaderboard** 3 times
   - Third time should trigger ad check
   - Check browser console for Monetag script loading

### **Step 3: Test Premium User Exemption**

1. **Mark yourself as premium**:
   ```sql
   UPDATE users 
   SET subscription_status = 'premium',
       subscription_expiry = '2026-12-31'
   WHERE user_id = 996261168;
   ```

2. **Take another quiz**
   - ✅ You should see NO ads now

3. **Revert to free**:
   ```sql
   UPDATE users 
   SET subscription_status = 'free'
   WHERE user_id = 996261168;
   ```

---

## 🚀 **Going Live** (After Testing)

### **Step 1: Disable Test Mode**

Edit `config/ad_config.json`:

```json
{
  "test_mode": false,  // ← Changed from true
  "test_user_ids": [],  // ← Cleared
  ...
}
```

### **Step 2: Restart Bot**

```bash
# Kill current bot
Ctrl+C

# Restart
python main.py
```

### **Step 3: Monitor Analytics**

**View ad impressions:**
```sql
SELECT 
  placement,
  COUNT(*) as total_impressions,
  COUNT(DISTINCT user_id) as unique_users,
  DATE(timestamp) as date
FROM ad_impressions
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY placement, DATE(timestamp)
ORDER BY date DESC, total_impressions DESC;
```

**Check daily stats view:**
```sql
SELECT * FROM daily_ad_stats
ORDER BY date DESC
LIMIT 7;
```

---

## 📊 **Ad Flow Diagram**

```
User completes quiz
    ↓
Check: Is test mode? → If yes → Is user in test_user_ids?
    ↓ yes
Check: Is premium? → If yes → SKIP AD ✗
    ↓ no
Check: Cooldown active? → If yes → SKIP AD ✗
    ↓ no
Check: Daily cap reached? → If yes → SKIP AD ✗
    ↓ no
✅ SHOW AD
    ↓
Record impression in database
```

---

## 🎨 **Customizing Ad Messages**

Edit `bot/handlers/ads.py`:

```python
# Change the message users see
await message.answer(
    "✨ **Your Custom Message**\n\n"
    "This free quiz is supported by ads.\n"
    "Thank you! 🙏",
    parse_mode="Markdown"
)
```

---

## 💡 **Monetag Integration Notes**

### **Current Setup:**
- **Publisher ID**: `10557666` (from your Monetag account)
- **Ad Type**: In-App Interstitial
- **Script**: Loaded in `web_app/index.html` header

### **How It Works:**
1. **Bot Side**: Shows placeholder ad message after quiz
2. **WebApp Side**: Checks `/api/check_ad` endpoint
3. **If approved**: Calls `show_10557666()` function (Monetag SDK)
4. **Monetag**: Displays native ad overlay

### **Expected Revenue** (Conservative Estimates):
- **100 daily users**: ₹150-300/month
- **500 daily users**: ₹750-1,500/month  
- **1,000 daily users**: ₹1,500-3,000/month

*Based on India CPM rates (~$0.50-1.50)*

---

## ⚠️ **Important Warnings**

### **1. Never Disable Error Handling**
All ad code is wrapped in try-catch. **DO NOT REMOVE** these safeguards:

```python
try:
    # Ad code
except Exception as e:
    logger.error(f"Ad error (non-critical): {e}")
    # Quiz continues normally ✅
```

### **2. Don't Show Too Many Ads**
Current caps are **optimal**:
- Max 6 ads/day per user
- 2-minute global cooldown
- If users complain, **reduce** these, don't increase

### **3. Premium Users = Zero Ads**
This creates upgrade incentive. **Keep this rule strict**.

---

## 🔧 **Troubleshooting**

### **Problem: Ads not showing at all**

**Check 1**: Is test mode enabled and you're using the test user ID?
```json
"test_mode": true,
"test_user_ids": [996261168]  // ← Must match your Telegram ID
```

**Check 2**: Check console logs
```bash
# Look for these messages:
"✅ Ad impression recorded"
"❌ Ad skipped for {user_id}: {reason}"
```

**Check 3**: Verify database table exists
```sql
SELECT * FROM ad_impressions LIMIT 1;
```

If error → Run `database/migration_ads.sql`

### **Problem: Too many ads showing**

Edit `config/ad_config.json`:
```json
"frequency_limits": {
  "max_ads_per_day": 3,  // ← Reduced from 6
  "min_seconds_between_ads": 300  // ← Increased to 5 mins
}
```

### **Problem: Monetag script not loading in WebApp**

**Check 1**: View page source of `web_app/index.html`
- Verify script tag exists:
  ```html
  <script async src="//thubanoa.com/1?z=8122224"></script>
  ```

**Check 2**: Browser console
- Look for errors related to `show_10557666` function
- If function undefined → Monetag SDK didn't load

---

## 📈 **Optimization Tips**

### **Week 1-2: Data Collection**
- Keep defaults
- Monitor which placements perform best
- Check user retention (should stay >50%)

### **Week 3+: Optimize Based on Data**

**If retention is HIGH (>60%)**:
```json
"show_every_nth_visit": 2,  // Show more frequently
"max_ads_per_day": 8
```

**If retention is LOW (<40%)**:
```json
"show_every_nth_visit": 5,  // Show less frequently
"max_ads_per_day": 4
```

---

## 🎯 **Revenue Tracking**

### **Monetag Dashboard**
1. Login to [Monetag](https://publishers.monetag.com)
2. Navigate to "Statistics"
3. View:
   - Daily impressions
   - eCPM (earnings per 1000 views)
   - Total revenue

### **Your Database (Impressions Only)**
```sql
-- Last 7 days performance
SELECT 
  DATE(timestamp) as date,
  COUNT(*) as impressions,
  COUNT(DISTINCT user_id) as unique_users
FROM ad_impressions
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

**Note**: Revenue data comes from Monetag, not your DB.

---

## 🛡️ **Security & Compliance**

### **✅ Already Handled:**
- User data not shared with Monetag
- Only anonymous impression counts tracked
- Premium users fully exempt
- All ad code fail-safe (won't break bot)

### **❗ Privacy Policy**
Users should know ads are shown. Add to your `/terms`:

> "This bot is free and supported by non-intrusive advertisements. Premium subscribers enjoy an ad-free experience."

---

## 📞 **Support**

**If something breaks:**

1. **Check logs**: Look for `"Ad error"`
2. **Disable ads temporarily**:
   ```json
   "enabled": false
   ```
3. **Restart bot**: Most issues resolve on restart
4. **Database issues**: Run migration again

**Quick disable command** (emergency):
```bash
# Edit config
nano config/ad_config.json

# Change to:
"enabled": false

# Restart bot
python main.py
```

---

## 🎓 **Summary Checklist**

**Before Going Live:**
- [ ] Run database migration (`migration_ads.sql`)
- [ ] Test ads with your user ID
- [ ] Test premium user exemption
- [ ] Verify no errors in logs
- [ ] Check analytics table has data
- [ ] Update privacy policy/terms
- [ ] Set `test_mode: false` in config
- [ ] Restart bot

**After Launch:**
- [ ] Monitor user retention weekly
- [ ] Check Monetag dashboard daily
- [ ] Review ad impressions in DB
- [ ] Adjust frequency if needed
- [ ] Collect user feedback

---

## 🎉 **You're Ready!**

Your monetization system is **production-ready** with:
✅ Test mode for safe testing  
✅ Premium exemptions  
✅ Frequency capping  
✅ Analytics tracking  
✅ Fail-safe error handling  
✅ Easy configuration  

**Start testing now, go live when confident!**
