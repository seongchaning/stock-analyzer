// 종목 정보 타입
export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap: number;
  sector: string;
}

// 기술적 지표 타입
export interface TechnicalIndicator {
  date: string;
  rsi: number;
  macd: number;
  macdSignal: number;
  macdHistogram: number;
}

// 매수 신호 타입
export interface BuySignal {
  stock: Stock;
  signalStrength: number;
  rsi: number;
  macd: number;
  reason: string;
  date: string;
}

// 차트 데이터 타입
export interface ChartData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// API 응답 타입
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// 시장 통계 타입
export interface MarketStats {
  kospiIndex: number;
  kospiChange: number;
  kosdaqIndex: number;
  kosdaqChange: number;
  signalCount: number;
  topSectors: string[];
}