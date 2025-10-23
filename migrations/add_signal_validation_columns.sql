-- ================================================
-- Migration: Add Signal Validation Columns
-- Created: 2025-10-17
-- Description: Adds columns to track signal validation,
--              rejection, and execution status
-- ================================================

BEGIN;

-- Add new columns to signals table
ALTER TABLE signals 
  ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDING',
  ADD COLUMN IF NOT EXISTS validated_by VARCHAR(255),
  ADD COLUMN IF NOT EXISTS validation_notes TEXT,
  ADD COLUMN IF NOT EXISTS confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 100),
  ADD COLUMN IF NOT EXISTS executed_at TIMESTAMP WITH TIME ZONE,
  ADD COLUMN IF NOT EXISTS trade_id INTEGER,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Add foreign key constraint to link signals to trades
ALTER TABLE signals 
  ADD CONSTRAINT fk_signals_trade_id 
  FOREIGN KEY (trade_id) 
  REFERENCES trades(id) 
  ON DELETE SET NULL;

-- Add index on status for faster filtering
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);

-- Add index on validated_by for tracking who validated
CREATE INDEX IF NOT EXISTS idx_signals_validated_by ON signals(validated_by);

-- Add index on trade_id for lookups
CREATE INDEX IF NOT EXISTS idx_signals_trade_id ON signals(trade_id);

-- Add index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);

-- Update existing signals to have PENDING status
UPDATE signals 
SET status = 'PENDING' 
WHERE status IS NULL;

-- Add trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_signals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_signals_updated_at ON signals;
CREATE TRIGGER trigger_signals_updated_at
  BEFORE UPDATE ON signals
  FOR EACH ROW
  EXECUTE FUNCTION update_signals_updated_at();

COMMIT;

-- ================================================
-- Verification Query
-- ================================================
-- Run this to verify the migration succeeded:
--
-- SELECT column_name, data_type, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'signals'
-- ORDER BY ordinal_position;
--
-- Expected new columns:
--   - status (varchar, default 'PENDING')
--   - validated_by (varchar, nullable)
--   - validation_notes (text, nullable)
--   - confidence_score (float, nullable)
--   - executed_at (timestamp, nullable)
--   - trade_id (integer, nullable)
--   - updated_at (timestamp, default CURRENT_TIMESTAMP)
-- ================================================
