import React, {useEffect, useState} from 'react'
import axios from 'axios'
import { apiUrl } from '../../../services/api'
import './Dashboard.css'

export default function Dashboard(){
  const [stats, setStats] = useState({
    totalTrades: 0,
    openPositions: 0,
    closedTrades: 0,
    totalPnL: 0,
    instruments: 0,
    activeInstruments: 0,
    tradingEnabled: false,
    totalFund: 0
  })
  const [recentTrades, setRecentTrades] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => { fetchDashboardData() }, [])
  
  async function fetchDashboardData(){
    try {
      setLoading(true)
      setError(null)
      
      // Fetch all data in parallel using proper API URLs
      const [tradesRes, positionsRes, instrumentsRes, settingsRes] = await Promise.all([
        axios.get(apiUrl('/api/trading/trades?limit=10')),
        axios.get(apiUrl('/api/trading/positions')),
        axios.get(apiUrl('/api/trading/instruments')),
        axios.get(apiUrl('/api/trading/settings'))
      ])
      
      const trades = tradesRes.data.trades || []
      const positions = positionsRes.data.positions || []
      const instruments = instrumentsRes.data.instruments || []
      const settings = settingsRes.data.settings || {}
      
      // Calculate stats
      const closedTrades = trades.filter(t => t.status === 'CLOSED')
      const totalPnL = closedTrades.reduce((sum, t) => sum + (parseFloat(t.profit_loss) || 0), 0)
      const activeInstruments = instruments.filter(i => i.enabled).length
      
      // Settings is a dictionary with keys like: {trading_enabled: {value, type, description}}
      const tradingEnabled = settings.trading_enabled?.value || false
      const totalFund = settings.total_fund?.value || 0
      
      setStats({
        totalTrades: trades.length,
        openPositions: positions.length,
        closedTrades: closedTrades.length,
        totalPnL,
        instruments: instruments.length,
        activeInstruments,
        tradingEnabled,
        totalFund
      })
      
      setRecentTrades(trades.slice(0, 5))
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }
  
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  if(loading) return <div className="dashboard-loading">Loading dashboard...</div>
  if(error) return (
    <div className="dashboard-error">
      <h4>❌ Error loading dashboard</h4>
      <p>{error}</p>
      <button onClick={fetchDashboardData}>Retry</button>
    </div>
  )
  
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>📊 Trading Dashboard</h1>
        <div className={`system-status-badge ${stats.tradingEnabled ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          {stats.tradingEnabled ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-label">Total Trades</div>
            <div className="stat-value">{stats.totalTrades}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🟢</div>
          <div className="stat-content">
            <div className="stat-label">Open Positions</div>
            <div className="stat-value">{stats.openPositions}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔴</div>
          <div className="stat-content">
            <div className="stat-label">Closed Trades</div>
            <div className="stat-value">{stats.closedTrades}</div>
          </div>
        </div>
        
        <div className={`stat-card ${stats.totalPnL >= 0 ? 'profit' : 'loss'}`}>
          <div className="stat-icon">{stats.totalPnL >= 0 ? '💰' : '⚠️'}</div>
          <div className="stat-content">
            <div className="stat-label">Total P&L</div>
            <div className="stat-value">{formatCurrency(stats.totalPnL)}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-label">Instruments</div>
            <div className="stat-value">{stats.activeInstruments}/{stats.instruments}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💵</div>
          <div className="stat-content">
            <div className="stat-label">Total Fund</div>
            <div className="stat-value">{formatCurrency(stats.totalFund)}</div>
          </div>
        </div>
      </div>
      
      {/* Recent Trades */}
      <div className="recent-trades-section">
        <h2>🕒 Recent Trades</h2>
        {recentTrades.length === 0 ? (
          <div className="no-trades-message">
            <p>No trades yet. Start trading to see activity here.</p>
          </div>
        ) : (
          <div className="trades-list">
            {recentTrades.map(trade => (
              <div key={trade.id} className={`trade-item ${trade.status.toLowerCase()}`}>
                <div className="trade-main">
                  <span className="trade-symbol">{trade.symbol}</span>
                  <span className={`trade-action ${trade.action.toLowerCase()}`}>
                    {trade.action === 'BUY' ? '📈' : '📉'} {trade.action}
                  </span>
                  <span className={`trade-status ${trade.status.toLowerCase()}`}>
                    {trade.status}
                  </span>
                </div>
                <div className="trade-details">
                  <span>Open: {formatCurrency(trade.open_price)}</span>
                  {trade.close_price && <span>Close: {formatCurrency(trade.close_price)}</span>}
                  {trade.profit_loss && (
                    <span className={trade.profit_loss >= 0 ? 'profit' : 'loss'}>
                      P&L: {formatCurrency(trade.profit_loss)}
                    </span>
                  )}
                  <span className="trade-time">{formatDateTime(trade.open_time)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>⚡ Quick Actions</h2>
        <div className="actions-grid">
          <button className="action-btn" onClick={() => window.location.href = '#positions'}>
            📍 View Positions
          </button>
          <button className="action-btn" onClick={() => window.location.href = '#trades'}>
            📊 Trade History
          </button>
          <button className="action-btn" onClick={() => window.location.href = '#instruments'}>
            🎯 Manage Instruments
          </button>
          <button className="action-btn" onClick={() => window.location.href = '#control'}>
            ⚙️ System Control
          </button>
        </div>
      </div>
      
      {/* Refresh Button */}
      <button className="refresh-dashboard-btn" onClick={fetchDashboardData}>
        🔄 Refresh Dashboard
      </button>
    </div>
  )
}
