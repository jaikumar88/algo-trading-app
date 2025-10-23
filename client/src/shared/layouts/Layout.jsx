import React from 'react'
import './Layout.css'

export default function Layout({children, onNavigate, current, theme, onThemeChange}){
  return (
    <div style={{minHeight:'100vh'}}>
      <header className="main-header">
        <div className="header-left">
          <h3 className="app-title">📊 RAG Trading System</h3>
          <nav className="main-nav">
            <button onClick={()=>onNavigate('dashboard')} className={current==='dashboard'?'nav-btn active':'nav-btn'}>
              📈 Dashboard
            </button>
            <button onClick={()=>onNavigate('signals')} className={current==='signals'?'nav-btn active':'nav-btn'}>
              📡 Signals
            </button>
            <button onClick={()=>onNavigate('trades')} className={current==='trades'?'nav-btn active':'nav-btn'}>
              📊 Trade History
            </button>
            <button onClick={()=>onNavigate('positions')} className={current==='positions'?'nav-btn active':'nav-btn'}>
              📍 Positions
            </button>
            <button onClick={()=>onNavigate('risk')} className={current==='risk'?'nav-btn active':'nav-btn'}>
              🛡️ Risk
            </button>
            <button onClick={()=>onNavigate('chart')} className={current==='chart'?'nav-btn active':'nav-btn'}>
              📉 Chart
            </button>
            <button onClick={()=>onNavigate('tradingview')} className={current==='tradingview'?'nav-btn active':'nav-btn'}>
              📊 TradingView
            </button>
            <button onClick={()=>onNavigate('historical')} className={current==='historical'?'nav-btn active':'nav-btn'}>
              📦 Historical
            </button>
            <button onClick={()=>onNavigate('multicharts')} className={current==='multicharts'?'nav-btn active':'nav-btn'}>
              📊 All Symbols
            </button>
            <button onClick={()=>onNavigate('instruments')} className={current==='instruments'?'nav-btn active':'nav-btn'}>
              🎯 Instruments
            </button>
            <button onClick={()=>onNavigate('control')} className={current==='control'?'nav-btn active':'nav-btn'}>
              ⚙️ Control
            </button>
            <button onClick={()=>onNavigate('settings')} className={current==='settings'?'nav-btn active':'nav-btn'}>
              🔧 Settings
            </button>
          </nav>
        </div>
        <div className="header-right">
          <button className="theme-toggle-btn" onClick={()=>onThemeChange(theme === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}
