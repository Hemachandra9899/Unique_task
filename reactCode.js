import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [bagTagId, setBagTagId] = useState('');
  const [destinationGate, setDestinationGate] = useState('');
  const [locationScanned, setLocationScanned] = useState('');
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post('http://localhost:5000/baggage/scan', {
      bag_tag_id: bagTagId,
      destination_gate: destinationGate,
      location_scanned: locationScanned
    });
    setResponse(res.data);
  };

  return (
    <div className="App" style={{ padding: '2rem' }}>
      <h2>Scan New Bag</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Bag Tag ID" value={bagTagId} onChange={e => setBagTagId(e.target.value)} /><br />
        <input placeholder="Destination Gate" value={destinationGate} onChange={e => setDestinationGate(e.target.value)} /><br />
        <input placeholder="Location Scanned" value={locationScanned} onChange={e => setLocationScanned(e.target.value)} /><br />
        <button type="submit">Log Scan</button>
      </form>

      {response && (
        <div>
          <h4>Response:</h4>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
