import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface StockItem {
  symbol: string;
  name: string;
  sector: string;
  market_type: string;
}

interface ApiResponse {
  data: StockItem[];
  message: string;
  success: boolean;
}

const StockListPage: React.FC = () => {
  const [stocks, setStocks] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  
  const ITEMS_PER_PAGE = 20;
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchStocks = async (page: number = 1, query: string = '') => {
    try {
      setLoading(true);
      setError(null);
      
      const offset = (page - 1) * ITEMS_PER_PAGE;
      const params = new URLSearchParams({
        limit: ITEMS_PER_PAGE.toString(),
        offset: offset.toString(),
      });
      
      if (query) {
        params.set('query', query);
      }
      
      const response = await axios.get<ApiResponse>(
        `${API_BASE_URL}/api/v1/stocks/?${params}`
      );
      
      if (response.data.success) {
        setStocks(response.data.data);
      } else {
        setError('데이터를 불러오는데 실패했습니다.');
      }
    } catch (err) {
      console.error('API Error:', err);
      setError('서버와의 연결에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks(currentPage, searchQuery);
  }, [currentPage]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchStocks(1, searchQuery);
  };

  const handleNextPage = () => {
    setCurrentPage(prev => prev + 1);
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <Link to="/" className="text-blue-600 hover:text-blue-800">
                ← 홈으로 돌아가기
              </Link>
              <h1 className="text-2xl font-bold text-gray-900 mt-2">종목 리스트</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="종목명 또는 종목코드로 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              검색
            </button>
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  setCurrentPage(1);
                  fetchStocks(1, '');
                }}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                초기화
              </button>
            )}
          </div>
        </form>

        {/* Content */}
        {loading && (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">종목 데이터를 불러오는 중...</div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="text-red-700">{error}</div>
          </div>
        )}

        {!loading && !error && stocks.length === 0 && (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">검색 결과가 없습니다.</div>
          </div>
        )}

        {!loading && !error && stocks.length > 0 && (
          <>
            {/* Stock List */}
            <div className="bg-white shadow-sm rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b">
                <div className="grid grid-cols-4 gap-4 font-medium text-gray-700">
                  <div>종목코드</div>
                  <div>종목명</div>
                  <div>시장구분</div>
                  <div>섹터</div>
                </div>
              </div>
              <div className="divide-y divide-gray-200">
                {stocks.map((stock) => (
                  <div
                    key={stock.symbol}
                    className="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => {
                      // TODO: Navigate to stock detail page
                      console.log('Navigate to stock:', stock.symbol);
                    }}
                  >
                    <div className="grid grid-cols-4 gap-4 items-center">
                      <div className="font-mono text-sm font-medium text-blue-600">
                        {stock.symbol}
                      </div>
                      <div className="font-medium text-gray-900">
                        {stock.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          stock.market_type === 'KOSPI' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {stock.market_type}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {stock.sector}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pagination */}
            <div className="flex justify-center items-center gap-4 mt-6">
              <button
                onClick={handlePrevPage}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                이전 페이지
              </button>
              <span className="text-gray-600">
                페이지 {currentPage}
              </span>
              <button
                onClick={handleNextPage}
                disabled={stocks.length < ITEMS_PER_PAGE}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                다음 페이지
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StockListPage;