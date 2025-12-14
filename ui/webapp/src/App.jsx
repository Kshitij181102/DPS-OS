import React, {useState, useEffect} from 'react'

export default function App(){
  const [rules, setRules] = useState([
    {
      from: 'zone1',
      to: 'zone2', 
      trigger: 'openSensitiveUrl',
      actions: ['enableVpn', 'lockClipboard']
    },
    {
      from: '*',
      to: 'zone3',
      trigger: 'usbPlugged', 
      actions: ['remountHomeRo', 'notifyUser']
    }
  ])
  const [zones, setZones] = useState({
    zone1: {name: 'Normal'},
    zone2: {name: 'Sensitive'}, 
    zone3: {name: 'Ultra'}
  })
  
  useEffect(()=>{
    // Load rules from local API or daemon
    // For prototype, could use fetch to local REST endpoint
  },[])
  
  return (
    <div className="container">
      <h1 className="header">DPS-OS Rule Manager</h1>
      
      <div className="grid">
        {/* Zones Section */}
        <div className="card">
          <h2 className="card-title">Privacy Zones</h2>
          <div className="zone-list">
            {Object.entries(zones).map(([id, zone]) => (
              <div key={id} className="zone-item">
                <span className="zone-name">{zone.name}</span>
                <span className="zone-id">({id})</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Rules Section */}
        <div className="card">
          <h2 className="card-title">Transition Rules</h2>
          <div className="rule-list">
            {rules.map((rule, idx) => (
              <div key={idx} className="rule-item">
                <div className="rule-transition">
                  {rule.from} → {rule.to}
                </div>
                <div className="rule-trigger">
                  Trigger: {rule.trigger}
                </div>
                <div className="rule-actions">
                  Actions: {rule.actions?.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Add Rule Form */}
      <div className="form-section">
        <h3 className="form-title">Add New Rule</h3>
        <div className="form-grid">
          <input 
            type="text" 
            placeholder="From Zone" 
            className="form-input"
          />
          <input 
            type="text" 
            placeholder="To Zone" 
            className="form-input"
          />
          <select className="form-select">
            <option>Select Trigger</option>
            <option value="usbPlugged">USB Plugged</option>
            <option value="openSensitiveUrl">Sensitive URL</option>
          </select>
        </div>
        <button className="btn">
          Add Rule
        </button>
      </div>
    </div>
  )
}