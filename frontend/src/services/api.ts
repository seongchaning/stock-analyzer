import axios from 'axios';
import { ApiResponse, BuySignal, Stock, ChartData, TechnicalIndicator, MarketStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const stockApi = {
  // 매수 신호 목록 조회
  getBuySignals: async (): Promise<BuySignal[]> => {
    const response = await api.get<ApiResponse<BuySignal[]>>('/api/v1/screening/signals');
    return response.data.data;
  },

  // 종목 상세 정보 조회
  getStockDetail: async (symbol: string): Promise<Stock> => {
    const response = await api.get<ApiResponse<Stock>>(`/api/v1/stocks/${symbol}`);
    return response.data.data;
  },

  // 차트 데이터 조회
  getChartData: async (symbol: string, period: string = '6M'): Promise<{
    candles: ChartData[];
    indicators: TechnicalIndicator[];
  }> => {
    const response = await api.get<ApiResponse<{
      candles: ChartData[];
      indicators: TechnicalIndicator[];
    }>>(`/api/v1/stocks/${symbol}/chart?period=${period}`);
    return response.data.data;
  },

  // 시장 통계 조회
  getMarketStats: async (): Promise<MarketStats> => {
    const response = await api.get<ApiResponse<MarketStats>>('/api/v1/market/stats');
    return response.data.data;
  },
};

export default api;