"""Check database structure"""
import sqlite3

conn = sqlite3.connect('dev_trading.db')
cursor = conn.cursor()

# Check trades table structure
cursor.execute('PRAGMA table_info(trades)')
columns = cursor.fetchall()

print("Columns in trades table:")
for col in columns:
    print(f"  • {col[1]} ({col[2]})")

conn.close()
