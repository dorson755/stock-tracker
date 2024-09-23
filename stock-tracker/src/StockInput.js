// StockInput.js
import React from 'react';

const StockInput = ({ symbol, setSymbol, fetchData }) => {
    const handleInputChange = (e) => {
        setSymbol(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        fetchData(symbol); // Trigger the data fetching function
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={symbol}
                onChange={handleInputChange}
                placeholder="Enter stock symbol"
                required
            />
            <button type="submit">Fetch Data</button>
        </form>
    );
};

export default StockInput;
