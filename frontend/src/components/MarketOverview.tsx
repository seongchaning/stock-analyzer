import React from 'react';
import { useStore } from '../store/useStore';

const MarketOverview: React.FC = () => {
  const { marketStats } = useStore();

  if (!marketStats) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-6 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const formatIndex = (index: number): string => {
    return index.toLocaleString('ko-KR', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    });
  };

  const formatChange = (change: number): string => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}`;
  };

  const getChangeColor = (change: number): string => {
    if (change > 0) return 'text-red-500';
    if (change < 0) return 'text-blue-500';
    return 'text-gray-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">📈 시장 현황</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* 코스피 */}
        <div className="text-center">
          <div className="text-sm text-gray-500 mb-1">코스피</div>
          <div className="text-xl font-bold text-gray-900 mb-1">
            {formatIndex(marketStats.kospiIndex)}
          </div>
          <div className={`text-sm font-medium ${getChangeColor(marketStats.kospiChange)}`}>
            {formatChange(marketStats.kospiChange)}
          </div>
        </div>

        {/* 코스닥 */}
        <div className="text-center">
          <div className="text-sm text-gray-500 mb-1">코스닥</div>
          <div className="text-xl font-bold text-gray-900 mb-1">
            {formatIndex(marketStats.kosdaqIndex)}
          </div>
          <div className={`text-sm font-medium ${getChangeColor(marketStats.kosdaqChange)}`}>
            {formatChange(marketStats.kosdaqChange)}
          </div>
        </div>

        {/* 매수 신호 */}
        <div className="text-center">
          <div className="text-sm text-gray-500 mb-1">매수 신호</div>
          <div className="text-xl font-bold text-primary-600 mb-1">
            {marketStats.signalCount}개
          </div>
          <div className="text-sm text-gray-400">
            종목 발견
          </div>
        </div>

        {/* 주요 섹터 */}
        <div className="text-center">
          <div className="text-sm text-gray-500 mb-1">주요 섹터</div>
          <div className="text-sm font-medium text-gray-900">
            {marketStats.topSectors.length > 0 
              ? marketStats.topSectors.slice(0, 2).join(', ')
              : '데이터 없음'
            }
          </div>
          <div className="text-xs text-gray-400 mt-1">
            상위 섹터
          </div>
        </div>
      </div>

      {/* 업데이트 정보 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="text-xs text-gray-400 text-center">
          매일 18:00 KST 업데이트 • 데이터는 6개월간 보관됩니다
        </div>
      </div>
    </div>
  );
};

export default MarketOverview;