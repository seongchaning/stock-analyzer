import { create } from 'zustand';
import { BuySignal, Stock, MarketStats } from '../types';

interface AppState {
  // 데이터 상태
  buySignals: BuySignal[];
  selectedStock: Stock | null;
  marketStats: MarketStats | null;
  
  // UI 상태
  isLoading: boolean;
  error: string | null;
  
  // 필터 상태
  sortBy: 'signal_strength' | 'change_percent' | 'market_cap';
  filterSector: string | null;
  
  // 액션
  setBuySignals: (signals: BuySignal[]) => void;
  setSelectedStock: (stock: Stock | null) => void;
  setMarketStats: (stats: MarketStats | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSortBy: (sortBy: 'signal_strength' | 'change_percent' | 'market_cap') => void;
  setFilterSector: (sector: string | null) => void;
  
  // 계산된 데이터
  getFilteredSignals: () => BuySignal[];
}

export const useStore = create<AppState>((set, get) => ({
  // 초기 상태
  buySignals: [],
  selectedStock: null,
  marketStats: null,
  isLoading: false,
  error: null,
  sortBy: 'signal_strength',
  filterSector: null,
  
  // 액션
  setBuySignals: (signals) => set({ buySignals: signals }),
  setSelectedStock: (stock) => set({ selectedStock: stock }),
  setMarketStats: (stats) => set({ marketStats: stats }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSortBy: (sortBy) => set({ sortBy }),
  setFilterSector: (sector) => set({ filterSector: sector }),
  
  // 계산된 데이터
  getFilteredSignals: () => {
    const { buySignals, sortBy, filterSector } = get();
    
    let filtered = [...buySignals];
    
    // 섹터 필터링
    if (filterSector) {
      filtered = filtered.filter(signal => signal.sector === filterSector);
    }
    
    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'signal_strength':
          return b.signal_strength - a.signal_strength;
        case 'change_percent':
          return b.change_percent - a.change_percent;
        case 'market_cap':
          return b.market_cap - a.market_cap;
        default:
          return 0;
      }
    });
    
    return filtered;
  },
}));