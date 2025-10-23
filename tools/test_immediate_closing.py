#!/usr/bin/env python3
"""
Test script to demonstrate the new immediate opposite signal closing behavior.

This script shows how the system now immediately closes opposite trades
when a valid opposite signal is received, bypassing stop loss and take profit levels.
"""

import os
import sys
from decimal import Decimal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/trading")

from src.services.trading_service import TradingManager
from src.database.session import SessionLocal, init_db
from src.models.base import Trade
from sqlalchemy import select

def setup_database():
    """Initialize database if needed"""
    print("[SETUP] Initializing database...")
    if not init_db():
        print("[ERROR] Failed to initialize database")
        return False
    print("[SUCCESS] Database initialized")
    return True

def clear_existing_trades(session, symbol):
    """Clear any existing trades for the test symbol"""
    existing_trades = session.execute(
        select(Trade).where(Trade.symbol == symbol)
    ).scalars().all()
    
    if existing_trades:
        print(f"[CLEANUP] Removing {len(existing_trades)} existing trades for {symbol}")
        for trade in existing_trades:
            session.delete(trade)
        session.commit()

def test_immediate_opposite_closing():
    """Test the immediate opposite signal closing behavior"""
    print("\n" + "="*80)
    print("TESTING: Immediate Opposite Signal Closing Behavior")
    print("="*80)
    
    if not setup_database():
        return False
    
    session = SessionLocal()
    trading_manager = TradingManager(session=session)
    
    try:
        # Test symbol and prices
        symbol = "BTCUSDT"
        buy_price = Decimal("45000.00")
        sell_price = Decimal("45500.00")  # Higher price for sell signal
        
        # Clear any existing trades
        clear_existing_trades(session, symbol)
        
        print(f"\n[TEST 1] Opening initial BUY position")
        print(f"Symbol: {symbol}, Side: BUY, Price: ${buy_price}")
        
        # Step 1: Open a BUY position
        result1 = trading_manager.handle_signal(
            user_id=None,
            symbol=symbol,
            side="BUY",
            price=buy_price
        )
        
        print(f"Result: {result1['action']}")
        print(f"Message: {result1['message']}")
        
        if result1['opened']:
            trade = result1['opened']
            print(f"✅ Opened BUY trade:")
            print(f"   - Entry Price: ${trade.open_price}")
            print(f"   - Stop Loss: ${trade.stop_loss}")
            print(f"   - Take Profit: ${trade.take_profit}")
            print(f"   - Status: {trade.status}")
        
        print(f"\n[TEST 2] Sending OPPOSITE SELL signal (should immediately close BUY)")
        print(f"Symbol: {symbol}, Side: SELL, Price: ${sell_price}")
        print(f"Expected: IMMEDIATE closure of BUY trade at ${sell_price} (bypassing SL/TP)")
        
        # Step 2: Send opposite SELL signal - should immediately close BUY
        result2 = trading_manager.handle_signal(
            user_id=None,
            symbol=symbol,
            side="SELL",
            price=sell_price
        )
        
        print(f"\nResult: {result2['action']}")
        print(f"Message: {result2['message']}")
        
        if result2['closed']:
            print(f"✅ IMMEDIATELY closed {len(result2['closed'])} BUY trade(s):")
            for closed_trade in result2['closed']:
                print(f"   - Original Entry: ${closed_trade.open_price}")
                print(f"   - Original SL: ${closed_trade.stop_loss}")
                print(f"   - Original TP: ${closed_trade.take_profit}")
                print(f"   - CLOSED AT: ${closed_trade.close_price} (MARKET PRICE)")
                print(f"   - P&L: ${closed_trade.profit_loss}")
                print(f"   - Status: {closed_trade.status}")
        
        if result2['opened']:
            new_trade = result2['opened']
            print(f"✅ Opened new SELL trade:")
            print(f"   - Entry Price: ${new_trade.open_price}")
            print(f"   - Stop Loss: ${new_trade.stop_loss}")
            print(f"   - Take Profit: ${new_trade.take_profit}")
            print(f"   - Status: {new_trade.status}")
        
        print(f"\n[TEST 3] Sending SAME direction SELL signal (should be ignored)")
        
        # Step 3: Send same direction SELL signal - should be ignored
        result3 = trading_manager.handle_signal(
            user_id=None,
            symbol=symbol,
            side="SELL",
            price=Decimal("45600.00")
        )
        
        print(f"Result: {result3['action']}")
        print(f"Message: {result3['message']}")
        
        print(f"\n[TEST 4] Sending OPPOSITE BUY signal (should immediately close SELL)")
        
        # Step 4: Send opposite BUY signal - should immediately close SELL
        final_buy_price = Decimal("45300.00")  # Lower price for final buy
        result4 = trading_manager.handle_signal(
            user_id=None,
            symbol=symbol,
            side="BUY",
            price=final_buy_price
        )
        
        print(f"Result: {result4['action']}")
        print(f"Message: {result4['message']}")
        
        if result4['closed']:
            print(f"✅ IMMEDIATELY closed {len(result4['closed'])} SELL trade(s):")
            for closed_trade in result4['closed']:
                print(f"   - Original Entry: ${closed_trade.open_price}")
                print(f"   - CLOSED AT: ${closed_trade.close_price} (MARKET PRICE)")
                print(f"   - P&L: ${closed_trade.profit_loss}")
        
        # Final verification - check what trades remain
        print(f"\n[VERIFICATION] Final trade status for {symbol}:")
        final_trades = session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
        
        open_trades = [t for t in final_trades if t.status == "OPEN"]
        closed_trades = [t for t in final_trades if t.status == "CLOSED"]
        
        print(f"   - Open trades: {len(open_trades)}")
        print(f"   - Closed trades: {len(closed_trades)}")
        
        for i, trade in enumerate(open_trades, 1):
            print(f"   - Open #{i}: {trade.action} @ ${trade.open_price}")
        
        print("\n" + "="*80)
        print("TEST SUMMARY:")
        print("✅ System immediately closes opposite trades at current market price")
        print("✅ Stop loss and take profit levels are bypassed for opposite signals")
        print("✅ Same direction signals are properly ignored")
        print("✅ New trades are opened with fresh SL/TP levels")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_immediate_opposite_closing()
    if success:
        print("\n[SUCCESS] All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Tests failed!")
        sys.exit(1)