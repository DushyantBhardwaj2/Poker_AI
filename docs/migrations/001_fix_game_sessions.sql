-- Migration: Add missing columns to game_sessions
-- Added by Claude 2026-05-09

-- Add total_winnings column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'game_sessions' AND column_name = 'total_winnings'
    ) THEN
        ALTER TABLE game_sessions ADD COLUMN total_winnings FLOAT DEFAULT 0.0;
    END IF;
END $$;

-- Add ended_at column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'game_sessions' AND column_name = 'ended_at'
    ) THEN
        ALTER TABLE game_sessions ADD COLUMN ended_at TIMESTAMPTZ;
    END IF;
END $$;