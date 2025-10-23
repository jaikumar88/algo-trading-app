import React, {useEffect, useState} from 'react'
import axios from 'axios'
import SignalDetails from './SignalDetails'
import {apiUrl} from '../api'

export default function Signals(){
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)
  useEffect(()=>{ load() }, [])
  async function load(){
    setLoading(true)
    const res = await axios.get(apiUrl('/api/trading/signals'))
    setSignals(res.data.signals || res.data)
    setLoading(false)
  }
  return (
    <div>
      <h4>Signals</h4>
      {loading ? <div>Loading...</div> : (
        <table style={{width:'100%',borderCollapse:'collapse'}}>
          <thead><tr><th>ID</th><th>Symbol</th><th>Action</th><th>Price</th><th>Time</th></tr></thead>
          <tbody>
            {signals.map(s=> (
              <tr key={s.id} onClick={()=>setSelected(s)} style={{cursor:'pointer'}}>
                <td>{s.id}</td>
                <td>{s.symbol}</td>
                <td>{s.action}</td>
                <td>{s.price}</td>
                <td>{s.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <SignalDetails signal={selected} onClose={()=>setSelected(null)} />
    </div>
  )
}
