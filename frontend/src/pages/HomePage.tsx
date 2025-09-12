import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { stockApi } from '../services/api';
import StockCard from '../components/StockCard';
import MarketOverview from '../components/MarketOverview';
import FilterControls from '../components/FilterControls';

const HomePage: React.FC = () => {
  const {
    isLoading,
    error,
    setLoading,
    setError,
    setBuySignals,
    setMarketStats,
    getFilteredSignals,
  } = useStore();

  const filteredSignals = getFilteredSignals();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [signals, stats] = await Promise.all([
          stockApi.getBuySignals(),
          stockApi.getMarketStats(),
        ]);
        
        setBuySignals(signals);
        setMarketStats(stats);
      } catch (err) {
        console.error('API Error Details:', err);
        if (err instanceof Error) {
          console.error('Error message:', err.message);
        }
        setError(`데이터를 불러오는데 실패했습니다. 오류: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [setBuySignals, setMarketStats, setLoading, setError]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️ 오류 발생</div>
          <div className="text-gray-600">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎯 한국 주식 매수 신호
          </h1>
          <p className="text-gray-600">
            RSI 과매도 + MACD 골든크로스 기반 기술적 분석
          </p>
        </div>

        {/* 시장 개요 */}
        <div className="mb-8">
          <MarketOverview />
        </div>

        {/* 필터 컨트롤 */}
        <div className="mb-6">
          <FilterControls />
        </div>

        {/* 매수 신호 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSignals.length > 0 ? (
            filteredSignals.map((signal, index) => (
              <StockCard 
                key={`${signal.symbol}-${index}`} 
                signal={signal} 
              />
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <div className="text-gray-500 text-lg">
                조건에 맞는 매수 신호가 없습니다.
              </div>
            </div>
          )}
        </div>

        {/* 푸터 */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>⚠️ 본 서비스는 정보 제공 목적이며, 투자 조언이 아닙니다.</p>
          <p>모든 투자 결정은 개인의 책임입니다.</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;