"""
주식 관련 스키마
"""
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class StockDetail(BaseModel):
    """종목 상세 정보"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    price: float = Field(..., description="현재가")
    change: float = Field(..., description="전일 대비 변화량")
    change_percent: float = Field(..., description="전일 대비 변화율 (%)")
    volume: int = Field(..., description="거래량")
    market_cap: float = Field(..., description="시가총액")
    sector: str = Field(..., description="섹터")
    industry: Optional[str] = Field(None, description="업종")
    listing_date: Optional[date] = Field(None, description="상장일")
    description: Optional[str] = Field(None, description="종목 설명")
    
    # 기술적 지표 (최신 값)
    current_rsi: Optional[float] = Field(None, description="현재 RSI")
    current_macd: Optional[float] = Field(None, description="현재 MACD")
    current_macd_signal: Optional[float] = Field(None, description="현재 MACD 신호선")
    
    class Config:
        from_attributes = True


class StockDetailResponse(BaseResponse[StockDetail]):
    """종목 상세 정보 응답"""
    pass


class CandleData(BaseModel):
    """캔들 데이터"""
    date: date = Field(..., description="날짜")
    open: float = Field(..., description="시가")
    high: float = Field(..., description="고가")
    low: float = Field(..., description="저가")
    close: float = Field(..., description="종가")
    volume: int = Field(..., description="거래량")
    
    class Config:
        from_attributes = True


class TechnicalIndicator(BaseModel):
    """기술적 지표 데이터"""
    date: date = Field(..., description="날짜")
    rsi: Optional[float] = Field(None, description="RSI")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD 신호선")
    macd_histogram: Optional[float] = Field(None, description="MACD 히스토그램")
    
    class Config:
        from_attributes = True


class ChartData(BaseModel):
    """차트 데이터 통합"""
    symbol: str = Field(..., description="종목 코드")
    period: str = Field(..., description="조회 기간")
    candles: List[CandleData] = Field(..., description="캔들 데이터")
    indicators: List[TechnicalIndicator] = Field(..., description="기술적 지표")
    
    class Config:
        from_attributes = True


class ChartDataResponse(BaseResponse[ChartData]):
    """차트 데이터 응답"""
    pass


class StockSearchResult(BaseModel):
    """종목 검색 결과"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    sector: str = Field(..., description="섹터")
    market_type: str = Field(..., description="시장 구분 (KOSPI/KOSDAQ)")
    
    class Config:
        from_attributes = True