# PostgreSQL Database Migration
# This script connects to PostgreSQL and adds missing columns

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv()

# Get PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'trading')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'  # noqa

print(f"🔄 Connecting to PostgreSQL: {DATABASE_URL}\n")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inspector = inspect(engine)
    
    # Check if trades table exists
    if 'trades' not in inspector.get_table_names():
        print("❌ 'trades' table doesn't exist in PostgreSQL!")
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
            ("stop_loss_triggered", "BOOLEAN DEFAULT FALSE"),
            ("closed_by_user", "BOOLEAN DEFAULT FALSE")
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
        
        print("\n🎉 PostgreSQL database is now up to date!")
        print("\n🔄 Please restart Flask server to apply changes:")
        print("   Stop: Ctrl+C")
        print("   Start: python app.py")
        
except Exception as e:
    print(f"❌ Migration failed: {e}")
    print("\nPossible solutions:")
    print("1. Make sure PostgreSQL is running")
    print("2. Check connection details in .env file")
    print("3. Run: python recreate_db.py (will create fresh database)")
