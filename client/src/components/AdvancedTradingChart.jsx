import { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';
import { apiUrl } from '../services/api';
import './AdvancedTradingChart.css';

const AdvancedTradingChart = () => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  
  const [instruments, setInstruments] = useState([]);
  const [selectedInstrument, setSelectedInstrument] = useState('');
  const [timeframe, setTimeframe] = useState('5m');
  const [positions, setPositions] = useState([]); // Open positions
  const [chartLoaded, setChartLoaded] = useState(false);
  const [crosshairPrice, setCrosshairPrice] = useState(null);
  const [showOrderPanel, setShowOrderPanel] = useState(false);
  const [orderType, setOrderType] = useState('market');
  const [orderSide, setOrderSide] = useState('buy');
  const [orderSize, setOrderSize] = useState('0.01');
  const [orderPrice, setOrderPrice] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Position markers on chart
  const positionMarkersRef = useRef([]);

  // Load instruments from backend
  useEffect(() => {
    loadInstruments();
    loadPositions();
  }, []);

  const loadInstruments = async () => {
    try {
      const response = await axios.get(apiUrl('/api/trading/instruments'));
      const instrumentsList = response.data.instruments || response.data || [];
      setInstruments(instrumentsList);
      if (instrumentsList.length > 0 && !selectedInstrument) {
        setSelectedInstrument(instrumentsList[0].symbol || instrumentsList[0].id);
      }
    } catch (error) {
      console.error('Error loading instruments:', error);
      setInstruments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadPositions = async () => {
    try {
      const response = await axios.get(apiUrl('/api/trading/positions'));
      const positionsList = response.data.positions || response.data || [];
      setPositions(positionsList);
    } catch (error) {
      console.error('Error loading positions:', error);
    }
  };

  const loadChartData = async (symbol, tf) => {
    try {
      // Call backend API for chart data
      const response = await axios.get(apiUrl('/api/chart/data'), {
        params: {
          symbol: symbol,
          timeframe: tf,
          limit: 500
        }
      });
      return response.data.data || response.data || [];
    } catch (error) {
      console.error('Error loading chart data:', error);
      return [];
    }
  };

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { color: '#0f0f0f' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1f1f1f' },
        horzLines: { color: '#1f1f1f' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#758696',
          width: 1,
          style: 3,
          labelBackgroundColor: '#2962FF',
        },
        horzLine: {
          color: '#758696',
          width: 1,
          style: 3,
          labelBackgroundColor: '#2962FF',
        },
      },
      rightPriceScale: {
        borderColor: '#2B2B43',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: '#2B2B43',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    candleSeriesRef.current = candleSeries;

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    volumeSeriesRef.current = volumeSeries;

    // Crosshair move handler
    chart.subscribeCrosshairMove((param) => {
      if (param.time && param.seriesData.size > 0) {
        const price = param.seriesData.get(candleSeriesRef.current);
        if (price) {
          setCrosshairPrice(price.close);
        }
      }
    });

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    setChartLoaded(true);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Load data when instrument or timeframe changes
  useEffect(() => {
    if (!chartLoaded || !candleSeriesRef.current || !volumeSeriesRef.current || !selectedInstrument) return;

    const loadData = async () => {
      const data = await loadChartData(selectedInstrument, timeframe);
      
      if (!data || data.length === 0) return;
      
      // Set candlestick data
      candleSeriesRef.current.setData(data);
      
      // Set volume data
      const volumeData = data.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#26a69a40' : '#ef535040',
      }));
      volumeSeriesRef.current.setData(volumeData);

      // Fit content
      chartRef.current.timeScale().fitContent();
      
      // Update position markers
      updatePositionMarkers();
    };

    loadData();
  }, [selectedInstrument, timeframe, chartLoaded, positions]);

  // Update position markers on chart
  const updatePositionMarkers = () => {
    if (!candleSeriesRef.current) return;

    // Clear existing markers
    positionMarkersRef.current.forEach(marker => {
      // Note: lightweight-charts doesn't have a direct remove marker API
      // Markers are set as a complete array each time
    });

    // Create new markers for positions
    const markers = positions.map(pos => ({
      time: pos.entryTime,
      position: pos.side === 'buy' ? 'belowBar' : 'aboveBar',
      color: pos.side === 'buy' ? '#26a69a' : '#ef5350',
      shape: pos.side === 'buy' ? 'arrowUp' : 'arrowDown',
      text: `${pos.side.toUpperCase()} ${pos.size} @ ${pos.entryPrice}`,
    }));

    candleSeriesRef.current.setMarkers(markers);
  };

  // One-click buy/sell from chart
  const handleQuickTrade = async (side) => {
    if (!crosshairPrice) return;

    try {
      const orderData = {
        symbol: selectedInstrument,
        side: side,
        type: 'market',
        size: Number.parseFloat(orderSize),
        price: crosshairPrice
      };

      const response = await axios.post(apiUrl('/api/trading/orders'), orderData);
      console.log('Order placed:', response.data);
      
      // Reload positions
      await loadPositions();
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order: ' + (error.response?.data?.message || error.message));
    }
  };

  // Close position
  const handleClosePosition = async (positionId) => {
    try {
      await axios.delete(apiUrl(`/api/trading/positions/${positionId}`));
      console.log('Position closed:', positionId);
      
      // Reload positions
      await loadPositions();
    } catch (error) {
      console.error('Error closing position:', error);
      alert('Failed to close position: ' + (error.response?.data?.message || error.message));
    }
  };

  // Reverse position (close and open opposite)
  const handleReversePosition = async (positionId) => {
    try {
      const response = await axios.post(apiUrl(`/api/trading/positions/${positionId}/reverse`));
      console.log('Position reversed:', response.data);
      
      // Reload positions
      await loadPositions();
    } catch (error) {
      console.error('Error reversing position:', error);
      alert('Failed to reverse position: ' + (error.response?.data?.message || error.message));
    }
  };

  // Place order at specific price level
  const handlePlaceOrder = async () => {
    const price = orderType === 'market' ? crosshairPrice : Number.parseFloat(orderPrice);
    
    if (!price && orderType !== 'market') {
      alert('Please enter a price');
      return;
    }

    try {
      const orderData = {
        symbol: selectedInstrument,
        side: orderSide,
        type: orderType,
        size: Number.parseFloat(orderSize),
        price: price
      };

      const response = await axios.post(apiUrl('/api/trading/orders'), orderData);
      console.log('Order placed:', response.data);
      
      setShowOrderPanel(false);
      
      // Reload positions
      await loadPositions();
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order: ' + (error.response?.data?.message || error.message));
    }
  };

  const currentInstrument = instruments.find(inst => inst.symbol === selectedInstrument || inst.id === selectedInstrument);

  if (loading) {
    return (
      <div className="advanced-trading-chart">
        <div className="loading-message">Loading chart data...</div>
      </div>
    );
  }

  return (
    <div className="advanced-trading-chart">
      {/* Header Controls */}
      <div className="chart-header">
        <div className="header-left">
          <div className="instrument-selector">
            <select 
              value={selectedInstrument} 
              onChange={(e) => setSelectedInstrument(e.target.value)}
              className="instrument-select"
              disabled={instruments.length === 0}
            >
              {instruments.length === 0 ? (
                <option value="">No instruments available</option>
              ) : (
                instruments.map(inst => (
                  <option key={inst.id || inst.symbol} value={inst.symbol || inst.id}>
                    {inst.symbol} {inst.name ? `- ${inst.name}` : ''}
                  </option>
                ))
              )}
            </select>
          </div>

          <div className="timeframe-selector">
            {['1m', '5m', '15m', '30m', '1h', '4h', '1d'].map(tf => (
              <button
                key={tf}
                className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div className="header-right">
          <div className="current-price">
            {crosshairPrice ? crosshairPrice.toFixed(5) : '---'}
          </div>
          
          <button 
            className="quick-buy-btn"
            onClick={() => handleQuickTrade('buy')}
            disabled={!crosshairPrice}
          >
            🚀 Quick BUY
          </button>
          
          <button 
            className="quick-sell-btn"
            onClick={() => handleQuickTrade('sell')}
            disabled={!crosshairPrice}
          >
            📉 Quick SELL
          </button>

          <button 
            className="order-panel-btn"
            onClick={() => setShowOrderPanel(!showOrderPanel)}
          >
            📊 Advanced Order
          </button>
        </div>
      </div>

      {/* Advanced Order Panel */}
      {showOrderPanel && (
        <div className="order-panel">
          <div className="order-panel-content">
            <h3>Place Order</h3>
            
            <div className="order-controls">
              <div className="order-control-group">
                <label>Order Type</label>
                <select 
                  value={orderType} 
                  onChange={(e) => setOrderType(e.target.value)}
                  className="order-select"
                >
                  <option value="market">Market Order</option>
                  <option value="limit">Limit Order</option>
                  <option value="stop">Stop Order</option>
                </select>
              </div>

              <div className="order-control-group">
                <label>Side</label>
                <div className="side-buttons">
                  <button
                    className={`side-btn buy ${orderSide === 'buy' ? 'active' : ''}`}
                    onClick={() => setOrderSide('buy')}
                  >
                    BUY
                  </button>
                  <button
                    className={`side-btn sell ${orderSide === 'sell' ? 'active' : ''}`}
                    onClick={() => setOrderSide('sell')}
                  >
                    SELL
                  </button>
                </div>
              </div>

              <div className="order-control-group">
                <label>Size (Lots)</label>
                <input
                  type="number"
                  value={orderSize}
                  onChange={(e) => setOrderSize(e.target.value)}
                  min={currentInstrument?.minLot}
                  max={currentInstrument?.maxLot}
                  step={currentInstrument?.minLot}
                  className="order-input"
                />
              </div>

              {orderType !== 'market' && (
                <div className="order-control-group">
                  <label>Price</label>
                  <input
                    type="number"
                    value={orderPrice || ''}
                    onChange={(e) => setOrderPrice(e.target.value)}
                    placeholder="Enter price"
                    step={currentInstrument?.pipSize}
                    className="order-input"
                  />
                </div>
              )}

              <button className="place-order-btn" onClick={handlePlaceOrder}>
                Place {orderSide.toUpperCase()} Order
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chart Container */}
      <div className="chart-container" ref={chartContainerRef} />

      {/* Open Positions Panel */}
      {positions.length > 0 && (
        <div className="positions-panel">
          <h3>Open Positions</h3>
          <div className="positions-list">
            {positions.map(pos => (
              <div key={pos.id} className={`position-card ${pos.side || pos.type}`}>
                <div className="position-info">
                  <span className="position-instrument">{pos.symbol || pos.instrument}</span>
                  <span className={`position-side ${pos.side || pos.type}`}>
                    {(pos.side || pos.type || '').toUpperCase()}
                  </span>
                  <span className="position-size">{pos.quantity || pos.size} {pos.units || 'lots'}</span>
                  <span className="position-price">@ {(pos.entry_price || pos.entryPrice || pos.price || 0).toFixed(5)}</span>
                  {pos.pnl !== undefined && (
                    <span className={`position-pnl ${pos.pnl >= 0 ? 'positive' : 'negative'}`}>
                      {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
                    </span>
                  )}
                </div>
                
                <div className="position-actions">
                  <button
                    className="btn-close-position"
                    onClick={() => handleClosePosition(pos.id)}
                    title="Close Position"
                  >
                    ❌ Close
                  </button>
                  <button
                    className="btn-reverse-position"
                    onClick={() => handleReversePosition(pos.id)}
                    title="Reverse Position"
                  >
                    🔄 Reverse
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chart Instructions */}
      <div className="chart-instructions">
        <p>
          💡 <strong>Quick Trading:</strong> Hover over the chart to see price, 
          then click Quick BUY/SELL buttons for instant orders at that price level.
        </p>
        <p>
          📊 <strong>Advanced Orders:</strong> Use the Advanced Order panel for limit and stop orders.
        </p>
        <p>
          🔄 <strong>Manage Positions:</strong> Close or reverse your positions with one click from the positions panel.
        </p>
      </div>
    </div>
  );
};

export default AdvancedTradingChart;
