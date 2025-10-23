"""
Test Performance Analytics API Endpoints
Run this script to verify all performance analytics features
"""
import requests
from datetime import datetime


BASE_URL = "http://localhost:5000"


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


def test_symbol_performance():
    """Test individual symbol performance"""
    print_section("1. SYMBOL PERFORMANCE")
    
    # Get BTCUSD performance for last 7 days
    url = f"{BASE_URL}/api/performance/symbol/BTCUSD?days=7"
    print(f"[GET] {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n[OK] Status: {response.status_code}")
        print(f"\nBTCUSD Performance (Last 7 Days):")
        print(f"  Total Trades: {data.get('total_trades', 0)}")
        print(f"  Win Rate: {data.get('win_rate', 0):.2f}%")
        print(f"  Total PnL: ${data.get('total_pnl', 0):.2f}")
        print(f"  Risk/Reward: {data.get('risk_reward_ratio', 0):.2f}")
        print(f"  Avg Hold Time: {data.get('avg_hold_time_minutes', 0):.1f} min")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[X] Error: {e}")
        return False


def test_all_symbols():
    """Test all symbols performance"""
    print_section("2. ALL SYMBOLS PERFORMANCE")
    
    url = f"{BASE_URL}/api/performance/all?days=30"
    print(f"[GET] {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n[OK] Status: {response.status_code}")
        print(f"\nPerformance Summary (Last 30 Days):")
        print(f"  Total Symbols: {data.get('total_symbols', 0)}")
        
        symbols = data.get('symbols', [])
        if symbols:
            print(f"\n  Top 5 Performers:")
            for i, symbol in enumerate(symbols[:5], 1):
                print(
                    f"    {i}. {symbol['symbol']}: "
                    f"${symbol['total_pnl']:.2f} "
                    f"({symbol['win_rate']:.1f}% WR, "
                    f"{symbol['total_trades']} trades)"
                )
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[X] Error: {e}")
        return False


def test_trading_flows():
    """Test trading flow patterns"""
    print_section("3. TRADING FLOW PATTERNS")
    
    url = f"{BASE_URL}/api/performance/flows?days=30"
    print(f"[GET] {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n[OK] Status: {response.status_code}")
        print(f"\nTrading Patterns (Last 30 Days):")
        print(f"  Total Trades Analyzed: {data.get('total_trades_analyzed', 0)}")
        
        # Best hours
        by_hour = data.get('by_hour', {})
        if by_hour:
            best_hours = sorted(
                by_hour.items(),
                key=lambda x: x[1]['win_rate'],
                reverse=True
            )[:3]
            
            print(f"\n  Top 3 Hours (by Win Rate):")
            for hour, stats in best_hours:
                print(
                    f"    Hour {hour}: "
                    f"{stats['win_rate']:.1f}% WR "
                    f"({stats['count']} trades, "
                    f"${stats['total_pnl']:.2f} PnL)"
                )
        
        # Best days
        by_day = data.get('by_day', {})
        if by_day:
            print(f"\n  Performance by Day:")
            for day, stats in by_day.items():
                print(
                    f"    {day}: "
                    f"{stats['win_rate']:.1f}% WR "
                    f"({stats['count']} trades, "
                    f"${stats['total_pnl']:.2f} PnL)"
                )
        
        # Direction analysis
        by_action = data.get('by_action', {})
        if by_action:
            print(f"\n  Performance by Direction:")
            for action, stats in by_action.items():
                print(
                    f"    {action.upper()}: "
                    f"{stats['win_rate']:.1f}% WR "
                    f"({stats['count']} trades, "
                    f"${stats['total_pnl']:.2f} PnL)"
                )
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[X] Error: {e}")
        return False


def test_suggestions():
    """Test improvement suggestions"""
    print_section("4. IMPROVEMENT SUGGESTIONS")
    
    url = f"{BASE_URL}/api/performance/suggestions?days=30"
    print(f"[GET] {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n[OK] Status: {response.status_code}")
        print(f"\nImprovement Suggestions (Last 30 Days):")
        print(f"  Total Suggestions: {data.get('total_suggestions', 0)}")
        
        suggestions = data.get('suggestions', [])
        
        # Group by priority
        high = [s for s in suggestions if s['priority'] == 'high']
        medium = [s for s in suggestions if s['priority'] == 'medium']
        low = [s for s in suggestions if s['priority'] == 'low']
        
        if high:
            print(f"\n  [HIGH PRIORITY] - {len(high)} issues:")
            for s in high:
                print(f"    - {s['suggestion']}")
                print(f"      Details: {s['details']}")
        
        if medium:
            print(f"\n  [MEDIUM PRIORITY] - {len(medium)} improvements:")
            for s in medium:
                print(f"    - {s['suggestion']}")
                print(f"      Details: {s['details']}")
        
        if low:
            print(f"\n  [LOW PRIORITY] - {len(low)} opportunities:")
            for s in low:
                print(f"    - {s['suggestion']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[X] Error: {e}")
        return False


def test_dashboard():
    """Test comprehensive dashboard"""
    print_section("5. PERFORMANCE DASHBOARD")
    
    url = f"{BASE_URL}/api/performance/dashboard?days=7"
    print(f"[GET] {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n[OK] Status: {response.status_code}")
        
        summary = data.get('summary', {})
        print(f"\nOverall Summary (Last 7 Days):")
        print(f"  Total Symbols: {summary.get('total_symbols', 0)}")
        print(f"  Total Trades: {summary.get('total_trades', 0)}")
        print(f"  Overall PnL: ${summary.get('overall_pnl', 0):.2f}")
        print(f"  Overall Win Rate: {summary.get('overall_win_rate', 0):.2f}%")
        
        top = data.get('top_performers', [])
        if top:
            print(f"\n  Top 3 Performers:")
            for symbol in top[:3]:
                print(
                    f"    - {symbol['symbol']}: "
                    f"${symbol['total_pnl']:.2f} "
                    f"({symbol['win_rate']:.1f}% WR)"
                )
        
        worst = data.get('worst_performers', [])
        if worst:
            print(f"\n  Worst 3 Performers:")
            for symbol in worst[:3]:
                print(
                    f"    - {symbol['symbol']}: "
                    f"${symbol['total_pnl']:.2f} "
                    f"({symbol['win_rate']:.1f}% WR)"
                )
        
        suggestions = data.get('suggestions', [])
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        if high_priority:
            print(f"\n  High Priority Actions ({len(high_priority)}):")
            for s in high_priority:
                print(f"    - {s['suggestion']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[X] Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("="*60)
    print(" PERFORMANCE ANALYTICS API TESTS")
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    tests = [
        ("Symbol Performance", test_symbol_performance),
        ("All Symbols", test_all_symbols),
        ("Trading Flows", test_trading_flows),
        ("Improvement Suggestions", test_suggestions),
        ("Performance Dashboard", test_dashboard),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[X] Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[X]"
        print(f"  {status} {name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n  [OK] All tests passed! Performance analytics is ready.")
    else:
        print(
            f"\n  [X] {total - passed} test(s) failed. "
            f"Check if Flask app is running."
        )
    
    print("\n")


if __name__ == "__main__":
    main()
