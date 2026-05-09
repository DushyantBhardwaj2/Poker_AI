-- 🚀 PokerSense AI: PostgreSQL Schema Creation Script
-- This script initializes or updates the database for production usage on Neon.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    poker_experience TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Opponents Table
CREATE TABLE IF NOT EXISTS opponents (
    opponent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    notes TEXT DEFAULT '',
    playstyle_archetype TEXT DEFAULT 'Unknown',
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast opponent lookups by user and name
CREATE UNIQUE INDEX IF NOT EXISTS idx_opponents_user_name ON opponents(user_id, player_name);

-- 3. Opponent Stats Table (ML Features)
CREATE TABLE IF NOT EXISTS opponent_stats (
    opponent_id UUID PRIMARY KEY REFERENCES opponents(opponent_id) ON DELETE CASCADE,
    hands_played INTEGER DEFAULT 0,
    last_hand_timestamp TIMESTAMPTZ,
    -- JSONB for dynamic ML features
    dynamic_features JSONB DEFAULT '{
        "vpip_count": 0,
        "pfr_count": 0,
        "aggression_ip": 0.0,
        "aggression_oop": 0.0,
        "strict_bluff_showdowns": 0,
        "cbet_count": 0,
        "cbet_success": 0,
        "three_bet_count": 0,
        "three_bet_success": 0,
        "fold_to_river_bet": 0,
        "calls_showdown": 0,
        "wins_at_showdown": 0,
        "total_bets": 0,
        "total_calls": 0
    }'::jsonb,
    -- Session-only features for baseline comparison
    session_features JSONB DEFAULT '{
        "hands_played": 0,
        "vpip_count": 0,
        "pfr_count": 0,
        "aggression_total": 0,
        "cbet_count": 0,
        "three_bet_count": 0
    }'::jsonb,
    reliability_score TEXT DEFAULT 'Low',
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Create a GIN index for fast JSONB querying
CREATE INDEX IF NOT EXISTS idx_opponent_stats_features ON opponent_stats USING GIN (dynamic_features);

-- 4. Game Sessions Table
CREATE TABLE IF NOT EXISTS game_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_name TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    total_hands INTEGER DEFAULT 0,
    total_winnings FLOAT DEFAULT 0.0
);

-- 5. Hand History Table
CREATE TABLE IF NOT EXISTS hand_history (
    hand_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES game_sessions(session_id) ON DELETE CASCADE,
    street TEXT NOT NULL,
    pot_size FLOAT DEFAULT 0.0,
    your_cards JSONB,
    community_cards JSONB,
    result TEXT, -- win, loss, tie
    amount_won FLOAT DEFAULT 0.0,
    action_count INTEGER DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    tactical_data JSONB, -- Stores equity, pot_odds, advisor verdict
    leak_detected BOOLEAN DEFAULT FALSE,
    leak_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Session Opponents (Many-to-Many junction)
CREATE TABLE IF NOT EXISTS session_opponents (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES game_sessions(session_id) ON DELETE CASCADE,
    opponent_id UUID NOT NULL REFERENCES opponents(opponent_id) ON DELETE CASCADE,
    hands_played INTEGER DEFAULT 0,
    vpip_count INTEGER DEFAULT 0,
    pfr_count INTEGER DEFAULT 0,
    aggression_total FLOAT DEFAULT 0.0,
    total_won FLOAT DEFAULT 0.0
);

-- --- UPDATES FOR EXISTING TABLES (Migrations) ---

-- Add columns to hand_history if missing
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='hand_history' AND column_name='tactical_data') THEN
        ALTER TABLE hand_history ADD COLUMN tactical_data JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='hand_history' AND column_name='leak_detected') THEN
        ALTER TABLE hand_history ADD COLUMN leak_detected BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='hand_history' AND column_name='leak_description') THEN
        ALTER TABLE hand_history ADD COLUMN leak_description TEXT;
    END IF;
END $$;

-- Add columns to opponents if missing
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponents' AND column_name='notes') THEN
        ALTER TABLE opponents ADD COLUMN notes TEXT DEFAULT '';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponents' AND column_name='playstyle_archetype') THEN
        ALTER TABLE opponents ADD COLUMN playstyle_archetype TEXT DEFAULT 'Unknown';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponents' AND column_name='last_seen') THEN
        ALTER TABLE opponents ADD COLUMN last_seen TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- Add columns to opponent_stats if missing
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponent_stats' AND column_name='last_hand_timestamp') THEN
        ALTER TABLE opponent_stats ADD COLUMN last_hand_timestamp TIMESTAMPTZ;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponent_stats' AND column_name='session_features') THEN
        ALTER TABLE opponent_stats ADD COLUMN session_features JSONB DEFAULT '{
            "hands_played": 0,
            "vpip_count": 0,
            "pfr_count": 0,
            "aggression_total": 0,
            "cbet_count": 0,
            "three_bet_count": 0
        }'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='opponent_stats' AND column_name='reliability_score') THEN
        ALTER TABLE opponent_stats ADD COLUMN reliability_score TEXT DEFAULT 'Low';
    END IF;
END $$;

-- --- UTILITIES ---

-- Trigger to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_opponent_stats_modtime ON opponent_stats;
CREATE TRIGGER update_opponent_stats_modtime
    BEFORE UPDATE ON opponent_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
