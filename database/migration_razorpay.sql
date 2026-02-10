-- Migration: Add Razorpay Payment Orders Table
-- Purpose: Track Razorpay payment orders and their status
-- Date: 2026-02-10

CREATE TABLE IF NOT EXISTS payment_orders (
    order_id VARCHAR PRIMARY KEY,        -- Razorpay order_id (e.g., order_DaZl...)
    user_id BIGINT NOT NULL,             -- Telegram User ID
    amount INTEGER NOT NULL,             -- Amount in paise (e.g., 9900 for ₹99)
    currency VARCHAR DEFAULT 'INR',
    status VARCHAR DEFAULT 'created',    -- created, paid, failed
    payment_id VARCHAR,                  -- Razorpay payment_id (populated after success)
    plan_type VARCHAR,                   -- monthly, yearly, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for quick lookups by user
CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id);

-- Index for status checks
CREATE INDEX IF NOT EXISTS idx_payment_orders_status ON payment_orders(status);
