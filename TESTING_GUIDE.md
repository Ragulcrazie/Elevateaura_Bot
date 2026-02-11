# 🧪 Quick Testing Guide - Payment System Fixes

## 🎯 **Critical Test Cases**

### **Test Case 1: First-Time Monthly Payment**
**Setup:** New user (never paid before)  
**Action:** Pay ₹99 via Razorpay test mode

**Expected Results:**
```json
Database After Payment:
{
  "subscription_status": "premium",
  "subscription_expires_at": "2026-03-13T09:32:00.000Z",
  "subscription_started_at": "2026-02-11T09:32:00.000Z",  // ✅ NEW
  "last_payment_date": "2026-02-11T09:32:00.000Z",
  "total_payments": 1,  // ✅ NEW (was missing)
  "wallet_stars": 0
}
```

**Logs to Check:**
```
✅ "🎉 First-time subscription: 30 days from now"
✅ "🆕 First payment detected, setting subscription_started_at"
✅ "💰 Webhook: Payment confirmed for user X (₹99)"
```

**User Experience:**
- ✅ Success message in Telegram
- ✅ Leaderboard shows NO ads
- ✅ AI Coach button works
- ✅ All premium features accessible

---

### **Test Case 2: Early Renewal (Active Subscription)**
**Setup:** User with premium expiring on Feb 20, 2026  
**Action:** Pay ₹99 on Feb 15, 2026 (5 days early)

**Expected Results:**
```
OLD: subscription_expires_at = "2026-02-20T00:00:00.000Z"
NEW: subscription_expires_at = "2026-03-22T00:00:00.000Z"  // ✅ Feb 20 + 30 days

total_payments: 2  // ✅ Incremented
subscription_started_at: "2026-01-15T..." // ✅ Unchanged (first payment date)
```

**Logs to Check:**
```
✅ "📅 Extending active subscription: 2026-02-20 + 30 days"
```

**Verification:**
- User gets 35 days total: 5 remaining + 30 new ✅
- No service interruption ✅

---

### **Test Case 3: Late Renewal (Expired Subscription)**
**Setup:** User premium expired on Feb 10, 2026  
**Action:** Pay ₹99 on Feb 15, 2026 (5 days late)

**Expected Results:**
```
OLD: subscription_expires_at = "2026-02-10T00:00:00.000Z"
NEW: subscription_expires_at = "2026-03-17T09:30:00.000Z"  // ✅ Feb 15 + 30 days

total_payments: 2  // ✅ Still tracked
```

**Logs to Check:**
```
✅ "📅 Renewing expired subscription: 30 days from now"
```

**Behavior:**
- User had 5 days with ads (expired period)
- Premium reactivates for fresh 30 days from payment date ✅

---

### **Test Case 4: Yearly Payment**
**Setup:** Any user  
**Action:** Pay ₹999 (or ₹499 with wallet)

**Expected Results:**
```json
{
  "subscription_expires_at": "2027-02-11T...",  // ✅ 365 days added
  "total_payments": N + 1
}
```

**Logic Check:**
```python
# In webhook handler:
days = 365 if amount >= 50000 else 30
# ₹499 = 49900 paise < 50000 → 30 days ❌
# ₹999 = 99900 paise >= 50000 → 365 days ✅
```

---

### **Test Case 5: Payment with 50% Wallet Discount**
**Setup:** User with ₹50 wallet balance  
**Action:** Pay monthly with discount (₹49 Razorpay + ₹50 wallet)

**Expected Results:**
```json
Before Payment:
{
  "wallet_stars": 50
}

After Payment:
{
  "wallet_stars": 0,  // ✅ Deducted
  "subscription_status": "premium",
  "total_payments": N + 1
}
```

**Logs to Check:**
```
✅ "💳 Wallet deducted: ₹50 (balance: ₹0)"
```

**Order Record Check:**
```sql
SELECT * FROM payment_orders WHERE user_id = X ORDER BY id DESC LIMIT 1;

-- Should show:
{
  "amount": 4900,  // What user paid via Razorpay
  "wallet_bonus_used": 50,  // What was deducted from wallet
  "status": "paid"
}
```

---

### **Test Case 6: AI Coach - Free User**
**Action:** Free user clicks "AI Coach" button on leaderboard

**Expected Behavior:**
1. ✅ Button responds immediately (no stuck loading)
2. ✅ Message edits inline (not new message)
3. ✅ Shows premium upgrade prompt
4. ✅ "Upgrade to Premium (₹99/month)" button appears
5. ✅ "Close" button appears
6. ✅ Clicking "Upgrade" takes user to Razorpay payment
7. ✅ Clicking "Close" dismisses message

**If this happens, bug NOT fixed:**
- ❌ Button stays in "loading..." state
- ❌ Two messages appear
- ❌ No response to button click

---

### **Test Case 7: AI Coach - Premium User**
**Action:** Premium user clicks "AI Coach" button

**Expected Behavior:**
1. ✅ Loads weakness analysis immediately
2. ✅ Shows weak topic (e.g., "Speed Math")
3. ✅ Shows common mistake
4. ✅ "Give me a Shortcut" button works
5. ✅ "Psych Hack" button works
6. ✅ "I'm Ready to Train" starts new quiz

---

## 🐞 **Bug Reproduction (Before Fix)**

### **Bug #1: How to Reproduce "Premium Not Unlocking"**
```bash
1. User pays ₹99 via Razorpay test mode
2. Payment succeeds in Razorpay dashboard
3. User opens leaderboard
4. ❌ Still sees ads (not premium)
5. ❌ AI Coach button shows "Premium locked"
6. Check database: subscription_status = "free" (not updated)
```

**Root Cause:**
```python
# OLD CODE (BROKEN):
db.client.table("users").update({...})  # No await! ❌
# Code continues before DB write completes
# User checks status → still sees old data
```

**Fix:**
```python
# NEW CODE (FIXED):
await db.client.table("users").update({...})  # ✅
# Code waits for DB write to complete
# User checks status → sees new data
```

---

### **Bug #2: How to Reproduce "AI Coach Silent Failure"**
```bash
1. Free user opens leaderboard
2. Clicks "AI Performance Coach" button
3. ❌ Button shows "loading..." forever
4. ❌ No message appears (or appears in wrong place)
5. ❌ User thinks feature is broken
```

**Root Cause:**
```python
# OLD CODE (BROKEN):
await callback.message.answer("Locked")  # ❌
# Creates NEW message, original button stays loading
```

**Fix:**
```python
# NEW CODE (FIXED):
await callback.answer()  # Dismiss loading
await callback.message.edit_text("Locked", ...)  # Edit inline ✅
```

---

## 🔍 **Database Queries for Verification**

### **Check User's Subscription Status:**
```sql
SELECT 
  user_id,
  subscription_status,
  subscription_expires_at,
  subscription_started_at,
  total_payments,
  wallet_stars
FROM users
WHERE user_id = 123456789;  -- Replace with test user ID
```

### **Check Recent Payments:**
```sql
SELECT 
  order_id,
  user_id,
  amount,
  wallet_bonus_used,
  status,
  created_at
FROM payment_orders
WHERE user_id = 123456789
ORDER BY created_at DESC
LIMIT 5;
```

### **Check All Premium Users:**
```sql
SELECT 
  user_id,
  first_name,
  subscription_expires_at,
  total_payments
FROM users
WHERE subscription_status = 'premium'
  AND subscription_expires_at > NOW()
ORDER BY subscription_expires_at DESC;
```

---

## 🚨 **Smoke Test After Deployment**

Run these 3 tests immediately after deploying:

### **1. Webhook Alive Test**
```bash
# Send test webhook from Razorpay dashboard
curl -X POST https://your-bot.onrender.com/razorpay/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"payment_link.paid","payload":{"payment_link":{"entity":{"notes":{"user_id":"123"}}}}}'

# Check logs for:
✅ "💰 Webhook: Payment confirmed"
```

### **2. Database Write Test**
```bash
# In Supabase SQL Editor:
SELECT subscription_status, total_payments 
FROM users 
WHERE user_id = 123456789 
LIMIT 1;

# Should show updated values immediately after payment
```

### **3. AI Coach Button Test**
```bash
# As free user:
1. Open /leaderboard
2. Click "AI Coach"
3. ✅ Should respond within 1 second
4. ✅ Should show upgrade prompt
```

---

## ✅ **Success Criteria**

All these must be TRUE:

- [ ] Test payment completes in Razorpay
- [ ] Webhook logs show "Payment confirmed"
- [ ] Database shows `subscription_status = "premium"` immediately
- [ ] `subscription_started_at` is set for first payment
- [ ] `total_payments` increments correctly
- [ ] User sees no ads on leaderboard
- [ ] AI Coach works for premium users
- [ ] AI Coach shows upgrade prompt for free users (with working buttons)
- [ ] Renewal logic extends from current expiry (no time lost)
- [ ] Wallet deduction works correctly

---

## 📞 **If Something Breaks**

### **Payment succeeded but premium not activated:**
```bash
# Check webhook logs:
grep "Payment confirmed" /var/log/render.log

# If no webhook received:
1. Check Razorpay webhook URL is correct
2. Check RAZORPAY_WEBHOOK_SECRET in .env
3. Manually activate via SQL (see CRITICAL_FIXES_DEPLOYMENT.md)
```

### **AI Coach button stuck:**
```bash
# Check browser console for errors
# Verify ai_mentor.py changes deployed
# Test with /start to reinitialize bot
```

### **Database not updating:**
```bash
# Check Supabase connection:
SELECT 1;  -- Should return 1

# Check columns exist:
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'subscription_started_at';
```

---

**Last Updated:** 2026-02-11  
**Status:** ✅ READY FOR PRODUCTION TESTING
