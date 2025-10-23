"""
Database Migration Script
Add signal validation columns to signals table
"""
import psycopg2
from psycopg2 import sql
import sys

def run_migration():
    """Run the signal validation columns migration"""
    
    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'trading',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    migration_sql = """
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
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_signals_trade_id'
  ) THEN
    ALTER TABLE signals 
      ADD CONSTRAINT fk_signals_trade_id 
      FOREIGN KEY (trade_id) 
      REFERENCES trades(id) 
      ON DELETE SET NULL;
  END IF;
END $$;

-- Add indexes for faster filtering
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_validated_by ON signals(validated_by);
CREATE INDEX IF NOT EXISTS idx_signals_trade_id ON signals(trade_id);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);

-- Update existing signals to have PENDING status
UPDATE signals 
SET status = 'PENDING' 
WHERE status IS NULL;

-- Add trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_signals_updated_at()
RETURNS TRIGGER AS $func$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_signals_updated_at ON signals;
CREATE TRIGGER trigger_signals_updated_at
  BEFORE UPDATE ON signals
  FOR EACH ROW
  EXECUTE FUNCTION update_signals_updated_at();
"""
    
    verification_sql = """
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'signals'
ORDER BY ordinal_position;
"""
    
    try:
        # Connect to database
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Run migration
        print("Running migration...")
        cursor.execute(migration_sql)
        conn.commit()
        print("✅ Migration executed successfully!")
        
        # Verify migration
        print("\nVerifying migration...")
        cursor.execute(verification_sql)
        columns = cursor.fetchall()
        
        print("\nSignals table columns:")
        print(f"{'Column Name':<30} {'Type':<30} {'Default':<30} {'Nullable':<10}")
        print("-" * 100)
        for col in columns:
            col_name, col_type, col_default, is_nullable = col
            default_str = str(col_default)[:27] + "..." if col_default and len(str(col_default)) > 30 else str(col_default)
            print(f"{col_name:<30} {col_type:<30} {default_str:<30} {is_nullable:<10}")
        
        # Check for new columns
        new_columns = ['status', 'validated_by', 'validation_notes', 'confidence_score', 
                      'executed_at', 'trade_id', 'updated_at']
        existing_columns = [col[0] for col in columns]
        
        print("\n✅ New columns verification:")
        for col in new_columns:
            if col in existing_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 100)
    print("Signal Validation Columns Migration")
    print("=" * 100)
    print()
    
    success = run_migration()
    sys.exit(0 if success else 1)
