import React, { useState } from 'react';

function App() {
  const [symbol, setSymbol] = useState('');
  const [stockData, setStockData] = useState([]);
  const [error, setError] = useState('');

  const fetchStockData = async () => {
    setError(''); // Reset any previous errors
    try {
      const response = await fetch(`http://127.0.0.1:5000/stocks?symbol=${symbol}`);
      const data = await response.json();
      if (response.ok) {
        setStockData(data); // Update stock data
      } else {
        setError(data.error || 'Error fetching stock data');
      }
    } catch (error) {
      setError('Error connecting to the API');
    }
  };

  const handleInputChange = (e) => {
    setSymbol(e.target.value);
  };

  const handleFetch = () => {
    if (symbol) {
      fetchStockData();
    } else {
      setError('Please enter a stock symbol');
    }
  };

  return (
    <div>
      <h1>Stock Tracker</h1>

      {/* Input for stock symbol */}
      <input 
        type="text" 
        value={symbol} 
        onChange={handleInputChange} 
        placeholder="Enter stock symbol" 
      />
      <button onClick={handleFetch}>Fetch Stock Data</button>

      {/* Error message */}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Display stock data */}
      {stockData.length > 0 && (
        <table border="1">
          <thead>
            <tr>
              <th>Date</th>
              <th>Close</th>
              <th>SMA_50</th>
              <th>Upper BB</th>
              <th>Lower BB</th>
              <th>%K</th>
              <th>%D</th>
            </tr>
          </thead>
          <tbody>
            {stockData.map((row, index) => (
              <tr key={index}>
                <td>{row.Date}</td>
                <td>{row.Close}</td>
                <td>{row.SMA_50}</td>
                <td>{row.Upper_BB}</td>
                <td>{row.Lower_BB}</td>
                <td>{row['%K']}</td>
                <td>{row['%D']}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
