"""
간단한 스크리닝 스키마 - pydantic v2 호환
"""
from typing import List
from datetime import datetime
from pydantic import BaseModel


class BuySignal(BaseModel):
    """매수 신호 정보 - 단순화"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    market_cap: float
    sector: str
    signal_strength: float
    rsi: float
    macd: float
    macd_signal: float
    reason: str
    date: str  # 간단하게 문자열로 처리