"""
Test Symbol Synchronization
Fetch symbols from Delta Exchange and update database
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.delta_exchange_service import get_delta_trader


def main():
    """Run symbol sync test"""
    print("=" * 80)
    print("DELTA EXCHANGE SYMBOL SYNC TEST")
    print("=" * 80)
    print()
    
    trader = get_delta_trader()
    
    # Test 1: Sync only perpetual futures (auto-enable)
    print("\n[TEST 1] Syncing perpetual futures only (auto-enable)...")
    print("-" * 80)
    result = trader.sync_symbols_to_db(
        auto_enable=True,
        product_types=['perpetual_futures']
    )
    
    print("\n[RESULT]")
    print(f"  Success: {result['success']}")
    print(f"  Added: {result['added']}")
    print(f"  Updated: {result['updated']}")
    print(f"  Total: {result['total']}")
    
    if not result['success']:
        print(f"  Error: {result.get('error')}")
        return
    
    # Test 2: Get enabled symbols from database
    print("\n" + "=" * 80)
    print("[TEST 2] Getting enabled symbols from database...")
    print("-" * 80)
    
    from src.database.session import SessionLocal
    from src.models.base import AllowedInstrument
    
    session = SessionLocal()
    enabled_instruments = session.query(AllowedInstrument).filter(
        AllowedInstrument.enabled == True  # noqa: E712
    ).all()
    session.close()
    
    symbols = [inst.symbol for inst in enabled_instruments]
    
    print(f"\n[ENABLED SYMBOLS] ({len(symbols)} total)")
    for i, symbol in enumerate(symbols[:20], 1):
        print(f"  {i}. {symbol}")
    
    if len(symbols) > 20:
        print(f"  ... and {len(symbols) - 20} more")
    
    print()
    print("=" * 80)
    print("[OK] Symbol sync test completed!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Start Flask app: python app.py")
    print("  2. Price collector will use these symbols")
    print("  3. Delta Exchange API endpoints available:")
    print("     - POST /api/delta/sync/symbols")
    print("     - POST /api/delta/sync/perpetuals")
    print("     - GET /api/delta/products")
    print("     - GET /api/delta/status")
    print()


if __name__ == "__main__":
    main()
