import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

interface CandleData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  color?: string;
}

interface TechnicalIndicator {
  date: string;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
}

interface ChartData {
  symbol: string;
  period: string;
  candles: CandleData[];
  indicators: TechnicalIndicator[];
}

interface StockInfo {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  sector: string;
  current_rsi: number | null;
  current_macd: number | null;
  current_macd_signal: number | null;
}

// 이동평균 계산 함수
const calculateMovingAverage = (data: any[], period: number) => {
  return data.map((item, index) => {
    if (index < period - 1) return null;
    
    const sum = data.slice(index - period + 1, index + 1)
      .reduce((acc, curr) => acc + curr.close, 0);
    return sum / period;
  });
};

// 캔들스틱 차트 컴포넌트
const CandlestickChart = ({ data }: { data: any[] }) => {
  console.log('CandlestickChart data:', data);
  
  if (!data || data.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-gray-50 rounded">
        <p className="text-gray-500">차트 데이터가 없습니다.</p>
      </div>
    );
  }

  // 이동평균선 계산
  const ma5 = calculateMovingAverage(data, 5);
  const ma20 = calculateMovingAverage(data, 20);
  const ma60 = calculateMovingAverage(data, 60);
  const ma120 = calculateMovingAverage(data, 120);

  // 캔들스틱과 이동평균 데이터 결합
  const chartData = data.map((item, index) => ({
    ...item,
    ma5: ma5[index],
    ma20: ma20[index], 
    ma60: ma60[index],
    ma120: ma120[index]
  }));

  // 최고가와 최저가 찾기
  const allPrices = chartData.flatMap(d => [d.high, d.low]).filter(Boolean);
  const maxPrice = Math.max(...allPrices);
  const minPrice = Math.min(...allPrices);
  
  console.log('Max price:', maxPrice, 'Min price:', minPrice);

  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
          />
          <YAxis 
            domain={['dataMin - 1000', 'dataMax + 1000']}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                const formatPrice = (price: number) => price ? price.toLocaleString('ko-KR') + '원' : 'N/A';
                const isRising = data.close > data.open;
                
                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                    <p className="font-medium">{new Date(label as string).toLocaleDateString('ko-KR')}</p>
                    <div className="space-y-1 text-sm">
                      <p>시가: <span className="font-medium">{formatPrice(data.open)}</span></p>
                      <p>고가: <span className="font-medium text-red-600">{formatPrice(data.high)}</span></p>
                      <p>저가: <span className="font-medium text-blue-600">{formatPrice(data.low)}</span></p>
                      <p>종가: <span className={`font-medium ${isRising ? 'text-red-600' : 'text-blue-600'}`}>
                        {formatPrice(data.close)}
                      </span></p>
                      <p>거래량: <span className="font-medium">{data.volume.toLocaleString('ko-KR')}</span></p>
                      {data.ma5 && <p>MA5: <span className="text-green-600">{formatPrice(data.ma5)}</span></p>}
                      {data.ma20 && <p>MA20: <span className="text-orange-600">{formatPrice(data.ma20)}</span></p>}
                      {data.ma60 && <p>MA60: <span className="text-blue-600">{formatPrice(data.ma60)}</span></p>}
                      {data.ma120 && <p>MA120: <span className="text-purple-600">{formatPrice(data.ma120)}</span></p>}
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          
          {/* 캔들스틱 바 - Recharts 좌표계 활용 */}
          <Bar 
            dataKey="high" 
            fill="transparent"
            shape={(props: any) => {
              const { payload, x, width } = props;
              if (!payload) return <g />;
              
              const { open, high, low, close } = payload;
              const isRising = close > open;
              const candleColor = isRising ? '#ef4444' : '#3b82f6';
              
              // Recharts가 제공하는 X 좌표와 width 활용
              const candleWidth = Math.max(width * 0.6, 2);
              const wickWidth = 1;
              const candleX = x + (width - candleWidth) / 2;
              const wickX = x + width / 2;
              
              // Y 좌표는 도메인 비례로 계산 (차트 높이 384px 기준)
              const chartHeight = 320; // h-96 = 384px, 여백 고려
              const chartTop = 20;
              
              // 현재 차트의 Y 도메인 계산
              const allPrices = chartData.flatMap(d => [d.high, d.low, d.open, d.close]).filter(Boolean);
              const chartMinPrice = Math.min(...allPrices) - 1000; // YAxis domain에서 사용하는 값
              const chartMaxPrice = Math.max(...allPrices) + 1000;
              const priceRange = chartMaxPrice - chartMinPrice;
              
              const yScale = (price: number) => {
                return chartTop + ((chartMaxPrice - price) / priceRange) * chartHeight;
              };
              
              const highY = yScale(high);
              const lowY = yScale(low);
              const openY = yScale(open);
              const closeY = yScale(close);
              
              const candleTop = Math.min(openY, closeY);
              const candleBottom = Math.max(openY, closeY);
              const candleHeight = Math.max(candleBottom - candleTop, 1);
              
              // 실제 최고가와 최저가 비교
              const actualMaxPrice = Math.max(...allPrices);
              const actualMinPrice = Math.min(...allPrices);
              
              console.log('Payload:', payload.date, 'High:', high, 'Low:', low, 'Max:', actualMaxPrice, 'Min:', actualMinPrice);
              
              return (
                <g>
                  {/* 심지 (wick) - high-low 라인 */}
                  <line
                    x1={wickX}
                    y1={highY}
                    x2={wickX}
                    y2={lowY}
                    stroke={candleColor}
                    strokeWidth={wickWidth}
                  />
                  
                  {/* 캔들 몸체 (body) - open-close 박스 */}
                  <rect
                    x={candleX}
                    y={candleTop}
                    width={candleWidth}
                    height={candleHeight}
                    fill={isRising ? candleColor : '#ffffff'}
                    stroke={candleColor}
                    strokeWidth={1}
                  />
                  
                  {/* 최고가 표시 */}
                  {high === actualMaxPrice && (
                    <>
                      <circle cx={wickX} cy={highY} r="4" fill="#ef4444" stroke="#ffffff" strokeWidth="2" />
                      <rect 
                        x={Math.max(wickX - 55, 10)} 
                        y={Math.max(highY + 8, 30)} 
                        width="110" 
                        height="16" 
                        fill="rgba(239, 68, 68, 0.9)" 
                        rx="3"
                      />
                      <text 
                        x={Math.max(wickX - 51, 14)} 
                        y={Math.max(highY + 19, 41)} 
                        fontSize="11" 
                        fill="#ffffff" 
                        fontWeight="bold"
                        textAnchor="start"
                      >
                        최고가: {actualMaxPrice.toLocaleString()}원
                      </text>
                    </>
                  )}
                  
                  {/* 최저가 표시 */}
                  {low === actualMinPrice && (
                    <>
                      <circle cx={wickX} cy={lowY} r="4" fill="#3b82f6" stroke="#ffffff" strokeWidth="2" />
                      <rect 
                        x={Math.max(wickX - 55, 10)} 
                        y={Math.min(lowY - 24, chartHeight - 20)} 
                        width="110" 
                        height="16" 
                        fill="rgba(59, 130, 246, 0.9)" 
                        rx="3"
                      />
                      <text 
                        x={Math.max(wickX - 51, 14)} 
                        y={Math.min(lowY - 13, chartHeight - 9)} 
                        fontSize="11" 
                        fill="#ffffff" 
                        fontWeight="bold"
                        textAnchor="start"
                      >
                        최저가: {actualMinPrice.toLocaleString()}원
                      </text>
                    </>
                  )}
                </g>
              );
            }}
            name="Candlesticks"
          />
          
          {/* 이동평균선들 */}
          <Line 
            type="monotone" 
            dataKey="ma5" 
            stroke="#22c55e" 
            strokeWidth={1}
            dot={false}
            connectNulls={false}
            name="MA5"
          />
          <Line 
            type="monotone" 
            dataKey="ma20" 
            stroke="#f97316" 
            strokeWidth={1}
            dot={false}
            connectNulls={false}
            name="MA20"
          />
          <Line 
            type="monotone" 
            dataKey="ma60" 
            stroke="#3b82f6" 
            strokeWidth={1}
            dot={false}
            connectNulls={false}
            name="MA60"
          />
          <Line 
            type="monotone" 
            dataKey="ma120" 
            stroke="#8b5cf6" 
            strokeWidth={1}
            dot={false}
            connectNulls={false}
            name="MA120"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

const StockDetailPage: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState('3M');

  useEffect(() => {
    const fetchData = async () => {
      if (!symbol) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // 차트 데이터와 주식 정보를 병렬로 가져오기
        const [chartResponse, stockResponse] = await Promise.all([
          fetch(`http://localhost:8000/api/v1/stocks/${symbol}/chart?period=${period}`),
          fetch(`http://localhost:8000/api/v1/stocks/${symbol}`)
        ]);

        if (!chartResponse.ok || !stockResponse.ok) {
          throw new Error('데이터 로딩 실패');
        }

        const chartResult = await chartResponse.json();
        const stockResult = await stockResponse.json();

        setChartData(chartResult.data);
        setStockInfo(stockResult.data);
      } catch (error) {
        setError(error instanceof Error ? error.message : '데이터 로딩 중 오류가 발생했습니다.');
        console.error('Error fetching stock data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, period]);

  // 차트 데이터 통합 (가격 + 지표)
  const combinedData = React.useMemo(() => {
    if (!chartData) return [];
    
    const dataMap = new Map();
    
    // 캔들 데이터 추가
    chartData.candles.forEach(candle => {
      const isRising = candle.close > candle.open;
      dataMap.set(candle.date, {
        ...candle,
        color: isRising ? '#ef4444' : '#3b82f6'
      });
    });
    
    // 기술적 지표 추가
    chartData.indicators.forEach(indicator => {
      const existing = dataMap.get(indicator.date);
      if (existing) {
        dataMap.set(indicator.date, {
          ...existing,
          ...indicator
        });
      }
    });
    
    return Array.from(dataMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [chartData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">차트 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error || !stockInfo || !chartData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">데이터 로딩 실패</h1>
          <p className="text-gray-600 mb-4">{error || '종목 정보를 찾을 수 없습니다.'}</p>
          <Link
            to="/stocks"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            종목 리스트로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  const formatPrice = (price: number) => {
    return price.toLocaleString('ko-KR') + '원';
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return (marketCap / 1e12).toFixed(1) + '조원';
    } else if (marketCap >= 1e8) {
      return (marketCap / 1e8).toFixed(0) + '억원';
    }
    return marketCap.toLocaleString('ko-KR') + '원';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        {/* 헤더 */}
        <div className="mb-6">
          <Link
            to="/stocks"
            className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
          >
            ← 종목 리스트로 돌아가기
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {stockInfo.name} ({stockInfo.symbol})
              </h1>
              <div className="flex items-center mt-2">
                <span className="text-2xl font-bold mr-4">
                  {formatPrice(stockInfo.price)}
                </span>
                <span className={`text-lg font-semibold ${
                  stockInfo.change >= 0 ? 'text-red-600' : 'text-blue-600'
                }`}>
                  {stockInfo.change >= 0 ? '+' : ''}{formatPrice(stockInfo.change)}
                  ({stockInfo.change >= 0 ? '+' : ''}{stockInfo.change_percent.toFixed(2)}%)
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">거래량</div>
              <div className="text-lg font-semibold">
                {stockInfo.volume.toLocaleString('ko-KR')}
              </div>
              <div className="text-sm text-gray-600 mt-2">시가총액</div>
              <div className="text-lg font-semibold">
                {formatMarketCap(stockInfo.market_cap)}
              </div>
            </div>
          </div>
        </div>

        {/* 기술적 지표 요약 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">기술적 지표</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">RSI</div>
              <div className={`text-2xl font-bold ${
                stockInfo.current_rsi 
                  ? stockInfo.current_rsi < 30 
                    ? 'text-blue-600' 
                    : stockInfo.current_rsi > 70 
                    ? 'text-red-600' 
                    : 'text-gray-900'
                  : 'text-gray-400'
              }`}>
                {stockInfo.current_rsi ? stockInfo.current_rsi.toFixed(1) : 'N/A'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stockInfo.current_rsi 
                  ? stockInfo.current_rsi < 30 
                    ? '과매도' 
                    : stockInfo.current_rsi > 70 
                    ? '과매수' 
                    : '중립'
                  : ''}
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">MACD</div>
              <div className={`text-xl font-bold ${
                stockInfo.current_macd && stockInfo.current_macd_signal
                  ? stockInfo.current_macd > stockInfo.current_macd_signal
                    ? 'text-red-600'
                    : 'text-blue-600'
                  : 'text-gray-400'
              }`}>
                {stockInfo.current_macd ? stockInfo.current_macd.toFixed(0) : 'N/A'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stockInfo.current_macd && stockInfo.current_macd_signal
                  ? stockInfo.current_macd > stockInfo.current_macd_signal
                    ? '골든크로스'
                    : '데드크로스'
                  : ''}
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">섹터</div>
              <div className="text-lg font-semibold text-gray-900">
                {stockInfo.sector}
              </div>
            </div>
          </div>
        </div>

        {/* 기간 선택 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">일봉 캔들스틱 차트</h2>
            <div className="flex space-x-2">
              {['1M', '3M', '6M', '1Y'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    period === p
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* 일봉 캔들스틱 차트 */}
          <div className="mb-6">
            <CandlestickChart data={combinedData} />
          </div>

          {/* 거래량 차트 */}
          <div className="h-32 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">거래량</h3>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={combinedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value as string).toLocaleDateString('ko-KR')}
                  formatter={(value: any) => [Number(value).toLocaleString('ko-KR'), '거래량']}
                />
                
                <Bar dataKey="volume">
                  {combinedData.map((entry, index) => (
                    <Cell 
                      key={`volume-cell-${index}`} 
                      fill={entry.color || '#64748b'}
                      opacity={0.7}
                    />
                  ))}
                </Bar>
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* RSI 차트 */}
          <div className="h-64 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">RSI (상대강도지수)</h3>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={combinedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value as string).toLocaleDateString('ko-KR')}
                  formatter={(value: any) => [Number(value).toFixed(1), 'RSI']}
                />
                
                {/* 과매수/과매도 선 */}
                <Line type="monotone" dataKey={() => 70} stroke="#ef4444" strokeDasharray="5 5" dot={false} name="과매수(70)" />
                <Line type="monotone" dataKey={() => 30} stroke="#3b82f6" strokeDasharray="5 5" dot={false} name="과매도(30)" />
                <Line 
                  type="monotone" 
                  dataKey="rsi" 
                  stroke="#8b5cf6" 
                  strokeWidth={2} 
                  dot={false}
                  name="RSI"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* MACD 차트 */}
          <div className="h-64">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">MACD</h3>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={combinedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value as string).toLocaleDateString('ko-KR')}
                  formatter={(value: any, name: string) => [
                    Number(value).toFixed(1), 
                    name === 'macd' ? 'MACD' : name === 'macd_signal' ? 'Signal' : 'Histogram'
                  ]}
                />
                
                <Bar dataKey="macd_histogram" fill="#64748b" opacity={0.6} name="Histogram" />
                <Line 
                  type="monotone" 
                  dataKey="macd" 
                  stroke="#dc2626" 
                  strokeWidth={2} 
                  dot={false}
                  name="MACD"
                />
                <Line 
                  type="monotone" 
                  dataKey="macd_signal" 
                  stroke="#2563eb" 
                  strokeWidth={2} 
                  dot={false}
                  name="Signal"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetailPage;