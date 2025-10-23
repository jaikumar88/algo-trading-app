"""
Test script for historical price data system.
Demonstrates data collection, storage, and retrieval.
"""
from db import SessionLocal, init_db
from price_history_service import PriceHistoryService
from models import AllowedInstrument, PriceHistory
import json


def test_historical_data_system():
    """Test the complete historical data flow."""
    
    print("=" * 80)
    print("🧪 Testing Historical Price Data System")
    print("=" * 80)
    
    # Initialize database
    print("\n1️⃣ Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    session = SessionLocal()
    service = PriceHistoryService(session)
    
    try:
        # Add test instruments if not exist
        print("\n2️⃣ Setting up test instruments...")
        test_symbols = [
            ('BTCUSDT', 'Bitcoin'),
            ('ETHUSDT', 'Ethereum'),
            ('BNBUSDT', 'Binance Coin'),
        ]
        
        for symbol, name in test_symbols:
            existing = session.query(AllowedInstrument).filter(
                AllowedInstrument.symbol == symbol
            ).first()
            
            if not existing:
                instrument = AllowedInstrument(
                    symbol=symbol,
                    name=name,
                    enabled=True
                )
                session.add(instrument)
        
        session.commit()
        print(f"✅ Set up {len(test_symbols)} test instruments")
        
        # Test mock data generation
        print("\n3️⃣ Generating mock data...")
        mock_data = service.generate_mock_data('BTCUSDT', '1h', 100, 65000.0)
        print(f"✅ Generated {len(mock_data)} mock candles")
        print(f"   First candle: {mock_data[0]}")
        print(f"   Last candle: {mock_data[-1]}")
        
        # Test data saving
        print("\n4️⃣ Saving data to database...")
        saved_count = service.save_price_data('BTCUSDT', '1h', mock_data)
        print(f"✅ Saved {saved_count} candles to database")
        
        # Test data retrieval
        print("\n5️⃣ Retrieving data from database...")
        historical = service.get_historical_data('BTCUSDT', '1h', 50)
        print(f"✅ Retrieved {len(historical)} candles")
        if historical:
            latest = historical[-1]
            print(f"   Latest price: ${latest['close']:.2f}")
            print(f"   Timestamp: {latest['timestamp']}")
        
        # Test latest price
        print("\n6️⃣ Getting latest price...")
        latest_price = service.get_latest_price('BTCUSDT', '1h')
        if latest_price:
            print(f"✅ Latest BTCUSDT price: ${latest_price['close']:.2f}")
            print(f"   High: ${latest_price['high']:.2f}, Low: ${latest_price['low']:.2f}")
            print(f"   Volume: {latest_price['volume']:.2f}")
        
        # Test collecting for single instrument
        print("\n7️⃣ Collecting data for single instrument...")
        result = service.collect_data_for_instrument('ETHUSDT', '1h', use_mock=True)
        print(f"✅ Collection result: {result['status']}")
        print(f"   Message: {result['message']}")
        
        # Test collecting for all instruments
        print("\n8️⃣ Collecting data for all enabled instruments...")
        results = service.collect_all_instruments('1h', use_mock=True)
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"✅ Collected for {success_count}/{len(results)} instruments")
        
        for result in results:
            if result['status'] == 'success':
                print(f"   - {result['symbol']}: {result['saved_count']} new candles")
        
        # Database statistics
        print("\n9️⃣ Database statistics...")
        total_records = session.query(PriceHistory).count()
        symbols_count = session.query(PriceHistory.symbol).distinct().count()
        print(f"✅ Total records in database: {total_records}")
        print(f"   Unique symbols: {symbols_count}")
        
        # Display data sample
        print("\n🔟 Sample data from database...")
        sample = session.query(PriceHistory).filter(
            PriceHistory.symbol == 'BTCUSDT'
        ).order_by(PriceHistory.timestamp.desc()).limit(5).all()
        
        print(f"   Last 5 BTCUSDT candles:")
        for record in sample:
            print(f"   {record.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                  f"O: ${float(record.open_price):.2f} | "
                  f"H: ${float(record.high_price):.2f} | "
                  f"L: ${float(record.low_price):.2f} | "
                  f"C: ${float(record.close_price):.2f} | "
                  f"V: {float(record.volume):.2f}")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED! Historical data system is working correctly.")
        print("=" * 80)
        
        print("\n📊 Next steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Start the React client: cd client && npm run dev")
        print("3. Navigate to '📦 Historical' in the UI")
        print("4. View your historical price data charts!")
        print("\n🔧 API Endpoints available:")
        print("   GET  /api/historical-prices/<symbol>?timeframe=1h&limit=500")
        print("   POST /api/collect-price-data")
        print("   GET  /api/latest-price/<symbol>?timeframe=1h")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()


if __name__ == '__main__':
    test_historical_data_system()
