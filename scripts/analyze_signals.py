"""
Analyze signals to see which ones have action=None
"""
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/trading'

from db import SessionLocal
from models import Signal

session = SessionLocal()

try:
    signals = session.query(Signal).order_by(Signal.created_at).all()
    
    print(f"\n📊 SIGNAL ANALYSIS")
    print("="*80)
    print(f"Total Signals: {len(signals)}\n")
    
    with_action = [s for s in signals if s.action]
    without_action = [s for s in signals if not s.action]
    
    print(f"✅ Signals with ACTION: {len(with_action)}")
    print(f"❌ Signals with NO action: {len(without_action)}\n")
    
    print("\n🔹 ALL SIGNALS:")
    print("-"*80)
    for i, sig in enumerate(signals, 1):
        action_str = sig.action if sig.action else "❌ MISSING"
        print(f"{i:2}. {sig.symbol:15} Action: {action_str:10} Price: {sig.price:15} @ {sig.created_at}")
        if not sig.action:
            print(f"    RAW: {sig.raw[:100]}...")
    
    print("\n\n🔹 SIGNALS WITHOUT ACTION (Not being processed):")
    print("-"*80)
    if without_action:
        for sig in without_action:
            print(f"\nID: {sig.id}")
            print(f"Symbol: {sig.symbol}")
            print(f"Price: {sig.price}")
            print(f"Time: {sig.created_at}")
            print(f"RAW TEXT:\n{sig.raw}")
            print("-"*40)
    else:
        print("All signals have action defined! ✅")

finally:
    session.close()
