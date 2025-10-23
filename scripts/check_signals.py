"""
Quick test to demonstrate Long → Buy and Short → Sell mapping
Run this after starting the Flask backend
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("⚠️  DATABASE_URL not found in .env")
    print("Using default: postgresql://postgres:postgres@localhost:5432/trading")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/trading"

# Test database connection
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

print("=" * 60)
print("Testing Action Mapping: Long → Buy, Short → Sell")
print("=" * 60)

try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check recent signals
    print("\n📊 Recent signals from database:")
    print("-" * 60)
    
    query = text("""
        SELECT id, source, symbol, action, price, 
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created 
        FROM signals 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    result = session.execute(query)
    rows = result.fetchall()
    
    if rows:
        print(f"{'ID':<5} {'Source':<10} {'Symbol':<10} {'Action':<8} {'Price':<12} {'Created'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<10} {row[2] or 'N/A':<10} {row[3] or 'N/A':<8} {row[4] or 'N/A':<12} {row[5]}")
    else:
        print("No signals found in database yet.")
        print("\nℹ️  Send a test webhook to create signals:")
        print("   python test_action_mapping.py")
    
    session.close()
    print("\n" + "=" * 60)
    print("✅ Database connection successful!")
    print("=" * 60)
    
    print("\n📝 Action Mapping Rules:")
    print("   • 'Long' or 'long' → BUY")
    print("   • 'Short' or 'short' → SELL")
    print("   • 'Buy' or 'buy' → BUY")
    print("   • 'Sell' or 'sell' → SELL")
    
    print("\n🧪 To test the webhook:")
    print("   1. Make sure Flask backend is running (python app.py)")
    print("   2. Run: python test_action_mapping.py")
    print("   3. Check the signals table with this script again")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nℹ️  Make sure:")
    print("   1. PostgreSQL is running")
    print("   2. Database 'trading' exists")
    print("   3. User 'postgres' has access")
    print("\n   Run: .\\setup_postgres.ps1")
