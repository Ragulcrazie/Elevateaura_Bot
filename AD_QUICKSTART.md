# 🚀 AD SYSTEM - QUICK START

## ⚡ Testing RIGHT NOW

### 1. Run Database Migration
```sql
-- Open Supabase SQL Editor
-- Paste contents of: database/migration_ads.sql
-- Click "Run"
```

### 2. Test Ad Display
```bash
# Start bot
python main.py

# Then use Telegram:
# - Send /quiz to bot (as user 996261168)
# - Complete quiz
# - Look for ad message after results
```

### 3. Check Logs
```bash
# Success indicators:
"✅ Ad impression recorded: 996261168 @ post_quiz"
"✅ Post-quiz ad shown to 996261168"

# Expected skips (if not test mode on first try):
"❌ Ad skipped for {other_user}: test_mode_user_not_whitelisted"
```

---

## 🎯 Going Live (After Testing)

### 1. Edit Config
```bash
# File: config/ad_config.json
# Line 4: "test_mode": false,  (change true → false)
# Line 5: "test_user_ids": [],  (empty array)
```

### 2. Restart Bot
```bash
Ctrl+C
python main.py
```

### 3. Done! 🎉

---

## 📊 Quick Analytics

```sql
-- Total ads shown today
SELECT COUNT(*) as ads_today
FROM ad_impressions
WHERE DATE(timestamp) = CURRENT_DATE;

-- Top user (ads viewed)
SELECT user_id, COUNT(*) as ad_count
FROM ad_impressions
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY ad_count DESC
LIMIT 10;
```

---

## 🔧 Config Cheat Sheet

```json
{
  "enabled": true,              // false = disable all ads
  "test_mode": false,           // true = only show to test_user_ids
  "max_ads_per_day": 6,        // Cap per user
  "min_seconds_between_ads": 120, // Global cooldown
  "premium_skip_ads": true     // Don't change this
}
```

---

## 🆘 Emergency Disable

```bash
# Edit: config/ad_config.json
# Set: "enabled": false
# Restart bot

# Ads will be disabled immediately
```

---

## ✅ Health Check

**Your test user ID**: `996261168`

**Test URLs:**
- Ad check API: `http://localhost:8080/api/check_ad?user_id=996261168&placement=leaderboard`
- User data: `http://localhost:8080/api/user_data?user_id=996261168`

**Files to know:**
- **Config**: `config/ad_config.json`
- **Service**: `bot/services/ad_service.py`
- **Handlers**: `bot/handlers/ads.py`
- **Integration**: `bot/handlers/quiz.py` (line ~675)
- **WebApp**: `web_app/index.html` (line 9)

**Support**: See `AD_MONETIZATION_GUIDE.md`
