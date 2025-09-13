import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import StockListPage from './pages/StockListPage';
import StockDetailPage from './pages/StockDetailPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/stocks" element={<StockListPage />} />
          <Route path="/stock/:symbol" element={<StockDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
