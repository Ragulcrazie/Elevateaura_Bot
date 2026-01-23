-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY, -- Telegram ID
    username TEXT,
    full_name TEXT,
    subscription_status VARCHAR(20) DEFAULT 'free', -- 'free', 'basic_49', 'pro_99'
    subscription_expiry TIMESTAMPTZ,
    current_streak INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    language_pref VARCHAR(10) DEFAULT 'en', -- 'en' or 'hi'
    exam_category VARCHAR(20) -- 'SSC', 'Bank', 'RRB', 'Police', 'General'
);

-- 2. GHOST PROFILES (Fake Players)
CREATE TABLE IF NOT EXISTS ghost_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    base_skill_level INT, -- 800 to 2000
    consistency_factor FLOAT DEFAULT 0.8
);

-- 3. QUIZ SESSIONS (The Daily Tests)
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream VARCHAR(50), -- 'SSC', 'Bank'
    quiz_date DATE DEFAULT CURRENT_DATE,
    questions JSONB, -- Array of 10 Question Objects
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. RESULTS (Real & Ghost)
CREATE TABLE IF NOT EXISTS results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    quiz_id UUID REFERENCES quiz_sessions(id),
    user_id BIGINT REFERENCES users(user_id), -- Nullable for Ghosts if we want, or separate formatting
    score INT,
    time_taken_seconds INT,
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);
