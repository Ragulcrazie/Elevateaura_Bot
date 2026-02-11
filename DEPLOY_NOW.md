# 🚀 DEPLOYMENT CHECKLIST - READ BEFORE DEPLOYING

## ⚠️ CRITICAL: Complete ALL steps before deploying

---

## ✅ **Step 1: Database Migration**

### **Action Required:**
1. Open Supabase Dashboard
2. Go to SQL Editor
3. Copy & paste contents of `database/PRE_DEPLOY_MIGRATION.sql`
4. Run the script
5. Verify all columns exist

### **How to Verify:**
Run this query in Supabase:
```sql
SELECT column_name 
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN (
  'subscription_expires_at',
  'subscription_started_at',
  'last_payment_date',
  'total_payments'
);
```

**Expected Result:** 4 rows returned

**Status:** [ ] DONE

---

## ⚠️ **Step 2: Razorpay Configuration**

### **Current Issue:**
Your `.env` file is **MISSING** Razorpay credentials!

### **Action Required:**
Add these lines to your `.env` file:

```env
# Razorpay Credentials (Get from https://dashboard.razorpay.com)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here
```

### **For Test Mode:**
1. Login to Razorpay Dashboard: https://dashboard.razorpay.com
2. Switch to **Test Mode** (toggle in top right)
3. Go to Settings → API Keys
4. Generate Test Keys
5. Copy `Key Id` and `Key Secret`
6. Add to `.env`

### **For Webhook Secret:**
1. In Razorpay Dashboard → Settings → Webhooks
2. Create new webhook pointing to: `https://your-bot.onrender.com/razorpay/webhook`
3. Copy the webhook secret
4. Add to `.env`

**Status:** [ ] DONE

---

## 📝 **Step 3: Update Render Environment Variables**

### **Action Required:**
Add the SAME Razorpay credentials to Render:

1. Go to Render Dashboard
2. Select your bot service
3. Go to "Environment" tab
4. Add these variables:
   ```
   RAZORPAY_KEY_ID = rzp_test_xxxxx
   RAZORPAY_KEY_SECRET = your_secret
   RAZORPAY_WEBHOOK_SECRET = your_webhook_secret
   ```
5. Click "Save Changes"

**Status:** [ ] DONE

---

## 💾 **Step 4: Commit & Push Code**

### **Action Required:**
Run these commands:

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "fix: Critical payment & premium unlock bugs

- Added await to webhook DB operations for immediate effect
- Implemented smart renewal logic (extend from current expiry)
- Added subscription_started_at & total_payments tracking
- Fixed test mode webhook signature verification
- Fixed AI Coach silent failure for free users
- Added upgrade button in premium lock screen

Fixes #payment-not-activating #ai-coach-broken"

# Push to deploy
git push origin main
```

**Status:** [ ] DONE

---

## 🧪 **Step 5: Post-Deployment Testing**

### **After deployment completes, test immediately:**

#### **Test 1: Webhook Responds**
```bash
# Check Render logs for:
✅ "✅ Razorpay Client Initialized"
✅ "Web server started on port 8080"
✅ No errors on startup
```

#### **Test 2: Make Test Payment**
1. Open bot: /upgrade
2. Select "Monthly Premium (₹99)"
3. **Use Razorpay TEST CARD:**
   - Card: `4111 1111 1111 1111`
   - CVV: `123`
   - Expiry: Any future date
4. Complete payment

#### **Test 3: Verify Premium Activated**
Check Render logs for:
```
✅ "💰 Webhook: Payment confirmed for user X (₹99)"
✅ "🎉 First-time subscription: 30 days from now"
✅ "🆕 First payment detected, setting subscription_started_at"
```

Check Supabase database:
```sql
SELECT 
  user_id,
  subscription_status,
  subscription_started_at,
  total_payments
FROM users
WHERE user_id = YOUR_TEST_USER_ID;
```

**Expected:**
- `subscription_status` = "premium" ✅
- `subscription_started_at` = current timestamp ✅
- `total_payments` = 1 ✅

#### **Test 4: AI Coach Works**
1. As free user: Click AI Coach → Should show upgrade prompt ✅
2. As premium user: Click AI Coach → Should show analysis ✅

**Status:** [ ] DONE

---

## 🔍 **Step 6: Monitor First Hour**

### **Watch Render logs for:**
- ✅ No webhook errors
- ✅ Payment confirmations working
- ✅ No database connection issues
- ✅ No unexpected errors

### **If issues occur:**
1. Check logs: `render logs --tail`
2. Verify database migration ran
3. Verify Razorpay credentials in Render
4. Check webhook URL is correct

---

## 🛡️ **Rollback Plan (If Needed)**

If CRITICAL issues occur after deployment:

### **Quick Rollback:**
```bash
git revert HEAD
git push origin main
```

### **Manual Premium Activation:**
If payment succeeds but premium doesn't activate:
```sql
-- In Supabase SQL Editor, run for affected user:
UPDATE users
SET 
  subscription_status = 'premium',
  subscription_expires_at = NOW() + INTERVAL '30 days',
  subscription_started_at = NOW(),
  last_payment_date = NOW(),
  total_payments = COALESCE(total_payments, 0) + 1
WHERE user_id = AFFECTED_USER_ID;
```

---

## ✅ **FINAL CHECKLIST**

Before deploying, confirm ALL are **DONE**:

- [ ] Database migration ran successfully in Supabase
- [ ] Razorpay credentials added to `.env`
- [ ] Razorpay credentials added to Render environment
- [ ] Code committed and pushed
- [ ] Render deployment completed
- [ ] Test payment made and verified
- [ ] Premium features tested
- [ ] AI Coach tested (free & premium users)
- [ ] Logs monitored for 5+ minutes

---

## 🎯 **DEPLOYMENT DECISION**

### **Can I Deploy Now?**

**IF ALL CHECKBOXES ABOVE ARE CHECKED:** ✅ **YES, DEPLOY NOW**

**IF ANY CHECKBOX IS UNCHECKED:** ❌ **STOP - Complete missing steps first**

---

## ⚠️ **IMPORTANT NOTES**

### **Database Migration Must Run FIRST**
If you deploy without running the database migration, the webhook will fail with:
```
❌ "column subscription_started_at does not exist"
```

### **Razorpay Credentials Required**
Without Razorpay credentials, the payment system won't work. The bot will show:
```
⚠️ Payment System Unavailable
```

### **Test Mode is Safe**
Using Razorpay **Test Mode** is completely safe:
- No real money charged
- Use test cards (4111 1111 1111 1111)
- Fully functional for testing

### **Production Deployment Later**
After testing in Test Mode, switch to Production:
1. Change `rzp_test_*` to `rzp_live_*` keys
2. Update webhook secret
3. Set `RAZORPAY_WEBHOOK_SECRET` (required for production)

---

## 📞 **Need Help?**

**Common Issues:**

1. **"Payment succeeded but premium not activated"**
   - Check webhook logs in Render
   - Verify database migration ran
   - Check Razorpay webhook secret matches

2. **"AI Coach button not responding"**
   - Clear browser cache
   - Check browser console for errors
   - Verify code deployed successfully

3. **"Webhook signature mismatch"**
   - Ensure `RAZORPAY_WEBHOOK_SECRET` matches Razorpay dashboard
   - For test mode: Secret can be left blank (will show warning but work)

---

**Last Updated:** 2026-02-11 15:08  
**Status:** Ready for deployment after checklist completion
