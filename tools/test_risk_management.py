"""
Test Risk Management System
Tests SL, trailing stops, and emergency exits
"""
import os
import sys
from decimal import Decimal
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.services.risk_management_service import get_risk_manager
from src.database.session import SessionLocal
from src.models.base import Trade


def create_test_trade(symbol, side, entry_price, status='open'):
    """Create a test trade in database"""
    with SessionLocal() as db:
        trade = Trade(
            symbol=symbol,
            side=side,
            entry_price=Decimal(str(entry_price)),
            size=Decimal('1'),
            status=status,
            opened_at=datetime.utcnow()
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        print(f"Created test trade: {trade.id} - {side} {symbol} @ ${entry_price}")
        return trade.id


def test_risk_scenarios():
    """Test different risk management scenarios"""
    print("=" * 80)
    print("TESTING RISK MANAGEMENT SCENARIOS")
    print("=" * 80)
    
    risk_manager = get_risk_manager()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Normal - No action',
            'entry': 100000.0,
            'current': 100050.0,  # +0.05% profit
            'side': 'BUY',
            'expected': False
        },
        {
            'name': 'Stop Loss Hit (-1%)',
            'entry': 100000.0,
            'current': 99000.0,  # -1% loss
            'side': 'BUY',
            'expected': True
        },
        {
            'name': 'Trailing Stop Hit (was 2%, now 0.5%)',
            'entry': 100000.0,
            'current': 100500.0,  # +0.5% (assume it was higher)
            'side': 'BUY',
            'expected': False  # Won't trigger without tracking peak
        },
        {
            'name': 'Emergency Spike (+10%)',
            'entry': 100000.0,
            'current': 110000.0,  # +10% spike
            'side': 'BUY',
            'expected': True
        },
        {
            'name': 'Short Stop Loss Hit',
            'entry': 100000.0,
            'current': 101000.0,  # -1% loss for short
            'side': 'SELL',
            'expected': True
        },
        {
            'name': 'Short in Profit',
            'entry': 100000.0,
            'current': 98000.0,  # +2% profit for short
            'side': 'SELL',
            'expected': False
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'-' * 80}")
        print(f"Scenario {i}: {scenario['name']}")
        print(f"Entry: ${scenario['entry']:,.2f}")
        print(f"Current: ${scenario['current']:,.2f}")
        print(f"Side: {scenario['side']}")
        
        # Create dummy trade object
        class DummyTrade:
            def __init__(self):
                self.id = i
                self.symbol = 'BTCUSD'
                self.side = scenario['side']
                self.entry_price = Decimal(str(scenario['entry']))
        
        trade = DummyTrade()
        current_price = Decimal(str(scenario['current']))
        
        should_close, reason, exit_type = risk_manager.should_close_trade(
            trade, current_price
        )
        
        pnl_pct = risk_manager.calculate_pnl_pct(
            trade.entry_price, current_price, trade.side
        )
        
        print(f"P&L: {pnl_pct*100:.2f}%")
        print(f"Should Close: {should_close}")
        if should_close:
            print(f"Reason: {reason}")
            print(f"Exit Type: {exit_type}")
        
        status = "✅ PASS" if should_close == scenario['expected'] else "❌ FAIL"
        print(status)
    
    print("\n" + "=" * 80)


def test_with_real_trades():
    """Test with actual database trades"""
    print("\n" + "=" * 80)
    print("TESTING WITH REAL DATABASE TRADES")
    print("=" * 80)
    
    # Create some test trades
    print("\nCreating test trades...")
    trade_ids = []
    
    # Trade 1: Normal profit
    trade_ids.append(create_test_trade('BTCUSD', 'BUY', 100000.0))
    
    # Trade 2: Should hit SL
    trade_ids.append(create_test_trade('ETHUSD', 'BUY', 3000.0))
    
    print(f"\nCreated {len(trade_ids)} test trades")
    
    # Test with mock price data
    price_data = {
        'BTCUSD': Decimal('100500.0'),  # +0.5% profit
        'ETHUSD': Decimal('2970.0'),     # -1% loss - should trigger SL
    }
    
    print("\nChecking trades with mock prices:")
    for symbol, price in price_data.items():
        print(f"  {symbol}: ${price:,.2f}")
    
    risk_manager = get_risk_manager()
    trades_to_close = risk_manager.check_all_open_trades(price_data)
    
    print(f"\nResult: {len(trades_to_close)} trade(s) should be closed")
    
    for trade_info in trades_to_close:
        print(f"\nTrade to close:")
        print(f"  Symbol: {trade_info['trade'].symbol}")
        print(f"  Side: {trade_info['trade'].side}")
        print(f"  Entry: ${trade_info['trade'].entry_price}")
        print(f"  Current: ${trade_info['current_price']}")
        print(f"  P&L: {trade_info['pnl_pct']:.2f}%")
        print(f"  Reason: {trade_info['reason']}")
        print(f"  Exit Type: {trade_info['exit_type']}")
    
    # Clean up test trades
    print("\nCleaning up test trades...")
    with SessionLocal() as db:
        for trade_id in trade_ids:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                db.delete(trade)
        db.commit()
    print("✅ Test trades deleted")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test risk management')
    parser.add_argument('--real', action='store_true', 
                        help='Test with real database trades')
    args = parser.parse_args()
    
    # Run scenario tests
    test_risk_scenarios()
    
    # Run real trade tests if requested
    if args.real:
        test_with_real_trades()
    else:
        print("\nℹ️  To test with real database trades, run with --real flag")
