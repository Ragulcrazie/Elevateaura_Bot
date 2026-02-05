-- Migration: Add Subscription Tracking Columns
-- Purpose: Track subscription lifecycle, payments, and expiration
-- Date: 2026-02-05

-- Add subscription tracking columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS subscription_started_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS last_payment_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS total_payments INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS expiration_warning_sent BOOLEAN DEFAULT FALSE;

-- Create index for expiration checks (performance optimization)
CREATE INDEX IF NOT EXISTS idx_users_subscription_expires 
ON users(subscription_expires_at) 
WHERE subscription_status = 'premium';

-- Create index for payment tracking
CREATE INDEX IF NOT EXISTS idx_users_last_payment 
ON users(last_payment_date);

COMMENT ON COLUMN users.subscription_expires_at IS 'UTC timestamp when premium subscription expires (30 days from payment)';
COMMENT ON COLUMN users.subscription_started_at IS 'UTC timestamp when user first became premium';
COMMENT ON COLUMN users.last_payment_date IS 'UTC timestamp of most recent payment';
COMMENT ON COLUMN users.total_payments IS 'Total number of premium payments received from this user';
