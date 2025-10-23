"""
Test database initialization and table creation
"""
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("🧪 Testing Database Initialization")
print("=" * 60)

# Initialize database
from db import init_db, engine
from sqlalchemy import inspect

print("\n1️⃣ Initializing database...")
success = init_db()

if success:
    print("\n2️⃣ Checking tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"\n✅ Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   • {table}")
            
            # Show column info
            columns = inspector.get_columns(table)
            print(f"     Columns ({len(columns)}):", end=" ")
            col_names = [col['name'] for col in columns[:5]]
            if len(columns) > 5:
                print(", ".join(col_names), "...")
            else:
                print(", ".join(col_names))
    else:
        print("\n⚠️  No tables found")
    
    print("\n3️⃣ Testing database connection...")
    from db import SessionLocal
    from models import Signal
    
    session = SessionLocal()
    try:
        # Try to query (will be empty but tests connection)
        count = session.query(Signal).count()
        print(f"✅ Connection successful! Signal count: {count}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    finally:
        session.close()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization test complete!")
    print("=" * 60)
else:
    print("\n❌ Database initialization failed")
    print("\nTroubleshooting:")
    print("  1. Check PostgreSQL is running")
    print("  2. Verify database exists: psql -U postgres -c 'CREATE DATABASE trading;'")
    print("  3. Check .env file has correct credentials")
    print("\n" + "=" * 60)
