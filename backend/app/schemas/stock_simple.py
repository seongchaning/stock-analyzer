"""
간단한 주식 스키마 - pydantic v2 호환
"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class StockDetail(BaseModel):
    """종목 상세 정보"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    sector: str


class CandleData(BaseModel):
    """캔들 데이터"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicator(BaseModel):
    """기술적 지표"""
    date: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None


class ChartData(BaseModel):
    """차트 데이터"""
    symbol: str
    period: str
    candles: List[CandleData]
    indicators: List[TechnicalIndicator]


class StockSearchResult(BaseModel):
    """종목 검색 결과"""
    symbol: str
    name: str
    sector: str
    market_type: str