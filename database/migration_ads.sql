-- Ad Analytics Table Migration
-- Run this SQL in your Supabase SQL Editor

-- Create ad_impressions table for tracking ad views
CREATE TABLE IF NOT EXISTS ad_impressions (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  placement VARCHAR(50) NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  success BOOLEAN DEFAULT true
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_ad_impressions_user_id ON ad_impressions(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_impressions_timestamp ON ad_impressions(timestamp);
CREATE INDEX IF NOT EXISTS idx_ad_impressions_placement ON ad_impressions(placement);

-- Create daily ad counter view (optional, for analytics)
CREATE OR REPLACE VIEW daily_ad_stats AS
SELECT 
  DATE(timestamp) as date,
  placement,
  COUNT(*) as impressions,
  COUNT(DISTINCT user_id) as unique_users
FROM ad_impressions
GROUP BY DATE(timestamp), placement
ORDER BY date DESC, impressions DESC;

-- Add comment
COMMENT ON TABLE ad_impressions IS 'Tracks ad impressions for revenue analytics and frequency capping';
