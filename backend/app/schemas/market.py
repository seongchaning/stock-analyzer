"""
시장 관련 스키마
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class MarketIndex(BaseModel):
    """시장 지수 정보"""
    name: str = Field(..., description="지수명")
    code: str = Field(..., description="지수 코드")
    value: float = Field(..., description="지수 값")
    change: float = Field(..., description="전일 대비 변화량")
    change_percent: float = Field(..., description="전일 대비 변화율 (%)")
    volume: Optional[int] = Field(None, description="거래량")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    
    class Config:
        from_attributes = True


class SectorStats(BaseModel):
    """섹터 통계"""
    sector: str = Field(..., description="섹터명")
    stock_count: int = Field(..., description="종목 수")
    signal_count: int = Field(..., description="신호 발생 종목 수")
    avg_change_percent: float = Field(..., description="평균 등락률")
    market_cap_ratio: float = Field(..., description="시가총액 비중 (%)")
    
    class Config:
        from_attributes = True


class MarketStats(BaseModel):
    """시장 통계 정보"""
    kospi_index: float = Field(..., description="코스피 지수")
    kospi_change: float = Field(..., description="코스피 변화량")
    kosdaq_index: float = Field(..., description="코스닥 지수")
    kosdaq_change: float = Field(..., description="코스닥 변화량")
    
    signal_count: int = Field(..., description="총 매수 신호 개수")
    strong_signal_count: int = Field(..., description="강한 신호 개수")
    
    top_sectors: List[str] = Field(..., description="신호가 많은 상위 섹터")
    sector_distribution: Dict[str, int] = Field(..., description="섹터별 신호 분포")
    
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    
    class Config:
        from_attributes = True


class MarketStatsResponse(BaseResponse[MarketStats]):
    """시장 통계 응답"""
    pass


class DataHealth(BaseModel):
    """데이터 상태 정보"""
    total_stocks: int = Field(..., description="전체 종목 수")
    active_stocks: int = Field(..., description="활성 종목 수")
    last_data_update: datetime = Field(..., description="마지막 데이터 업데이트")
    data_freshness_hours: float = Field(..., description="데이터 신선도 (시간)")
    
    # 데이터 품질 지표
    missing_price_count: int = Field(..., description="가격 정보 누락 종목 수")
    missing_indicator_count: int = Field(..., description="지표 정보 누락 종목 수")
    data_quality_score: float = Field(..., ge=0, le=100, description="데이터 품질 점수")
    
    # 시스템 상태
    database_status: str = Field(..., description="데이터베이스 상태")
    api_status: str = Field(..., description="API 상태")
    
    class Config:
        from_attributes = True