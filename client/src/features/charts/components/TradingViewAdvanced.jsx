import { useState, useEffect, useRef } from 'react';
import Select from 'react-select';
import axios from 'axios';
import './TradingViewChart.css';
import { apiClient } from '../../../services/api'

const TradingViewAdvanced = () => {
  const containerRef = useRef(null);
  const widgetRef = useRef(null);
  const scriptRef = useRef(null);

  const [instruments, setInstruments] = useState([]);
  const [selectedInstrument, setSelectedInstrument] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [interval, setInterval] = useState('5');
  const [chartType, setChartType] = useState('1'); // 1=Candles, 0=Bars, 3=Line, etc.
  const [studies, setStudies] = useState({
    ma: true,
    rsi: false,
    macd: false,
    bb: false,
    volume: true
  });

  // Fetch instruments from your database
  useEffect(() => {
    fetchInstruments();
  }, []);

  const fetchInstruments = async () => {
    try {
      const response = await apiClient.get('/api/trading/instruments');
      
      // Map to TradingView symbols
      const instrumentOptions = response.data.map(inst => {
        // Convert your symbols to TradingView format
        let tvSymbol = `BINANCE:${inst.symbol.replace('USD', 'USDT')}`;
        
        // Handle different instrument types
        if (inst.symbol.includes('BTC')) tvSymbol = 'BINANCE:BTCUSDT';
        else if (inst.symbol.includes('ETH')) tvSymbol = 'BINANCE:ETHUSDT';
        else if (inst.symbol.includes('ADA')) tvSymbol = 'BINANCE:ADAUSDT';
        // Add more mappings as needed
        
        return {
          value: tvSymbol,
          label: `${inst.name} (${inst.symbol})`,
          symbol: inst.symbol
        };
      });
      
      setInstruments(instrumentOptions);
      if (instrumentOptions.length > 0) {
        setSelectedInstrument(instrumentOptions[0]);
      }
    } catch (error) {
      console.error('Error fetching instruments:', error);
    }
  };

  // Initialize/Update TradingView Widget
  useEffect(() => {
    if (!selectedInstrument) return;

    // Clean up previous widget
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    // Remove old script
    if (scriptRef.current) {
      scriptRef.current.remove();
    }

    // Create and load TradingView script
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      if (typeof window.TradingView !== 'undefined' && containerRef.current) {
        
        // Build studies array
        const studiesArray = [];
        if (studies.ma) studiesArray.push('MASimple@tv-basicstudies');
        if (studies.rsi) studiesArray.push('RSI@tv-basicstudies');
        if (studies.macd) studiesArray.push('MACD@tv-basicstudies');
        if (studies.bb) studiesArray.push('BB@tv-basicstudies');
        if (studies.volume) studiesArray.push('Volume@tv-basicstudies');

        widgetRef.current = new window.TradingView.widget({
          container_id: 'tradingview_advanced',
          autosize: true,
          symbol: selectedInstrument.value,
          interval: interval,
          timezone: 'Etc/UTC',
          theme: theme,
          style: chartType,
          locale: 'en',
          toolbar_bg: theme === 'dark' ? '#0f0f0f' : '#f1f3f6',
          enable_publishing: false,
          allow_symbol_change: true,
          save_image: true,
          studies: studiesArray,
          
          // UI Settings for smooth presentation
          hide_top_toolbar: false,
          hide_legend: false,
          hide_side_toolbar: false,
          details: true,
          hotlist: true,
          calendar: true,
          show_popup_button: true,
          popup_width: '1000',
          popup_height: '650',
          
          // Enable live data updates
          enabled_features: ['study_templates'],
          disabled_features: ['use_localstorage_for_settings'],
          
          // Volume customization
          studies_overrides: {
            'volume.volume.color.0': '#ef535080',
            'volume.volume.color.1': '#26a69a80',
            'volume.volume.transparency': 80,
            'volume.options.showMA': false,
          },
          
          // Chart styling for smooth presentation
          overrides: {
            // Candle colors
            'mainSeriesProperties.candleStyle.upColor': '#26a69a',
            'mainSeriesProperties.candleStyle.downColor': '#ef5350',
            'mainSeriesProperties.candleStyle.borderUpColor': '#26a69a',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ef5350',
            'mainSeriesProperties.candleStyle.wickUpColor': '#26a69a',
            'mainSeriesProperties.candleStyle.wickDownColor': '#ef5350',
            
            // Bar colors (for bar chart type)
            'mainSeriesProperties.barStyle.upColor': '#26a69a',
            'mainSeriesProperties.barStyle.downColor': '#ef5350',
            
            // Line colors
            'mainSeriesProperties.lineStyle.color': '#2962FF',
            'mainSeriesProperties.lineStyle.linewidth': 2,
            
            // Area colors
            'mainSeriesProperties.areaStyle.color1': '#2962FF',
            'mainSeriesProperties.areaStyle.color2': '#2962FF',
            'mainSeriesProperties.areaStyle.linecolor': '#2962FF',
            
            // Background and grid
            'paneProperties.background': theme === 'dark' ? '#0f0f0f' : '#ffffff',
            'paneProperties.backgroundType': 'solid',
            'paneProperties.vertGridProperties.color': theme === 'dark' ? '#1a1a1a' : '#e1e1e1',
            'paneProperties.vertGridProperties.style': 0,
            'paneProperties.horzGridProperties.color': theme === 'dark' ? '#1a1a1a' : '#e1e1e1',
            'paneProperties.horzGridProperties.style': 0,
            
            // Crosshair
            'paneProperties.crossHairProperties.color': '#758696',
            'paneProperties.crossHairProperties.width': 1,
            'paneProperties.crossHairProperties.style': 2,
            
            // Scales
            'scalesProperties.textColor': theme === 'dark' ? '#d1d4dc' : '#131722',
            'scalesProperties.lineColor': theme === 'dark' ? '#2b2b43' : '#e1e1e1',
            'scalesProperties.fontSize': 12,
            
            // Watermark (optional - can disable)
            'paneProperties.legendProperties.showLegend': true,
            'paneProperties.legendProperties.showStudyArguments': true,
            'paneProperties.legendProperties.showStudyTitles': true,
            'paneProperties.legendProperties.showStudyValues': true,
            'paneProperties.legendProperties.showSeriesTitle': true,
            'paneProperties.legendProperties.showSeriesOHLC': true,
            
            // Timezone
            'paneProperties.topMargin': 10,
            'paneProperties.bottomMargin': 8,
          },
          
          // Loading screen customization
          loading_screen: {
            backgroundColor: theme === 'dark' ? '#0f0f0f' : '#ffffff',
            foregroundColor: theme === 'dark' ? '#2962FF' : '#2962FF',
          },
        });
      }
    };

    scriptRef.current = script;
    document.head.appendChild(script);

    return () => {
      if (scriptRef.current) {
        scriptRef.current.remove();
      }
    };
  }, [selectedInstrument, theme, interval, chartType, studies]);

  const toggleStudy = (study) => {
    setStudies(prev => ({
      ...prev,
      [study]: !prev[study]
    }));
  };

  const intervalOptions = [
    { value: '1', label: '1 Minute' },
    { value: '5', label: '5 Minutes' },
    { value: '15', label: '15 Minutes' },
    { value: '60', label: '1 Hour' },
    { value: '240', label: '4 Hours' },
    { value: 'D', label: '1 Day' },
    { value: 'W', label: '1 Week' },
  ];

  const chartTypeOptions = [
    { value: '0', label: 'Bars' },
    { value: '1', label: 'Candles' },
    { value: '2', label: 'Line' },
    { value: '3', label: 'Area' },
    { value: '8', label: 'Heikin Ashi' },
    { value: '9', label: 'Hollow Candles' },
  ];

  return (
    <div className="tradingview-advanced-wrapper">
      <div className="tv-header">
        <h1>📊 TradingView Professional Chart</h1>
        <p>Full-featured charting with 100+ indicators, drawing tools, and analysis</p>
      </div>

      <div className="tv-controls">
        <div className="control-group">
          <label>Instrument</label>
          <Select
            options={instruments}
            value={selectedInstrument}
            onChange={setSelectedInstrument}
            className="instrument-select"
            classNamePrefix="select"
            placeholder="Select instrument..."
          />
        </div>

        <div className="control-group">
          <label>Interval</label>
          <Select
            options={intervalOptions}
            value={intervalOptions.find(opt => opt.value === interval)}
            onChange={(option) => setInterval(option.value)}
            className="interval-select"
            classNamePrefix="select"
          />
        </div>

        <div className="control-group">
          <label>Chart Type</label>
          <Select
            options={chartTypeOptions}
            value={chartTypeOptions.find(opt => opt.value === chartType)}
            onChange={(option) => setChartType(option.value)}
            className="chart-type-select"
            classNamePrefix="select"
          />
        </div>

        <div className="control-group">
          <label>Theme</label>
          <button
            className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
          </button>
        </div>
      </div>

      <div className="tv-studies">
        <h3>Quick Studies</h3>
        <div className="studies-grid">
          <button
            className={`study-btn ${studies.ma ? 'active' : ''}`}
            onClick={() => toggleStudy('ma')}
          >
            Moving Average
          </button>
          <button
            className={`study-btn ${studies.rsi ? 'active' : ''}`}
            onClick={() => toggleStudy('rsi')}
          >
            RSI
          </button>
          <button
            className={`study-btn ${studies.macd ? 'active' : ''}`}
            onClick={() => toggleStudy('macd')}
          >
            MACD
          </button>
          <button
            className={`study-btn ${studies.bb ? 'active' : ''}`}
            onClick={() => toggleStudy('bb')}
          >
            Bollinger Bands
          </button>
          <button
            className={`study-btn ${studies.volume ? 'active' : ''}`}
            onClick={() => toggleStudy('volume')}
          >
            Volume
          </button>
        </div>
        <p className="studies-note">
          💡 <strong>Tip:</strong> Use the toolbar above the chart to add 100+ more indicators, 
          drawing tools, alerts, and save your layouts!
        </p>
      </div>

      <div className="tv-chart-wrapper">
        <div id="tradingview_advanced" ref={containerRef} />
      </div>

      <div className="tv-features-info">
        <div className="feature-card">
          <h4>📈 Available Features</h4>
          <ul>
            <li>✅ 100+ Technical Indicators</li>
            <li>✅ Drawing Tools (Trend lines, Fibonacci, etc.)</li>
            <li>✅ Multiple Chart Types</li>
            <li>✅ Compare Symbols</li>
            <li>✅ Save Layouts</li>
            <li>✅ Price Alerts</li>
            <li>✅ Volume Profile</li>
            <li>✅ Economic Calendar</li>
          </ul>
        </div>

        <div className="feature-card">
          <h4>🎯 How to Use</h4>
          <ul>
            <li><strong>Add Indicators:</strong> Click "Indicators" button in toolbar</li>
            <li><strong>Draw:</strong> Click drawing tools on left sidebar</li>
            <li><strong>Compare:</strong> Click "+" icon to overlay symbols</li>
            <li><strong>Alerts:</strong> Right-click on chart → "Add alert"</li>
            <li><strong>Save:</strong> Click cloud icon to save your layout</li>
            <li><strong>Zoom:</strong> Scroll or pinch to zoom in/out</li>
          </ul>
        </div>

        <div className="feature-card">
          <h4>⚙️ Advanced Options</h4>
          <ul>
            <li><strong>Chart Settings:</strong> Click gear icon</li>
            <li><strong>Timeframes:</strong> Use top toolbar for any timeframe</li>
            <li><strong>Templates:</strong> Save and load chart templates</li>
            <li><strong>Screenshots:</strong> Click camera icon</li>
            <li><strong>Fullscreen:</strong> Click fullscreen icon</li>
            <li><strong>Undo/Redo:</strong> Available in top toolbar</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TradingViewAdvanced;
