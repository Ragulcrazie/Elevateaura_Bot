-- ⚠️ RUN THIS IN SUPABASE BEFORE DEPLOYING ⚠️
-- Database Migration for Payment System Fixes
-- Date: 2026-02-11

-- Step 1: Verify subscription columns exist
SELECT column_name 
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN (
  'subscription_expires_at',
  'subscription_started_at',
  'last_payment_date',
  'total_payments',
  'expiration_warning_sent'
);

-- Expected: Should return 5 rows
-- If NOT, run the migration below:

-- Step 2: Add missing columns (if needed)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS subscription_started_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS last_payment_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS total_payments INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS expiration_warning_sent BOOLEAN DEFAULT FALSE;

-- Step 3: Create performance indexes
CREATE INDEX IF NOT EXISTS idx_users_subscription_expires 
ON users(subscription_expires_at) 
WHERE subscription_status = 'premium';

CREATE INDEX IF NOT EXISTS idx_users_last_payment 
ON users(last_payment_date);

-- Step 4: Verify payment_orders table exists
SELECT column_name 
FROM information_schema.columns
WHERE table_name = 'payment_orders';

-- If table doesn't exist, create it:
CREATE TABLE IF NOT EXISTS payment_orders (
  id SERIAL PRIMARY KEY,
  order_id TEXT UNIQUE NOT NULL,
  user_id BIGINT NOT NULL,
  amount INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  status TEXT DEFAULT 'created',
  plan_type TEXT,
  wallet_bonus_used INTEGER DEFAULT 0,
  payment_id TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_orders_status ON payment_orders(status);

-- Step 5: Final verification
SELECT 
  COUNT(*) as total_users,
  COUNT(subscription_expires_at) as has_expiry,
  COUNT(subscription_started_at) as has_started,
  COUNT(total_payments) as has_payments
FROM users;

-- ✅ If all counts match (or close), you're ready!
