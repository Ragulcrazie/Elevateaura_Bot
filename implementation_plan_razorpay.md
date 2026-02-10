---
description: Implementation plan for replacing Telegram Stars with Razorpay Payment Links
---

# Razorpay Integration Plan

## 1. Overview
This plan implements Razorpay Payment Links to replace Telegram Stars. This method is used to avoid app store fees and improve conversion rates in India, while maintaining compliance by processing payments outside the Telegram Mini App webview (using external browser).

## 2. Architecture Changes

### A. Database Schema
We will create a new table `payment_orders` to track all payment attempts and their status. This ensures we can debug issues and handle webhooks reliably.

```sql
CREATE TABLE IF NOT EXISTS payment_orders (
    order_id VARCHAR PRIMARY KEY,    -- Razorpay order_id (e.g., order_DaZl...)
    user_id BIGINT NOT NULL,         -- Telegram User ID
    amount INTEGER NOT NULL,         -- Amount in paise (e.g., 9900 for ₹99)
    currency VARCHAR DEFAULT 'INR',
    status VARCHAR DEFAULT 'created', -- created, paid, failed
    payment_id VARCHAR,              -- Razorpay payment_id (populated after success)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id);
```

### B. New Mock/Service Layer
We will create `bot/services/razorpay_service.py` to handle:
1.  Creating Payment Links via Razorpay API.
2.  Verifying Webhook Signatures.

### C. Backend (Webhook Handler)
We will add a new route to the existing `aiohttp` server in `main.py`:
`POST /razorpay/webhook`
- Receives the webhook event from Razorpay.
- Verifies the signature securely using `RAZORPAY_KEY_SECRET`.
- If valid:
    - Updates `payment_orders` status to `paid`.
    - Updates `users` table (subscription_status, expires_at).
    - Sends a notification to the user via the Bot.

### D. Bot Command / Interface
- **Command:** `/upgrade` or "Upgrade" button in Main Menu.
- **Action:**
    - Generates a unique Razorpay Payment Link for the user.
    - Sends a message with an **Inline Button**: `[ 💳 Pay ₹99 via Razorpay ]`.
    - **Crucial:** The button uses `url=...` which opens in the system browser, NOT `web_app=...`. This bypasses the strict IAP rules for Mini Apps.

## 3. Step-by-Step Implementation

### Step 1: Install Dependencies
Add `razorpay` to `requirements.txt`.

### Step 2: Database Migration
Create and run `database/migration_razorpay.sql`.

### Step 3: Implement Razorpay Service
Create `bot/services/razorpay_service.py` containing the logic to interact with Razorpay API.
- Need `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `.env`.

### Step 4: Add Webhook Route in `main.py`
Integrate the webhook listener into the existing `aiohttp` application.

### Step 5: Create Bot Handler
Create `bot/handlers/razorpay_payment.py` to handle the `/upgrade` command and button clicks.

### Step 6: Testing
1.  Set `RAZORPAY_KEY_ID` to Test Mode keys.
2.  Run `/upgrade`.
3.  Click link -> Pay.
4.  Verify Database update and Bot Notification.

## 4. Safety & Compliance Note
- **External Browser:** By forcing the link to open in Chrome/Safari (not Telegram Webview), we classify this as a "web payment" rather than an "in-app purchase", which is generally safer from App Store guidelines for cross-platform services.
- **Signature Verification:** We strictly verify the webhook signature to preventing spoofing.

## 5. Fallback/Redundancy
- If the webhook fails, we can provide a manual `/check_payment` command that queries the Razorpay API for the status of the user's latest order.
