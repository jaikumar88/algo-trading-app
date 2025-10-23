"""
Test script to verify duplicate trade prevention.

This script simulates simultaneous BUY and SELL signals to ensure
only ONE trade remains open per instrument.

Run with: python test_duplicate_prevention.py
"""
import time
import threading
from decimal import Decimal
from db import SessionLocal
from trading import TradingManager
from models import Trade
from sqlalchemy import select


def send_signal(symbol, action, price):
    """Simulate a signal by calling TradingManager directly."""
    tm = TradingManager()
    try:
        result = tm.handle_signal(
            user_id=None,
            symbol=symbol,
            side=action,
            price=Decimal(str(price))
        )
        print(f"✅ {action} signal processed: {result.get('message')}")
    except Exception as e:
        print(f"❌ {action} signal failed: {e}")


def test_simultaneous_signals():
    """Test that simultaneous BUY and SELL signals don't create duplicate positions."""
    print("\n" + "="*70)
    print("TEST: Simultaneous BUY and SELL Signals")
    print("="*70)
    
    symbol = "TESTBTC"
    price = 50000
    
    # Clean up any existing trades for this test symbol
    session = SessionLocal()
    try:
        existing = session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
        for trade in existing:
            session.delete(trade)
        session.commit()
        print(f"🧹 Cleaned up {len(existing)} existing test trades\n")
    finally:
        session.close()
    
    # Send simultaneous signals
    print("📤 Sending simultaneous BUY and SELL signals...")
    threads = [
        threading.Thread(target=send_signal, args=(symbol, "BUY", price)),
        threading.Thread(target=send_signal, args=(symbol, "SELL", price))
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # Wait a moment for transactions to complete
    time.sleep(0.5)
    
    # Check results
    print("\n" + "-"*70)
    print("VERIFICATION")
    print("-"*70)
    
    session = SessionLocal()
    try:
        # Count open trades
        open_trades = session.execute(
            select(Trade).where(
                Trade.symbol == symbol,
                Trade.status == "OPEN"
            )
        ).scalars().all()
        
        # Count all trades
        all_trades = session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
        
        print(f"\n📊 Results for {symbol}:")
        print(f"   Total trades created: {len(all_trades)}")
        print(f"   Open trades: {len(open_trades)}")
        print(f"   Closed trades: {len(all_trades) - len(open_trades)}")
        
        print("\n📋 Trade Details:")
        for i, trade in enumerate(all_trades, 1):
            status_icon = "🟢" if trade.status == "OPEN" else "🔴"
            pl_str = f"P&L: ${trade.profit_loss:.2f}" if trade.profit_loss else "P&L: N/A"
            print(f"   {status_icon} Trade {i}: {trade.action} | {trade.status} | Open: ${trade.open_price} | {pl_str}")
        
        # Verdict
        print("\n" + "="*70)
        if len(open_trades) == 1:
            print("✅ TEST PASSED: Only 1 open trade exists (duplicate prevention working!)")
        elif len(open_trades) == 0:
            print("⚠️  TEST WARNING: No open trades (both signals may have canceled each other)")
        else:
            print(f"❌ TEST FAILED: {len(open_trades)} open trades found (should be exactly 1)")
        print("="*70 + "\n")
        
    finally:
        session.close()


def test_rapid_signals():
    """Test rapid successive signals (not simultaneous)."""
    print("\n" + "="*70)
    print("TEST: Rapid Successive Signals")
    print("="*70)
    
    symbol = "TESTETH"
    base_price = 3000
    
    # Clean up
    session = SessionLocal()
    try:
        existing = session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
        for trade in existing:
            session.delete(trade)
        session.commit()
        print(f"🧹 Cleaned up {len(existing)} existing test trades\n")
    finally:
        session.close()
    
    # Send 5 rapid signals
    print("📤 Sending 5 rapid signals (BUY-SELL-BUY-SELL-BUY)...")
    signals = [
        ("BUY", base_price + 0),
        ("SELL", base_price + 10),
        ("BUY", base_price + 20),
        ("SELL", base_price + 30),
        ("BUY", base_price + 40),
    ]
    
    for action, price in signals:
        send_signal(symbol, action, price)
        time.sleep(0.1)  # Small delay between signals
    
    # Check results
    print("\n" + "-"*70)
    print("VERIFICATION")
    print("-"*70)
    
    session = SessionLocal()
    try:
        open_trades = session.execute(
            select(Trade).where(
                Trade.symbol == symbol,
                Trade.status == "OPEN"
            )
        ).scalars().all()
        
        all_trades = session.execute(
            select(Trade).where(Trade.symbol == symbol).order_by(Trade.open_time)
        ).scalars().all()
        
        print(f"\n📊 Results for {symbol}:")
        print(f"   Signals sent: 5")
        print(f"   Total trades created: {len(all_trades)}")
        print(f"   Open trades: {len(open_trades)}")
        print(f"   Closed trades: {len(all_trades) - len(open_trades)}")
        
        print("\n📋 Trade History (chronological):")
        for i, trade in enumerate(all_trades, 1):
            status_icon = "🟢" if trade.status == "OPEN" else "🔴"
            pl_str = f"P&L: ${trade.profit_loss:.2f}" if trade.profit_loss else "P&L: N/A"
            print(f"   {status_icon} Trade {i}: {trade.action} | {trade.status} | Open: ${trade.open_price} | {pl_str}")
        
        # Verdict
        print("\n" + "="*70)
        if len(open_trades) == 1:
            last_signal = signals[-1][0]
            if open_trades[0].action == last_signal:
                print(f"✅ TEST PASSED: Only 1 {last_signal} trade open (matches last signal)")
            else:
                print(f"⚠️  TEST WARNING: Open trade is {open_trades[0].action}, expected {last_signal}")
        else:
            print(f"❌ TEST FAILED: {len(open_trades)} open trades found (should be exactly 1)")
        print("="*70 + "\n")
        
    finally:
        session.close()


if __name__ == "__main__":
    print("\n" + "🔬 DUPLICATE TRADE PREVENTION TEST SUITE 🔬".center(70))
    print("="*70 + "\n")
    
    try:
        # Test 1: Simultaneous signals
        test_simultaneous_signals()
        
        # Test 2: Rapid successive signals
        test_rapid_signals()
        
        print("\n" + "="*70)
        print("✅ All tests completed! Check results above.")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
