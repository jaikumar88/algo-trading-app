"""
Fix symbol names for Delta Exchange
Delta Exchange uses symbols like: BTCUSD, ETHUSD, etc (not BTCUSDT)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database.session import SessionLocal
from src.models.base import AllowedInstrument


def fix_symbols():
    """Fix symbol names to match Delta Exchange format"""
    session = SessionLocal()
    
    # Symbol mapping: old -> new
    symbol_map = {
        'BTCUSDT': 'BTCUSD',
        'ETHUSDT': 'ETHUSD',
        'BNBUSDT': 'BNBUSD',
        'XRPUSDT': 'XRPUSD',
        'SOLUSDT': 'SOLUSD',
    }
    
    try:
        print("[CLEANUP] Removing invalid symbols...")
        for old_symbol in symbol_map.keys():
            existing = session.query(AllowedInstrument).filter(
                AllowedInstrument.symbol == old_symbol
            ).first()
            
            if existing:
                session.delete(existing)
                print(f"  [DELETED] {old_symbol}")
        
        # Also clean up extra symbols we added
        extra_symbols = ['BTCUSD', 'ETHUSD', 'SOLUSD']
        for symbol in extra_symbols:
            existing = session.query(AllowedInstrument).filter(
                AllowedInstrument.symbol == symbol
            ).first()
            
            if existing:
                session.delete(existing)
                print(f"  [DELETED] {symbol} (duplicate)")
        
        session.commit()
        print("[OK] Cleanup complete\n")
        
        # Now add correct symbols
        correct_symbols = [
            {
                'symbol': 'BTCUSD',
                'name': 'Bitcoin Perpetual',
                'instrument_type': 'perpetual_futures',
                'base_currency': 'BTC',
                'quote_currency': 'USD',
                'enabled': True
            },
            {
                'symbol': 'ETHUSD',
                'name': 'Ethereum Perpetual',
                'instrument_type': 'perpetual_futures',
                'base_currency': 'ETH',
                'quote_currency': 'USD',
                'enabled': False
            },
        ]
        
        print("[ADDING] Correct Delta Exchange symbols...")
        for symbol_data in correct_symbols:
            instrument = AllowedInstrument(**symbol_data)
            session.add(instrument)
            status = "[ENABLED]" if symbol_data['enabled'] else "[DISABLED]"
            print(f"  {status} {symbol_data['symbol']}")
        
        session.commit()
        
        print("\n[SUMMARY] Symbol configuration:")
        all_symbols = session.query(AllowedInstrument).all()
        for inst in all_symbols:
            status = "[ENABLED]" if inst.enabled else "[DISABLED]"
            print(f"  {status} {inst.symbol} - {inst.name}")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 80)
    print("FIXING SYMBOLS FOR DELTA EXCHANGE")
    print("=" * 80)
    print()
    
    fix_symbols()
    
    print()
    print("=" * 80)
    print("[OK] Symbols fixed!")
    print("=" * 80)
    print()
    print("Restart Flask app to start collecting data:")
    print("  python app.py")
    print()
