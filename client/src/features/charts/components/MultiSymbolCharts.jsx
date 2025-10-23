import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './MultiSymbolCharts.css';
import { apiClient } from '../../../services/api'

const MultiSymbolCharts = () => {
  const [instruments, setInstruments] = useState([]);
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [interval, setInterval] = useState('5');
  const [chartType, setChartType] = useState('1'); // 1=Candles
  const [theme, setTheme] = useState('dark');
  const [gridLayout, setGridLayout] = useState('2x2'); // 1x1, 2x2, 3x3, 4x4
  const [loading, setLoading] = useState(true);
  const widgetRefs = useRef({});
  const scriptLoaded = useRef(false);

  // Interval options
  const intervals = [
    { value: '1', label: '1m' },
    { value: '5', label: '5m' },
    { value: '15', label: '15m' },
    { value: '30', label: '30m' },
    { value: '60', label: '1h' },
    { value: '240', label: '4h' },
    { value: 'D', label: '1D' },
    { value: 'W', label: '1W' }
  ];

  // Grid layout options
  const layouts = [
    { value: '1x1', label: '1 Chart', cols: 1, rows: 1 },
    { value: '2x2', label: '4 Charts', cols: 2, rows: 2 },
    { value: '3x3', label: '9 Charts', cols: 3, rows: 3 },
    { value: '4x4', label: '16 Charts', cols: 4, rows: 4 },
    { value: '2x1', label: '2 Charts (Horiz)', cols: 2, rows: 1 },
    { value: '1x2', label: '2 Charts (Vert)', cols: 1, rows: 2 }
  ];

  // Fetch instruments
  useEffect(() => {
    fetchInstruments();
  }, []);

  // Load TradingView script once
  useEffect(() => {
    if (scriptLoaded.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      scriptLoaded.current = true;
      console.log('TradingView script loaded');
    };
    document.head.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  const fetchInstruments = async () => {
    try {
      const response = await apiClient.get('/api/trading/instruments');
      const data = response.data.instruments || response.data || [];
      
      // Filter enabled instruments and map to TradingView symbols
      const enabledInstruments = data
        .filter(inst => inst.enabled)
        .map(inst => ({
          symbol: inst.symbol,
          name: inst.name,
          tvSymbol: mapToTradingViewSymbol(inst.symbol)
        }));
      
      setInstruments(enabledInstruments);
      
      // Select first 4 by default for 2x2 layout
      if (enabledInstruments.length > 0) {
        setSelectedSymbols(enabledInstruments.slice(0, 4));
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching instruments:', error);
      setLoading(false);
    }
  };

  const mapToTradingViewSymbol = (symbol) => {
    // Map your symbols to TradingView format
    const symbolMap = {
      'BTCUSD': 'BINANCE:BTCUSDT',
      'ETHUSD': 'BINANCE:ETHUSDT',
      'ADAUSD': 'BINANCE:ADAUSDT',
      'DOGEUSD': 'BINANCE:DOGEUSDT',
      'SOLUSD': 'BINANCE:SOLUSDT',
      'BNBUSD': 'BINANCE:BNBUSDT',
      'XRPUSD': 'BINANCE:XRPUSDT',
      'MATICUSD': 'BINANCE:MATICUSDT',
      'LINKUSD': 'BINANCE:LINKUSDT',
      'DOTUSD': 'BINANCE:DOTUSDT'
    };

    return symbolMap[symbol] || `BINANCE:${symbol.replace('USD', 'USDT')}`;
  };

  // Initialize charts when symbols or settings change
  useEffect(() => {
    if (!scriptLoaded.current || selectedSymbols.length === 0) return;

    // Wait for TradingView to be available
    const checkAndInitialize = () => {
      if (typeof window.TradingView !== 'undefined') {
        initializeCharts();
      } else {
        setTimeout(checkAndInitialize, 100);
      }
    };

    checkAndInitialize();

    return () => {
      // Cleanup widgets
      Object.values(widgetRefs.current).forEach(widget => {
        if (widget && widget.remove) {
          widget.remove();
        }
      });
      widgetRefs.current = {};
    };
  }, [selectedSymbols, interval, chartType, theme]);

  const initializeCharts = () => {
    selectedSymbols.forEach((instrument, index) => {
      const containerId = `tradingview_${index}`;
      const container = document.getElementById(containerId);
      
      if (!container) return;

      // Clear previous widget
      container.innerHTML = '';

      try {
        widgetRefs.current[index] = new window.TradingView.widget({
          container_id: containerId,
          autosize: true,
          symbol: instrument.tvSymbol,
          interval: interval,
          timezone: 'Etc/UTC',
          theme: theme,
          style: chartType,
          locale: 'en',
          toolbar_bg: theme === 'dark' ? '#0f0f0f' : '#f1f3f6',
          enable_publishing: false,
          allow_symbol_change: false,
          hide_top_toolbar: false,
          hide_side_toolbar: false,
          save_image: false,
          studies: [
            chartType === '1' ? 'MASimple@tv-basicstudies' : null,
            'Volume@tv-basicstudies'
          ].filter(Boolean),
          disabled_features: [
            'header_symbol_search',
            'header_compare',
            'display_market_status'
          ],
          enabled_features: [
            'hide_left_toolbar_by_default'
          ],
          overrides: {
            'mainSeriesProperties.candleStyle.upColor': '#26a69a',
            'mainSeriesProperties.candleStyle.downColor': '#ef5350',
            'mainSeriesProperties.candleStyle.borderUpColor': '#26a69a',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ef5350',
            'mainSeriesProperties.candleStyle.wickUpColor': '#26a69a',
            'mainSeriesProperties.candleStyle.wickDownColor': '#ef5350'
          }
        });
      } catch (error) {
        console.error(`Error initializing chart for ${instrument.symbol}:`, error);
      }
    });
  };

  const handleLayoutChange = (layout) => {
    setGridLayout(layout);
    const layoutConfig = layouts.find(l => l.value === layout);
    const maxCharts = layoutConfig.cols * layoutConfig.rows;
    
    // Adjust selected symbols based on new layout
    if (selectedSymbols.length > maxCharts) {
      setSelectedSymbols(selectedSymbols.slice(0, maxCharts));
    } else if (selectedSymbols.length < maxCharts && instruments.length > selectedSymbols.length) {
      const additionalSymbols = instruments
        .filter(inst => !selectedSymbols.find(s => s.symbol === inst.symbol))
        .slice(0, maxCharts - selectedSymbols.length);
      setSelectedSymbols([...selectedSymbols, ...additionalSymbols]);
    }
  };

  const handleSymbolToggle = (instrument) => {
    const isSelected = selectedSymbols.find(s => s.symbol === instrument.symbol);
    const layoutConfig = layouts.find(l => l.value === gridLayout);
    const maxCharts = layoutConfig.cols * layoutConfig.rows;

    if (isSelected) {
      setSelectedSymbols(selectedSymbols.filter(s => s.symbol !== instrument.symbol));
    } else if (selectedSymbols.length < maxCharts) {
      setSelectedSymbols([...selectedSymbols, instrument]);
    } else {
      // Replace last one
      const newSymbols = [...selectedSymbols];
      newSymbols[newSymbols.length - 1] = instrument;
      setSelectedSymbols(newSymbols);
    }
  };

  const getGridStyle = () => {
    const layoutConfig = layouts.find(l => l.value === gridLayout);
    return {
      gridTemplateColumns: `repeat(${layoutConfig.cols}, 1fr)`,
      gridTemplateRows: `repeat(${layoutConfig.rows}, 1fr)`
    };
  };

  if (loading) {
    return <div className="multi-charts-loading">Loading instruments...</div>;
  }

  return (
    <div className="multi-symbol-charts">
      <div className="charts-header">
        <h2>📊 Multi-Symbol TradingView Charts</h2>
        
        <div className="charts-controls">
          <div className="control-group">
            <label>Layout</label>
            <select value={gridLayout} onChange={(e) => handleLayoutChange(e.target.value)}>
              {layouts.map(layout => (
                <option key={layout.value} value={layout.value}>
                  {layout.label}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Timeframe</label>
            <select value={interval} onChange={(e) => setInterval(e.target.value)}>
              {intervals.map(int => (
                <option key={int.value} value={int.value}>
                  {int.label}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Chart Type</label>
            <select value={chartType} onChange={(e) => setChartType(e.target.value)}>
              <option value="1">Candles</option>
              <option value="0">Bars</option>
              <option value="3">Line</option>
              <option value="9">Area</option>
            </select>
          </div>

          <div className="control-group">
            <label>Theme</label>
            <select value={theme} onChange={(e) => setTheme(e.target.value)}>
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>
        </div>
      </div>

      <div className="symbol-selector">
        <div className="symbol-chips">
          {instruments.map(instrument => {
            const isSelected = selectedSymbols.find(s => s.symbol === instrument.symbol);
            return (
              <button
                key={instrument.symbol}
                className={`symbol-chip ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSymbolToggle(instrument)}
              >
                {instrument.symbol}
              </button>
            );
          })}
        </div>
      </div>

      <div className="charts-grid" style={getGridStyle()}>
        {selectedSymbols.map((instrument, index) => (
          <div key={`${instrument.symbol}_${index}`} className="chart-container">
            <div className="chart-title">{instrument.name || instrument.symbol}</div>
            <div id={`tradingview_${index}`} className="tradingview-widget"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MultiSymbolCharts;
