import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* 추후 추가될 라우트들 */}
          {/* <Route path="/stock/:symbol" element={<StockDetailPage />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
