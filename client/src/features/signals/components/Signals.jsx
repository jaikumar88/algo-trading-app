import React, {useEffect, useState} from 'react'
import axios from 'axios'
import SignalDetails from '../../../components/SignalDetails'
import {apiUrl} from '../../../services/api'
import './Signals.css'

export default function Signals(){
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  
  // Filter state
  const [filters, setFilters] = useState({
    symbol: '',
    action: '',
    startDate: '',
    endDate: ''
  })
  
  // Stats state
  const [stats, setStats] = useState({
    total: 0,
    buy: 0,
    sell: 0
  })

  useEffect(()=>{ load() }, [])
  
  async function load(){
    setLoading(true)
    try {
      const res = await axios.get(apiUrl('/api/trading/signals'))
      setSignals(res.data.signals || [])
      calculateStats(res.data.signals || [])
    } catch (error) {
      console.error('Error loading signals:', error)
      setSignals([])
    }
    setLoading(false)
  }
  
  function calculateStats(signalList) {
    setStats({
      total: signalList.length,
      buy: signalList.filter(s => s.action?.toLowerCase() === 'buy').length,
      sell: signalList.filter(s => s.action?.toLowerCase() === 'sell').length
    })
  }
  
  // Filter signals based on current filters
  const filteredSignals = signals.filter(signal => {
    // Symbol filter
    if (filters.symbol && !signal.symbol?.toLowerCase().includes(filters.symbol.toLowerCase())) {
      return false
    }
    
    // Action filter
    if (filters.action && signal.action?.toLowerCase() !== filters.action.toLowerCase()) {
      return false
    }
    
    // Date range filter
    if (filters.startDate) {
      const signalDate = new Date(signal.created_at)
      const startDate = new Date(filters.startDate)
      if (signalDate < startDate) return false
    }
    
    if (filters.endDate) {
      const signalDate = new Date(signal.created_at)
      const endDate = new Date(filters.endDate)
      endDate.setHours(23, 59, 59, 999) // End of day
      if (signalDate > endDate) return false
    }
    
    return true
  })
  
  // Calculate pagination
  const totalPages = Math.ceil(filteredSignals.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentSignals = filteredSignals.slice(startIndex, endIndex)
  
  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters, itemsPerPage])
  
  function handleFilterChange(field, value) {
    setFilters(prev => ({ ...prev, [field]: value }))
  }
  
  function clearFilters() {
    setFilters({
      symbol: '',
      action: '',
      startDate: '',
      endDate: ''
    })
  }
  
  function formatDate(dateString) {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }
  
  function getActionBadgeClass(action) {
    if (!action) return 'badge-neutral'
    const actionLower = action.toLowerCase()
    if (actionLower === 'buy') return 'badge-success'
    if (actionLower === 'sell') return 'badge-danger'
    return 'badge-neutral'
  }
  
  return (
    <div className="signals-container">
      {/* Header with Stats */}
      <div className="signals-header">
        <div className="header-title">
          <h2>📊 Trading Signals</h2>
          <p className="subtitle">Monitor and analyze your trading signals</p>
        </div>
        
        <div className="stats-cards">
          <div className="stat-card stat-total">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Signals</div>
            </div>
          </div>
          
          <div className="stat-card stat-buy">
            <div className="stat-icon">🟢</div>
            <div className="stat-content">
              <div className="stat-value">{stats.buy}</div>
              <div className="stat-label">Buy Signals</div>
            </div>
          </div>
          
          <div className="stat-card stat-sell">
            <div className="stat-icon">🔴</div>
            <div className="stat-content">
              <div className="stat-value">{stats.sell}</div>
              <div className="stat-label">Sell Signals</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Filters Section */}
      <div className="filters-section">
        <div className="filters-header">
          <h3>🔍 Filters</h3>
          <button className="btn-clear" onClick={clearFilters}>
            Clear All
          </button>
        </div>
        
        <div className="filters-grid">
          <div className="filter-group">
            <label>Symbol</label>
            <input
              type="text"
              placeholder="e.g. BTCUSDT"
              value={filters.symbol}
              onChange={(e) => handleFilterChange('symbol', e.target.value)}
              className="filter-input"
            />
          </div>
          
          <div className="filter-group">
            <label>Action</label>
            <select
              value={filters.action}
              onChange={(e) => handleFilterChange('action', e.target.value)}
              className="filter-select"
            >
              <option value="">All Actions</option>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Start Date</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange('startDate', e.target.value)}
              className="filter-input"
            />
          </div>
          
          <div className="filter-group">
            <label>End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleFilterChange('endDate', e.target.value)}
              className="filter-input"
            />
          </div>
        </div>
        
        <div className="filter-results">
          Showing <strong>{currentSignals.length}</strong> of <strong>{filteredSignals.length}</strong> signals
          {filteredSignals.length < signals.length && (
            <span className="filter-badge">{signals.length - filteredSignals.length} filtered out</span>
          )}
        </div>
      </div>
      
      {/* Signals Table */}
      <div className="signals-table-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading signals...</p>
          </div>
        ) : currentSignals.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No signals found</h3>
            <p>
              {filteredSignals.length === 0 && signals.length > 0
                ? 'Try adjusting your filters'
                : 'No signals have been recorded yet'}
            </p>
          </div>
        ) : (
          <>
            <table className="signals-table">
              <thead>
                <tr>
                  <th className="th-id">ID</th>
                  <th className="th-symbol">Symbol</th>
                  <th className="th-action">Action</th>
                  <th className="th-price">Price</th>
                  <th className="th-source">Source</th>
                  <th className="th-time">Time</th>
                  <th className="th-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentSignals.map(signal => (
                  <tr key={signal.id} className="signal-row">
                    <td className="td-id">#{signal.id}</td>
                    <td className="td-symbol">
                      <span className="symbol-badge">{signal.symbol || 'N/A'}</span>
                    </td>
                    <td className="td-action">
                      <span className={`action-badge ${getActionBadgeClass(signal.action)}`}>
                        {signal.action || 'N/A'}
                      </span>
                    </td>
                    <td className="td-price">
                      {signal.price ? `$${parseFloat(signal.price).toLocaleString()}` : '-'}
                    </td>
                    <td className="td-source">
                      <span className="source-badge">{signal.source || 'Unknown'}</span>
                    </td>
                    <td className="td-time">{formatDate(signal.created_at)}</td>
                    <td className="td-actions">
                      <button
                        className="btn-view"
                        onClick={() => setSelected(signal)}
                        title="View Details"
                      >
                        👁️ View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* Pagination Controls */}
            <div className="pagination-container">
              <div className="pagination-info">
                Showing {startIndex + 1} - {Math.min(endIndex, filteredSignals.length)} of {filteredSignals.length}
              </div>
              
              <div className="pagination-controls">
                <button
                  className="btn-page"
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                >
                  ⏮️ First
                </button>
                
                <button
                  className="btn-page"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  ◀️ Prev
                </button>
                
                <div className="page-numbers">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum
                    if (totalPages <= 5) {
                      pageNum = i + 1
                    } else if (currentPage <= 3) {
                      pageNum = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i
                    } else {
                      pageNum = currentPage - 2 + i
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        className={`btn-page-num ${currentPage === pageNum ? 'active' : ''}`}
                        onClick={() => setCurrentPage(pageNum)}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>
                
                <button
                  className="btn-page"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next ▶️
                </button>
                
                <button
                  className="btn-page"
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                >
                  Last ⏭️
                </button>
              </div>
              
              <div className="items-per-page">
                <label>Items per page:</label>
                <select
                  value={itemsPerPage}
                  onChange={(e) => setItemsPerPage(Number(e.target.value))}
                  className="select-items"
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
          </>
        )}
      </div>
      
      <SignalDetails signal={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
