import React from 'react';
import { useStore } from '../store/useStore';

const FilterControls: React.FC = () => {
  const {
    sortBy,
    filterSector,
    buySignals,
    setSortBy,
    setFilterSector,
  } = useStore();

  // 유니크한 섹터 목록 생성
  const uniqueSectors = React.useMemo(() => {
    const sectors = buySignals.map(signal => signal.sector);
    return Array.from(new Set(sectors)).sort();
  }, [buySignals]);

  const sortOptions = [
    { value: 'signal_strength', label: '신호강도순' },
    { value: 'change_percent', label: '등락률순' },
    { value: 'market_cap', label: '시가총액순' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        {/* 정렬 선택 */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
            정렬:
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* 섹터 필터 */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
            섹터:
          </label>
          <select
            value={filterSector || ''}
            onChange={(e) => setFilterSector(e.target.value || null)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 min-w-[120px]"
          >
            <option value="">전체</option>
            {uniqueSectors.map((sector) => (
              <option key={sector} value={sector}>
                {sector}
              </option>
            ))}
          </select>
        </div>

        {/* 초기화 버튼 */}
        <button
          onClick={() => {
            setSortBy('signal_strength');
            setFilterSector(null);
          }}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors border border-gray-300"
        >
          필터 초기화
        </button>

        {/* 결과 개수 */}
        <div className="text-sm text-gray-500 sm:ml-auto">
          총 {buySignals.length}개 종목
          {filterSector && (
            <span className="ml-1">
              ({filterSector}: {buySignals.filter(s => s.sector === filterSector).length}개)
            </span>
          )}
        </div>
      </div>

      {/* 활성 필터 표시 */}
      {(sortBy !== 'signal_strength' || filterSector) && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex flex-wrap gap-2">
            <span className="text-xs text-gray-500">적용된 필터:</span>
            
            {sortBy !== 'signal_strength' && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-100 text-primary-700">
                {sortOptions.find(opt => opt.value === sortBy)?.label}
              </span>
            )}
            
            {filterSector && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700">
                섹터: {filterSector}
                <button
                  onClick={() => setFilterSector(null)}
                  className="ml-1 hover:text-green-900"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterControls;