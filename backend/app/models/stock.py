"""
주식 데이터 모델 - 무료 플랜 최적화
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Date, DECIMAL, BigInteger, Boolean, DateTime, Text, Index, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Stock(Base):
    """종목 마스터 테이블 - 상위 200개 종목만"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    market = Column(String(10), nullable=False)  # 'KOSPI' or 'KOSDAQ'
    sector = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)  # 업종
    market_cap = Column(BigInteger, nullable=True)
    listing_date = Column(Date, nullable=True)  # 상장일
    description = Column(Text, nullable=True)  # 종목 설명
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 현재가 정보 (자주 업데이트되는 데이터)
    price = Column(Float, nullable=True)
    change = Column(Float, nullable=True)  # 전일 대비 변화량
    change_percent = Column(Float, nullable=True)  # 전일 대비 변화율
    volume = Column(BigInteger, nullable=True)  # 거래량
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    prices = relationship("StockPrice", back_populates="stock")
    indicators = relationship("TechnicalIndicator", back_populates="stock")
    buy_signals = relationship("BuySignal", back_populates="stock")
    
    # 인덱스 최적화
    __table_args__ = (
        Index('idx_stocks_market_active', 'market', 'is_active'),
        Index('idx_stocks_market_cap', 'market_cap'),
        Index('idx_stocks_sector', 'sector'),
    )


class StockPrice(Base):
    """일별 주가 데이터 - API와 연동"""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # 주가 정보
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False) 
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # 변동률
    change_amount = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    stock = relationship("Stock", back_populates="prices")
    
    # 복합 인덱스 최적화
    __table_args__ = (
        Index('idx_stock_prices_stock_date', 'stock_id', 'date'),
        Index('idx_stock_prices_date', 'date'),
        # 유니크 제약조건
        Index('uk_stock_date', 'stock_id', 'date', unique=True),
    )


class TechnicalIndicator(Base):
    """기술적 지표 데이터"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # 기술적 지표
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    sma_20 = Column(Float, nullable=True)
    sma_60 = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    stock = relationship("Stock", back_populates="indicators")
    
    # 복합 인덱스 최적화
    __table_args__ = (
        Index('idx_indicators_stock_date', 'stock_id', 'date'),
        Index('idx_indicators_screening', 'date', 'rsi', 'macd', 'macd_signal'),
        # 유니크 제약조건
        Index('uk_indicator_stock_date', 'stock_id', 'date', unique=True),
    )


class BuySignal(Base):
    """매수 신호 데이터"""
    __tablename__ = "buy_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # 신호 정보
    signal_type = Column(String(50), nullable=False, default='rsi_oversold_macd_golden')
    signal_strength = Column(Float, nullable=False)  # 0-100
    reason = Column(Text, nullable=True)  # 신호 발생 이유
    
    # 신호 발생시 기술적 지표 값
    rsi = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    
    # 가격 정보
    price = Column(Float, nullable=False)  # 신호 발생 시점 가격
    volume = Column(BigInteger, nullable=True)
    
    # 메타 정보
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    stock = relationship("Stock", back_populates="buy_signals")
    
    # 인덱스 최적화
    __table_args__ = (
        Index('idx_buy_signals_stock_date', 'stock_id', 'date'),
        Index('idx_buy_signals_strength', 'signal_strength'),
        Index('idx_buy_signals_active', 'is_active', 'date'),
        # 중복 방지
        Index('uk_buy_signal_stock_date', 'stock_id', 'date', 'signal_type', unique=True),
    )


class MarketIndex(Base):
    """시장 지수 정보"""
    __tablename__ = "market_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)  # KOSPI, KOSDAQ
    name = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # 지수 값
    value = Column(Float, nullable=False)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_market_indices_code_date', 'code', 'date'),
        Index('uk_market_index_code_date', 'code', 'date', unique=True),
    )


class MarketSummary(Base):
    """시장 요약 정보 - 일별 통계 (레거시 호환)"""
    __tablename__ = "market_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    summary_date = Column(Date, nullable=False, unique=True, index=True)
    
    # 지수 정보
    kospi_index = Column(Float, nullable=True)
    kospi_change_pct = Column(Float, nullable=True)
    kosdaq_index = Column(Float, nullable=True)
    kosdaq_change_pct = Column(Float, nullable=True)
    
    # 신호 통계
    total_signals = Column(Integer, default=0)
    strong_signals = Column(Integer, default=0)  # signal_strength >= 80
    
    # 시장 통계
    rising_stocks = Column(Integer, default=0)
    declining_stocks = Column(Integer, default=0)
    
    # 메타 정보 (JSON 대신 간단한 텍스트)
    top_sectors = Column(Text, nullable=True)  # "반도체:5,자동차:3,화학:2"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_market_summary_date', 'summary_date'),
    )