# Multi-Symbol TradingView Charts - User Guide

## Overview
A comprehensive charting page that displays multiple cryptocurrency symbols simultaneously using TradingView's advanced charting widgets.

## Features

### 📊 Multiple Chart Layouts
- **1x1**: Single full-screen chart
- **2x2**: 4 charts in a grid (default)
- **3x3**: 9 charts in a grid
- **4x4**: 16 charts in a grid
- **2x1**: 2 charts horizontally
- **1x2**: 2 charts vertically

### ⏱️ Timeframe Options
- 1m, 5m, 15m, 30m (for day trading)
- 1h, 4h (for swing trading)
- 1D, 1W (for position trading)

### 📈 Chart Types
- **Candles**: Traditional candlestick charts (default)
- **Bars**: OHLC bar charts
- **Line**: Simple line chart
- **Area**: Filled area chart

### 🎨 Theme Support
- **Dark Mode**: Easy on the eyes for extended trading sessions
- **Light Mode**: Professional look for presentations

### 🎯 Symbol Selection
- Click on symbol chips to add/remove from grid
- Automatically maps your database symbols to TradingView format
- Supports all enabled instruments from your trading system

## Symbol Mapping

Your database symbols are automatically mapped to TradingView format:

| Your Symbol | TradingView Symbol |
|-------------|-------------------|
| BTCUSD      | BINANCE:BTCUSDT   |
| ETHUSD      | BINANCE:ETHUSDT   |
| ADAUSD      | BINANCE:ADAUSDT   |
| SOLUSD      | BINANCE:SOLUSDT   |
| etc.        | BINANCE:*USDT     |

## How to Use

### 1. Access the Page
Click on **"📊 All Symbols"** in the navigation menu

### 2. Choose Layout
Select your preferred grid layout from the dropdown (default: 2x2 = 4 charts)

### 3. Select Symbols
Click on symbol chips at the top to toggle them on/off
- Selected symbols appear in blue
- Maximum symbols = layout grid size (e.g., 4 for 2x2)

### 4. Adjust Settings
- **Timeframe**: Change the candle/bar interval
- **Chart Type**: Switch between candles, bars, line, or area
- **Theme**: Toggle between dark and light mode

### 5. Analyze
Each chart includes:
- Real-time price data from Binance
- Moving Averages (MA)
- Volume indicator
- Full TradingView toolset (drawing tools, studies, etc.)

## TradingView Features Included

Each chart widget includes:
- ✅ Real-time price updates
- ✅ Technical indicators (MA, Volume)
- ✅ Drawing tools (trendlines, fibonacci, etc.)
- ✅ Multiple timeframes
- ✅ Professional charting interface
- ✅ Price alerts
- ✅ Full-screen mode (double-click chart)

## Tips

### Best Practices
1. **Monitor Multiple Assets**: Use 2x2 or 3x3 layout to watch correlations
2. **Multi-Timeframe Analysis**: Set different charts to different timeframes
3. **Quick Scanning**: Use 4x4 layout to scan many symbols quickly
4. **Deep Analysis**: Use 1x1 layout for detailed technical analysis

### Performance
- Recommended: 2x2 layout (4 charts) for balance of overview and performance
- Maximum: 4x4 layout (16 charts) may be resource-intensive
- For lower-end systems: Use 1x1 or 2x1 layouts

### Symbol Coverage
All enabled instruments from your database are available:
- BTC, ETH, ADA, SOL, BNB, XRP, etc.
- Updated automatically when you add new instruments
- Only shows enabled instruments

## Keyboard Shortcuts (TradingView)

Within each chart:
- **Space**: Toggle crosshair
- **Alt + T**: Add trendline
- **Alt + H**: Add horizontal line
- **Alt + V**: Add vertical line
- **Ctrl + Z**: Undo
- **Ctrl + Y**: Redo
- **Double Click**: Full screen mode

## Troubleshooting

### Charts Not Loading
- Check your internet connection
- Ensure TradingView script is loaded (wait a few seconds)
- Refresh the page

### Wrong Symbols Displayed
- Symbol mapping is automatic based on your database
- Check that instruments are enabled in the database
- Verify symbol names match TradingView format

### Performance Issues
- Reduce number of charts (use smaller grid layout)
- Close unused browser tabs
- Disable unnecessary technical indicators

## Integration with Your Trading System

The charts automatically use:
- ✅ Your database instruments
- ✅ Real-time data from Binance
- ✅ Your theme preferences
- ✅ Responsive design for all screen sizes

## Future Enhancements

Potential additions:
- Save custom layouts
- Custom symbol groups/watchlists
- Sync charts (linked crosshairs)
- Export chart snapshots
- Custom indicator presets
- Alert notifications integration

## Navigation

Access from main menu: **📊 All Symbols**

Related pages:
- **📊 TradingView**: Single-symbol advanced chart
- **📦 Historical**: Historical data analysis
- **📉 Chart**: Basic lightweight chart

---

**Note**: This feature uses TradingView's free widget. For advanced features like more indicators, replay mode, or extended hours data, consider upgrading to TradingView Pro.
