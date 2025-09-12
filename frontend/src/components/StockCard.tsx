import React from 'react';
import { BuySignal } from '../types';
import { useNavigate } from 'react-router-dom';

interface StockCardProps {
  signal: BuySignal;
}

const StockCard: React.FC<StockCardProps> = ({ signal }) => {
  const navigate = useNavigate();
  const { stock } = signal;

  const handleClick = () => {
    navigate(`/stock/${stock.symbol}`);
  };

  const formatNumber = (num: number): string => {
    if (num >= 1e12) {
      return `${(num / 1e12).toFixed(1)}조`;
    } else if (num >= 1e8) {
      return `${(num / 1e8).toFixed(0)}억`;
    } else if (num >= 1e4) {
      return `${(num / 1e4).toFixed(0)}만`;
    }
    return num.toLocaleString();
  };

  const formatPrice = (price: number): string => {
    return price.toLocaleString() + '원';
  };

  const getSignalStrengthColor = (strength: number): string => {
    if (strength >= 80) return 'bg-green-500';
    if (strength >= 60) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const getChangeColor = (change: number): string => {
    if (change > 0) return 'text-red-500';
    if (change < 0) return 'text-blue-500';
    return 'text-gray-500';
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-6 border border-gray-200"
    >
      {/* 헤더 */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{stock.name}</h3>
          <p className="text-sm text-gray-500">{stock.symbol}</p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium text-white ${getSignalStrengthColor(signal.signalStrength)}`}>
          신호강도 {signal.signalStrength}
        </div>
      </div>

      {/* 가격 정보 */}
      <div className="mb-4">
        <div className="text-xl font-bold text-gray-900 mb-1">
          {formatPrice(stock.price)}
        </div>
        <div className={`text-sm font-medium ${getChangeColor(stock.change)}`}>
          {stock.change > 0 ? '+' : ''}{formatPrice(stock.change)} 
          ({stock.changePercent > 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%)
        </div>
      </div>

      {/* 기술적 지표 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-xs text-gray-500">RSI</div>
          <div className="text-sm font-semibold">{signal.rsi.toFixed(1)}</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-xs text-gray-500">MACD</div>
          <div className="text-sm font-semibold">{signal.macd.toFixed(3)}</div>
        </div>
      </div>

      {/* 추가 정보 */}
      <div className="border-t pt-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>시가총액</span>
          <span>{formatNumber(stock.marketCap)}</span>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>섹터</span>
          <span>{stock.sector}</span>
        </div>
        <div className="text-xs text-gray-400 mt-2">
          {signal.reason}
        </div>
      </div>
    </div>
  );
};

export default StockCard;