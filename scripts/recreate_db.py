"""Simple script to recreate database from scratch"""
import os
import sys

# Delete the existing database
db_file = 'dev_trading.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Deleted {db_file}")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reinitialize database
from db import init_db

print("📊 Creating fresh database...")
init_db()
print("✅ Database recreated successfully with all tables and columns!")
