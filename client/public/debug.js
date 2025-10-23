// Debug helper - paste this in browser console (F12) to check API connectivity

console.log('=== RAG Trading Assistant Debug ===')

// Check environment
console.log('Environment:', import.meta?.env?.DEV ? 'Development' : 'Production')

// Check API base URL
const apiBase = localStorage.getItem('apiBaseUrl') || 'default (localhost:5000)'
console.log('Configured API Base:', apiBase)

// Test API endpoint
console.log('\nTesting API endpoint...')
fetch('/api/metrics')
  .then(res => {
    console.log('Status:', res.status, res.statusText)
    return res.json()
  })
  .then(data => {
    console.log('✅ API Response:', data)
    console.log('\nData breakdown:')
    console.log('- Today trades:', data.today?.count || 0)
    console.log('- Today PNL:', data.today?.pnl || 0)
    console.log('- Week data points:', data.week?.values?.length || 0)
    console.log('- Month data points:', data.month?.values?.length || 0)
  })
  .catch(err => {
    console.error('❌ API Error:', err)
    console.log('\nTroubleshooting:')
    console.log('1. Check Flask is running: http://localhost:5000')
    console.log('2. Check Vite proxy config in vite.config.js')
    console.log('3. Look for CORS errors above')
    console.log('4. Verify network request in Network tab')
  })

console.log('\n=== End Debug ===')
