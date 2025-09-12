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
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  market_cap: number;
  sector: string;
  signal_strength: number;
  rsi: number;
  macd: number;
  macd_signal: number;
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
  kospi_index: number;
  kospi_change: number;
  kosdaq_index: number;
  kosdaq_change: number;
  signal_count: number;
  strong_signal_count: number;
  top_sectors: string[];
  sector_distribution: Record<string, number>;
  last_updated: string;
}