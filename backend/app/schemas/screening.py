"""
스크리닝 관련 스키마
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class StockInfo(BaseModel):
    """종목 기본 정보"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    price: float = Field(..., description="현재가")
    change: float = Field(..., description="전일 대비 변화량")
    change_percent: float = Field(..., description="전일 대비 변화율 (%)")
    market_cap: float = Field(..., description="시가총액")
    sector: str = Field(..., description="섹터")
    
    model_config = {"from_attributes": True}


class BuySignal(BaseModel):
    """매수 신호 정보"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    price: float = Field(..., description="현재가")
    change: float = Field(..., description="전일 대비 변화량")
    change_percent: float = Field(..., description="전일 대비 변화율 (%)")
    market_cap: float = Field(..., description="시가총액")
    sector: str = Field(..., description="섹터")
    signal_strength: float = Field(..., ge=0, le=100, description="신호 강도 (0-100)")
    rsi: float = Field(..., description="RSI 값")
    macd: float = Field(..., description="MACD 값")
    macd_signal: float = Field(..., description="MACD 신호선")
    reason: str = Field(..., description="신호 발생 이유")
    date: datetime = Field(..., description="신호 발생 일시")
    
    model_config = {"from_attributes": True}


class BuySignalResponse(BaseResponse[BuySignal]):
    """매수 신호 단일 응답"""
    pass


class SignalListResponse(BaseResponse[List[BuySignal]]):
    """매수 신호 목록 응답"""
    pass


class SignalHistory(BaseModel):
    """신호 이력 정보"""
    date: datetime = Field(..., description="날짜")
    signal_type: str = Field(..., description="신호 타입")
    signal_strength: float = Field(..., description="신호 강도")
    rsi: float = Field(..., description="RSI 값")
    macd: float = Field(..., description="MACD 값")
    price: float = Field(..., description="해당 일자 종가")
    
    model_config = {"from_attributes": True}


class ScreeningStats(BaseModel):
    """스크리닝 통계"""
    total_signals: int = Field(..., description="총 신호 개수")
    strong_signals: int = Field(..., description="강한 신호 개수 (80점 이상)")
    sector_distribution: dict = Field(..., description="섹터별 신호 분포")
    avg_signal_strength: float = Field(..., description="평균 신호 강도")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    
    model_config = {"from_attributes": True}