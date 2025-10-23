"""
Setup Enabled Symbols
Add initial symbols to the database for price collection
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database.session import SessionLocal
from src.models.base import AllowedInstrument


def setup_symbols():
    """Add initial symbols for price collection"""
    session = SessionLocal()
    
    symbols = [
        {
            'symbol': 'BTCUSD',
            'name': 'Bitcoin',
            'instrument_type': 'crypto',
            'base_currency': 'BTC',
            'quote_currency': 'USD',
            'enabled': True
        },
        {
            'symbol': 'ETHUSD',
            'name': 'Ethereum',
            'instrument_type': 'crypto',
            'base_currency': 'ETH',
            'quote_currency': 'USD',
            'enabled': True
        },
        {
            'symbol': 'SOLUSD',
            'name': 'Solana',
            'instrument_type': 'crypto',
            'base_currency': 'SOL',
            'quote_currency': 'USD',
            'enabled': False
        },
    ]
    
    try:
        added = 0
        updated = 0
        
        for symbol_data in symbols:
            existing = session.query(AllowedInstrument).filter(
                AllowedInstrument.symbol == symbol_data['symbol']
            ).first()
            
            if existing:
                # Update
                existing.enabled = symbol_data['enabled']
                existing.name = symbol_data['name']
                updated += 1
                status = symbol_data['enabled']
                print(f"[UPDATE] {symbol_data['symbol']} - "
                      f"Enabled: {status}")
            else:
                # Add new
                instrument = AllowedInstrument(**symbol_data)
                session.add(instrument)
                added += 1
                status = symbol_data['enabled']
                print(f"[ADD] {symbol_data['symbol']} - Enabled: {status}")
        
        session.commit()
        
        print("\n[SUMMARY]")
        print(f"  Added: {added}")
        print(f"  Updated: {updated}")
        print(f"  Total: {added + updated}")
        
        # Show all symbols
        print("\n[ALL SYMBOLS]")
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
    print("SETTING UP SYMBOLS FOR PRICE COLLECTION")
    print("=" * 80)
    print()
    
    setup_symbols()
    
    print()
    print("=" * 80)
    print("[OK] Setup complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Start Flask app: python app.py")
    print("  2. Price collector will start automatically")
    print("  3. View latest prices: GET /api/historical/latest")
    print("  4. View history: GET /api/historical/prices/BTCUSD?hours=1")
    print()
