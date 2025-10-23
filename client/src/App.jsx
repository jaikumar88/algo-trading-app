import React from 'react'
import Layout from './shared/layouts/Layout'
import Dashboard from './features/dashboard/components/Dashboard'
import Signals from './features/signals/components/Signals'
import Settings from './features/settings/components/Settings'
import TradeHistory from './features/trading/components/TradeHistory'
import Positions from './features/trading/components/Positions'
import AdminInstruments from './features/trading/components/AdminInstruments'
import SystemControl from './features/trading/components/SystemControl'
import RiskManagement from './features/risk/components/RiskManagement'
import TradingViewAdvanced from './features/charts/components/TradingViewAdvanced'
import HistoricalChart from './features/charts/components/HistoricalChart'
import MultiSymbolCharts from './features/charts/components/MultiSymbolCharts'
import AdvancedTradingChart from './components/AdvancedTradingChart'

export default function App(){
  const [route, setRoute] = React.useState('dashboard')
  const [theme, setTheme] = React.useState(() => {
    return localStorage.getItem('theme') || 'light'
  })

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    if (newTheme === 'dark') {
      document.documentElement.classList.add('theme-dark')
    } else {
      document.documentElement.classList.remove('theme-dark')
    }
  }

  // Set initial theme on mount
  React.useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('theme-dark')
    }
  }, [])

  const renderRoute = () => {
    if (route === 'dashboard') return <Dashboard />
    if (route === 'signals') return <Signals />
    if (route === 'trades') return <TradeHistory />
    if (route === 'positions') return <Positions />
    if (route === 'risk') return <RiskManagement />
    if (route === 'chart') return <AdvancedTradingChart />
    if (route === 'tradingview') return <TradingViewAdvanced />
    if (route === 'historical') return <HistoricalChart />
    if (route === 'multicharts') return <MultiSymbolCharts />
    if (route === 'instruments') return <AdminInstruments />
    if (route === 'control') return <SystemControl />
    if (route === 'settings') return <Settings theme={theme} onThemeChange={handleThemeChange} />
    return <Dashboard />
  }

  return (
    <Layout onNavigate={setRoute} current={route} theme={theme} onThemeChange={handleThemeChange}>
      {renderRoute()}
    </Layout>
  )
}
