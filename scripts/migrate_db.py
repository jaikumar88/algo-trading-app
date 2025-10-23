# Database Migration Script
# This script applies the missing columns to the trades table

from db import engine
from sqlalchemy import text, inspect

print("🔄 Applying database migration...")
print("   Adding missing columns to 'trades' table\n")

try:
    inspector = inspect(engine)
    
    # Check if trades table exists
    if 'trades' not in inspector.get_table_names():
        print("❌ 'trades' table doesn't exist!")
        print("\nRun: python recreate_db.py")
        exit(1)
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('trades')]
    print(f"📋 Existing columns: {', '.join(existing_columns)}\n")
    
    with engine.connect() as conn:
        # Add missing columns
        columns_to_add = [
            ("allocated_fund", "NUMERIC(15,2)"),
            ("risk_amount", "NUMERIC(15,2)"),
            ("stop_loss_triggered", "BOOLEAN DEFAULT 0"),
            ("closed_by_user", "BOOLEAN DEFAULT 0")
        ]
        
        added_count = 0
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name} ({col_type})")
                sql = f"ALTER TABLE trades ADD COLUMN {col_name} {col_type}"
                conn.execute(text(sql))
                conn.commit()
                print(f"   ✅ Added {col_name}\n")
                added_count += 1
            else:
                print(f"   ⏭️  Column {col_name} already exists\n")
        
        if added_count > 0:
            print(f"✅ Migration completed! Added {added_count} columns.")
        else:
            print("✅ All columns already exist!")
        
        print("\n🎉 Database is now up to date!")
        
except Exception as e:
    print(f"❌ Migration failed: {e}")
    print("\nIf you see this error, you may need to run:")
    print("   python recreate_db.py")
    print("\nThis will create a fresh database with the correct schema.")

