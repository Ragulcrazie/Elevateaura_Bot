-- ELEVATE AURA ECOSYSTEM MIGRATION V2 --
-- Run this in your Supabase SQL Editor to enable the Wallet & Leaderboard features.

-- 1. Add Wallet Column (The "Stars" Balance)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS wallet_stars BIGINT DEFAULT 0;

-- 2. Add Lead Data Column (To store captured Phone/Exam info)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS lead_data JSONB DEFAULT '{}'::jsonb;

-- 3. Add Weekly Score Column (For the Weekly Tournament)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS weekly_score BIGINT DEFAULT 0;

-- 4. Add Weekly Timestamp (To handle resets)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS weekly_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 5. Add Deposit Balance (Hidden/Internal use if regulations change)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS wallet_deposit BIGINT DEFAULT 0;

-- 6. Indexing for fast Leaderboard queries
CREATE INDEX IF NOT EXISTS idx_weekly_score ON public.users (weekly_score DESC);
CREATE INDEX IF NOT EXISTS idx_wallet_stars ON public.users (wallet_stars DESC);

-- 7. Comment for Documentation
COMMENT ON COLUMN public.users.wallet_stars IS 'The Unified Currency (Displayed as Stars/Rupees). Legally Store Credit.';
COMMENT ON COLUMN public.users.weekly_score IS 'Score for the current week (Mon-Sun). Resets on Sunday.';
