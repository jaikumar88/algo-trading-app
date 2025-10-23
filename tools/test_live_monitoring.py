"""
Test Real-Time Trade Monitoring with Delta Exchange Integration
Simulates live trading with real-time price monitoring and risk management
"""
import os
import sys
import time
from decimal import Decimal
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.services.trade_monitor_service import get_trade_monitor
from src.services.delta_exchange_service import get_delta_trader
from src.database.session import SessionLocal
from src.models.base import Trade


def create_test_trades():
    """Create test trades for monitoring"""
    print("=" * 80)
    print("Creating Test Trades")
    print("=" * 80)
    
    delta_trader = get_delta_trader()
    
    # Get current BTC price
    if not delta_trader.client:
        print("❌ Delta Exchange client not initialized")
        print("Please configure DELTA_API_KEY and DELTA_API_SECRET")
        return []
    
    print("\nFetching current BTCUSD price...")
    orderbook = delta_trader.client.get_orderbook('BTCUSD')
    
    if not orderbook.get('success'):
        print(f"❌ Failed to get BTCUSD price: {orderbook.get('error')}")
        return []
    
    result = orderbook.get('result', {})
    buy_orders = result.get('buy', [])
    sell_orders = result.get('sell', [])
    
    if not buy_orders or not sell_orders:
        print("❌ No market data available")
        return []
    
    best_bid = float(buy_orders[0].get('price', 0))
    best_ask = float(sell_orders[0].get('price', 0))
    current_price = (best_bid + best_ask) / 2
    
    print(f"✅ Current BTCUSD price: ${current_price:,.2f}")
    
    # Create test trades at different price levels
    test_trades = []
    
    with SessionLocal() as db:
        # Trade 1: Normal trade (slightly in profit)
        entry_1 = current_price * 0.995  # Entry 0.5% below current
        trade_1 = Trade(
            symbol='BTCUSD',
            side='BUY',
            entry_price=Decimal(str(entry_1)),
            size=Decimal('1'),
            status='open',
            opened_at=datetime.utcnow()
        )
        db.add(trade_1)
        print(f"\nTrade 1: BUY @ ${entry_1:,.2f} (0.5% profit)")
        
        # Trade 2: Will hit stop loss
        entry_2 = current_price * 1.015  # Entry 1.5% above current (loss)
        trade_2 = Trade(
            symbol='BTCUSD',
            side='BUY',
            entry_price=Decimal(str(entry_2)),
            size=Decimal('1'),
            status='open',
            opened_at=datetime.utcnow()
        )
        db.add(trade_2)
        print(f"Trade 2: BUY @ ${entry_2:,.2f} (will hit -1% SL)")
        
        # Trade 3: Short position in profit
        entry_3 = current_price * 1.005  # Entry 0.5% above for short
        trade_3 = Trade(
            symbol='BTCUSD',
            side='SELL',
            entry_price=Decimal(str(entry_3)),
            size=Decimal('1'),
            status='open',
            opened_at=datetime.utcnow()
        )
        db.add(trade_3)
        print(f"Trade 3: SELL @ ${entry_3:,.2f} (0.5% profit)")
        
        db.commit()
        db.refresh(trade_1)
        db.refresh(trade_2)
        db.refresh(trade_3)
        
        test_trades = [trade_1.id, trade_2.id, trade_3.id]
    
    print(f"\n✅ Created {len(test_trades)} test trades")
    print(f"Trade IDs: {test_trades}")
    
    return test_trades


def cleanup_test_trades(trade_ids):
    """Delete test trades"""
    print("\n" + "=" * 80)
    print("Cleaning Up Test Trades")
    print("=" * 80)
    
    with SessionLocal() as db:
        for trade_id in trade_ids:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                print(f"Deleting trade {trade_id}: {trade.side} {trade.symbol}")
                db.delete(trade)
        db.commit()
    
    print("✅ Test trades deleted")


def test_real_time_monitoring(duration=30):
    """Test real-time monitoring for specified duration"""
    print("\n" + "=" * 80)
    print(f"REAL-TIME MONITORING TEST ({duration} seconds)")
    print("=" * 80)
    
    # Create test trades
    trade_ids = create_test_trades()
    
    if not trade_ids:
        print("❌ Failed to create test trades")
        return
    
    # Start trade monitor
    monitor = get_trade_monitor(check_interval=5)
    
    print("\n" + "=" * 80)
    print("Starting Trade Monitor...")
    print("=" * 80)
    print(f"Monitor will check every 5 seconds")
    print(f"Test will run for {duration} seconds")
    print(f"Watch for real-time price updates and risk management actions")
    print("=" * 80)
    
    try:
        monitor.start()
        
        # Wait for specified duration
        print(f"\n⏰ Monitor running... (will stop in {duration}s)")
        time.sleep(duration)
        
    finally:
        # Stop monitor
        print("\n" + "=" * 80)
        print("Stopping Trade Monitor...")
        print("=" * 80)
        monitor.stop()
        
        # Cleanup
        cleanup_test_trades(trade_ids)
    
    print("\n" + "=" * 80)
    print("✅ Real-Time Monitoring Test Complete")
    print("=" * 80)


def test_price_fetching():
    """Test real-time price fetching from Delta Exchange"""
    print("=" * 80)
    print("TESTING REAL-TIME PRICE FETCHING")
    print("=" * 80)
    
    delta_trader = get_delta_trader()
    
    if not delta_trader.client:
        print("❌ Delta Exchange client not initialized")
        return
    
    symbols = ['BTCUSD', 'ETHUSD']
    
    print(f"\nFetching live prices for {len(symbols)} symbols...")
    print("-" * 80)
    
    for symbol in symbols:
        try:
            print(f"\n{symbol}:")
            orderbook = delta_trader.client.get_orderbook(symbol)
            
            if orderbook.get('success'):
                result = orderbook.get('result', {})
                buy_orders = result.get('buy', [])
                sell_orders = result.get('sell', [])
                
                if buy_orders and sell_orders:
                    best_bid = float(buy_orders[0].get('price', 0))
                    best_ask = float(sell_orders[0].get('price', 0))
                    mid_price = (best_bid + best_ask) / 2
                    spread = best_ask - best_bid
                    spread_pct = (spread / mid_price) * 100
                    
                    print(f"  Best Bid: ${best_bid:,.2f}")
                    print(f"  Best Ask: ${best_ask:,.2f}")
                    print(f"  Mid Price: ${mid_price:,.2f}")
                    print(f"  Spread: ${spread:.2f} ({spread_pct:.4f}%)")
                    print(f"  ✅ Price fetch successful")
                else:
                    print(f"  ❌ No orderbook data")
            else:
                print(f"  ❌ Error: {orderbook.get('error')}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Price Fetching Test Complete")
    print("=" * 80)


def show_current_trades():
    """Display all current open trades"""
    print("\n" + "=" * 80)
    print("CURRENT OPEN TRADES")
    print("=" * 80)
    
    with SessionLocal() as db:
        open_trades = db.query(Trade).filter(Trade.status == 'open').all()
        
        if not open_trades:
            print("No open trades")
            return
        
        print(f"\nFound {len(open_trades)} open trade(s):\n")
        
        for trade in open_trades:
            print(f"Trade ID: {trade.id}")
            print(f"  Symbol: {trade.symbol}")
            print(f"  Side: {trade.side}")
            print(f"  Entry: ${trade.entry_price:,.2f}")
            print(f"  Size: {trade.size}")
            print(f"  Opened: {trade.opened_at}")
            print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test real-time trade monitoring'
    )
    parser.add_argument(
        '--monitor',
        type=int,
        metavar='SECONDS',
        help='Run live monitoring for specified seconds (e.g., 30)'
    )
    parser.add_argument(
        '--prices',
        action='store_true',
        help='Test real-time price fetching'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current open trades'
    )
    
    args = parser.parse_args()
    
    if args.prices:
        test_price_fetching()
    elif args.show:
        show_current_trades()
    elif args.monitor:
        test_real_time_monitoring(duration=args.monitor)
    else:
        # Default: show prices and trades
        test_price_fetching()
        show_current_trades()
        print("\nℹ️  Options:")
        print("  --prices : Test price fetching")
        print("  --show   : Show open trades")
        print("  --monitor 30 : Run live monitoring for 30 seconds")
