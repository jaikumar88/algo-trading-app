import { useState, useEffect } from 'react';
import axios from 'axios';
import './Positions.css';

const Positions = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [closingTrade, setClosingTrade] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchPositions();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchPositions, 5000); // Refresh every 5 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchPositions = async () => {
    try {
      const response = await axios.get('/api/trading/positions');
      setPositions(response.data.positions || []);
      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('Error fetching positions:', err);
      setError(err.response?.data?.error || 'Failed to fetch positions');
      setLoading(false);
    }
  };

  const closePosition = async (tradeId, symbol, currentPrice) => {
    // Prompt user for close price
    const priceInput = prompt(
      `Enter the close price for ${symbol}:`,
      currentPrice || ''
    );
    
    if (!priceInput) {
      return; // User cancelled
    }

    const closePrice = parseFloat(priceInput);
    if (isNaN(closePrice) || closePrice <= 0) {
      alert('Invalid price. Please enter a valid number.');
      return;
    }

    if (!confirm(`Close ${symbol} position at $${closePrice}?`)) {
      return;
    }

    setClosingTrade(tradeId);
    try {
      await axios.post(
        `/api/trading/trades/${tradeId}/close`,
        { close_price: closePrice },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      await fetchPositions(); // Refresh positions
      alert('Position closed successfully!');
    } catch (err) {
      console.error('Error closing position:', err);
      alert(err.response?.data?.error || 'Failed to close position');
    } finally {
      setClosingTrade(null);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateUnrealizedPnL = (trade) => {
    // This is a placeholder - in real app, you'd fetch current market price
    // For now, we'll show the allocated fund
    if (trade.allocated_fund) {
      return trade.allocated_fund;
    }
    return 0;
  };

  const calculateDuration = (openTime) => {
    const now = new Date();
    const opened = new Date(openTime);
    const diff = now - opened;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
  };

  const totalExposure = positions.reduce((sum, p) => 
    sum + (parseFloat(p.total_cost) || 0), 0);

  const totalAllocated = positions.reduce((sum, p) => 
    sum + (parseFloat(p.allocated_fund) || 0), 0);

  return (
    <div className="positions-container">
      <div className="positions-header">
        <h1>📍 Current Positions</h1>
        <div className="header-controls">
          <label className="auto-refresh-toggle">
            <input 
              type="checkbox" 
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span>Auto-refresh (5s)</span>
          </label>
          <button className="refresh-btn" onClick={fetchPositions}>
            🔄 Refresh Now
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <div className="summary-label">Open Positions</div>
            <div className="summary-value">{positions.length}</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">💰</div>
          <div className="summary-content">
            <div className="summary-label">Total Exposure</div>
            <div className="summary-value">{formatCurrency(totalExposure)}</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">🎯</div>
          <div className="summary-content">
            <div className="summary-label">Allocated Funds</div>
            <div className="summary-value">{formatCurrency(totalAllocated)}</div>
          </div>
        </div>
      </div>

      {/* Positions Grid */}
      {loading ? (
        <div className="loading">Loading positions...</div>
      ) : error ? (
        <div className="error-message">
          ❌ {error}
          <button onClick={fetchPositions}>Retry</button>
        </div>
      ) : positions.length === 0 ? (
        <div className="no-positions">
          <div className="no-positions-icon">📭</div>
          <h3>No Open Positions</h3>
          <p>All positions are currently closed. New positions will appear here when trades are executed.</p>
        </div>
      ) : (
        <div className="positions-grid">
          {positions.map(position => (
            <div key={position.id} className="position-card">
              <div className="position-header">
                <div className="position-symbol">
                  <span className="symbol-text">{position.symbol}</span>
                  <span className={`action-indicator ${position.action.toLowerCase()}`}>
                    {position.action === 'BUY' ? '📈 LONG' : '📉 SHORT'}
                  </span>
                </div>
                <div className="position-id">ID: {position.id}</div>
              </div>

              <div className="position-details">
                <div className="detail-row">
                  <span className="detail-label">Quantity:</span>
                  <span className="detail-value">{parseFloat(position.quantity).toFixed(8)}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Entry Price:</span>
                  <span className="detail-value">{formatCurrency(position.open_price)}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Total Cost:</span>
                  <span className="detail-value">{formatCurrency(position.total_cost)}</span>
                </div>
                {position.allocated_fund && (
                  <div className="detail-row">
                    <span className="detail-label">Allocated:</span>
                    <span className="detail-value">{formatCurrency(position.allocated_fund)}</span>
                  </div>
                )}
                {position.risk_amount && (
                  <div className="detail-row">
                    <span className="detail-label">Risk (2%):</span>
                    <span className="detail-value risk">{formatCurrency(position.risk_amount)}</span>
                  </div>
                )}
              </div>

              <div className="position-meta">
                <div className="meta-item">
                  <span className="meta-icon">🕐</span>
                  <span className="meta-text">
                    Opened: {formatDateTime(position.open_time)}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">⏱️</span>
                  <span className="meta-text">
                    Duration: {calculateDuration(position.open_time)}
                  </span>
                </div>
              </div>

              <button 
                className="close-btn"
                onClick={() => closePosition(position.id, position.symbol, position.open_price)}
                disabled={closingTrade === position.id}
              >
                {closingTrade === position.id ? (
                  <>⏳ Closing...</>
                ) : (
                  <>🔒 Close Position</>
                )}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Risk Warning */}
      {positions.length > 0 && (
        <div className="risk-warning">
          <div className="warning-icon">⚠️</div>
          <div className="warning-content">
            <strong>Risk Management:</strong> Each position is limited to 2% risk of allocated funds. 
            Monitor your positions regularly and close them manually when needed.
          </div>
        </div>
      )}
    </div>
  );
};

export default Positions;
