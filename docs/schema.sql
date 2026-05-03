-- 🚀 PokerSense AI: PostgreSQL Schema Creation Script
-- This script initializes the database for production usage on Supabase/Neon.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table (Multi-tenant security)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Opponents Table (Isolation)
CREATE TABLE IF NOT EXISTS opponents (
    opponent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast opponent lookups by user and name
CREATE UNIQUE INDEX idx_opponents_user_name ON opponents(user_id, player_name);

-- 3. Opponent Stats Table (ML Features)
CREATE TABLE IF NOT EXISTS opponent_stats (
    opponent_id UUID PRIMARY KEY REFERENCES opponents(opponent_id) ON DELETE CASCADE,
    hands_played INTEGER DEFAULT 0,
    -- JSONB for dynamic ML features and future-proofing
    dynamic_features JSONB DEFAULT '{
        "vpip_count": 0,
        "pfr_count": 0,
        "aggression_ip": 0.0,
        "aggression_oop": 0.0,
        "strict_bluff_showdowns": 0
    }'::jsonb,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Create a GIN index for fast JSONB querying (performance-optimized)
CREATE INDEX idx_opponent_stats_features ON opponent_stats USING GIN (dynamic_features);

-- Trigger to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_opponent_stats_modtime
    BEFORE UPDATE ON opponent_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- --- INITIALIZATION DATA (Optional) ---
-- INSERT INTO users (email) VALUES ('default@pokersense.ai');
