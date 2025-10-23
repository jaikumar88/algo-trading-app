import { useState, useEffect } from 'react';
import axios from 'axios';
import './TradeHistory.css';

const TradeHistory = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    symbol: 'all',
    page: 1,
    limit: 50
  });
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    closed: 0,
    totalPnL: 0
  });

  useEffect(() => {
    fetchTrades();
  }, [filters]);

  const fetchTrades = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page: filters.page,
        limit: filters.limit
      };
      
      if (filters.status !== 'all') {
        params.status = filters.status;
      }
      
      if (filters.symbol !== 'all') {
        params.symbol = filters.symbol;
      }

      const response = await axios.get('/api/trading/trades', { params });
      setTrades(response.data.trades || []);
      
      // Calculate stats
      const allTrades = response.data.trades || [];
      const openTrades = allTrades.filter(t => t.status === 'OPEN');
      const closedTrades = allTrades.filter(t => t.status === 'CLOSED');
      const totalPnL = closedTrades.reduce((sum, t) => sum + (parseFloat(t.profit_loss) || 0), 0);
      
      setStats({
        total: allTrades.length,
        open: openTrades.length,
        closed: closedTrades.length,
        totalPnL
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching trades:', err);
      setError(err.response?.data?.error || 'Failed to fetch trades');
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }));
  };

  const exportToCSV = () => {
    if (trades.length === 0) return;

    const headers = ['ID', 'Symbol', 'Action', 'Quantity', 'Open Price', 'Close Price', 'Status', 'P&L', 'Open Time', 'Close Time'];
    const rows = trades.map(trade => [
      trade.id,
      trade.symbol,
      trade.action,
      trade.quantity,
      trade.open_price,
      trade.close_price || 'N/A',
      trade.status,
      trade.profit_loss || 'N/A',
      new Date(trade.open_time).toLocaleString(),
      trade.close_time ? new Date(trade.close_time).toLocaleString() : 'N/A'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trade-history-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const deleteTrade = async (tradeId, symbol) => {
    if (!confirm(`Are you sure you want to delete trade #${tradeId} (${symbol})? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`/api/trading/trades/${tradeId}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      alert('Trade deleted successfully!');
      fetchTrades(); // Refresh the list
    } catch (err) {
      console.error('Error deleting trade:', err);
      alert(err.response?.data?.error || 'Failed to delete trade');
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
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get unique symbols for filter
  const uniqueSymbols = [...new Set(trades.map(t => t.symbol))];

  return (
    <div className="trade-history-container">
      <div className="trade-history-header">
        <h1>📊 Trade History</h1>
        <button className="export-btn" onClick={exportToCSV} disabled={trades.length === 0}>
          📥 Export CSV
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-label">Total Trades</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🟢</div>
          <div className="stat-content">
            <div className="stat-label">Open Positions</div>
            <div className="stat-value">{stats.open}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔴</div>
          <div className="stat-content">
            <div className="stat-label">Closed Trades</div>
            <div className="stat-value">{stats.closed}</div>
          </div>
        </div>
        <div className={`stat-card ${stats.totalPnL >= 0 ? 'profit' : 'loss'}`}>
          <div className="stat-icon">{stats.totalPnL >= 0 ? '💰' : '⚠️'}</div>
          <div className="stat-content">
            <div className="stat-label">Total P&L</div>
            <div className="stat-value">{formatCurrency(stats.totalPnL)}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-container">
        <div className="filter-group">
          <label>Status:</label>
          <select 
            value={filters.status} 
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="all">All</option>
            <option value="OPEN">Open</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Symbol:</label>
          <select 
            value={filters.symbol} 
            onChange={(e) => handleFilterChange('symbol', e.target.value)}
          >
            <option value="all">All Symbols</option>
            {uniqueSymbols.map(symbol => (
              <option key={symbol} value={symbol}>{symbol}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Per Page:</label>
          <select 
            value={filters.limit} 
            onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
          >
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="200">200</option>
          </select>
        </div>

        <button className="refresh-btn" onClick={fetchTrades}>
          🔄 Refresh
        </button>
      </div>

      {/* Trades Table */}
      {loading ? (
        <div className="loading">Loading trades...</div>
      ) : error ? (
        <div className="error-message">
          ❌ {error}
          <button onClick={fetchTrades}>Retry</button>
        </div>
      ) : trades.length === 0 ? (
        <div className="no-data">No trades found</div>
      ) : (
        <div className="table-container">
          <table className="trades-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Symbol</th>
                <th>Action</th>
                <th>Quantity</th>
                <th>Open Price</th>
                <th>Close Price</th>
                <th>Status</th>
                <th>P&L</th>
                <th>Open Time</th>
                <th>Close Time</th>
                <th>Closed By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {trades.map(trade => (
                <tr key={trade.id} className={trade.status === 'OPEN' ? 'open-trade' : 'closed-trade'}>
                  <td>{trade.id}</td>
                  <td className="symbol-cell">
                    <span className="symbol-badge">{trade.symbol}</span>
                  </td>
                  <td>
                    <span className={`action-badge ${trade.action.toLowerCase()}`}>
                      {trade.action === 'BUY' ? '📈' : '📉'} {trade.action}
                    </span>
                  </td>
                  <td>{parseFloat(trade.quantity).toFixed(8)}</td>
                  <td>{formatCurrency(trade.open_price)}</td>
                  <td>{trade.close_price ? formatCurrency(trade.close_price) : '-'}</td>
                  <td>
                    <span className={`status-badge ${trade.status.toLowerCase()}`}>
                      {trade.status}
                    </span>
                  </td>
                  <td className={trade.profit_loss ? (trade.profit_loss >= 0 ? 'profit-cell' : 'loss-cell') : ''}>
                    {trade.profit_loss ? formatCurrency(trade.profit_loss) : '-'}
                  </td>
                  <td>{formatDateTime(trade.open_time)}</td>
                  <td>{formatDateTime(trade.close_time)}</td>
                  <td>
                    {trade.closed_by_user ? (
                      <span className="manual-badge">👤 Manual</span>
                    ) : trade.status === 'CLOSED' ? (
                      <span className="auto-badge">🤖 Auto</span>
                    ) : '-'}
                  </td>
                  <td>
                    <button 
                      className="delete-trade-btn"
                      onClick={() => deleteTrade(trade.id, trade.symbol)}
                      title="Delete this trade"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {trades.length > 0 && (
        <div className="pagination">
          <button 
            onClick={() => handleFilterChange('page', filters.page - 1)}
            disabled={filters.page === 1}
          >
            ← Previous
          </button>
          <span className="page-info">Page {filters.page}</span>
          <button 
            onClick={() => handleFilterChange('page', filters.page + 1)}
            disabled={trades.length < filters.limit}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default TradeHistory;
