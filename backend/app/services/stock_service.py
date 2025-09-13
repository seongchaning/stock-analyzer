"""
주식 서비스 - 종목 관련 비즈니스 로직
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func

from app.models import Stock, StockPrice, TechnicalIndicator
from app.schemas.stock_simple import StockDetail, ChartData, StockSearchResult


class StockService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_stock_detail(self, symbol: str) -> Optional[Dict[str, Any]]:
        """종목 상세 정보 조회"""
        
        stock = (
            self.db.query(Stock)
            .filter(Stock.symbol == symbol)
            .first()
        )
        
        if not stock:
            return None
        
        # 최신 가격 정보
        latest_price = (
            self.db.query(StockPrice)
            .filter(StockPrice.stock_id == stock.id)
            .order_by(desc(StockPrice.date))
            .first()
        )
        
        # 최신 기술적 지표
        latest_indicator = (
            self.db.query(TechnicalIndicator)
            .filter(TechnicalIndicator.stock_id == stock.id)
            .order_by(desc(TechnicalIndicator.date))
            .first()
        )
        
        # dict 형태로 반환
        return {
            "symbol": stock.symbol,
            "name": stock.name,
            "price": float(stock.price or 0.0),
            "change": float(stock.change or 0.0),
            "change_percent": float(stock.change_percent or 0.0),
            "volume": int(stock.volume or 0),
            "market_cap": float(stock.market_cap or 0),
            "sector": stock.sector or "기타",
            "industry": stock.industry,
            "listing_date": stock.listing_date,
            "description": stock.description,
            "current_rsi": float(latest_indicator.rsi) if latest_indicator and latest_indicator.rsi else None,
            "current_macd": float(latest_indicator.macd) if latest_indicator and latest_indicator.macd else None,
            "current_macd_signal": float(latest_indicator.macd_signal) if latest_indicator and latest_indicator.macd_signal else None,
        }
    
    async def get_chart_data(
        self,
        symbol: str,
        period: str = "6M"
    ) -> Optional[Dict[str, Any]]:
        """차트 데이터 조회"""
        
        stock = (
            self.db.query(Stock)
            .filter(Stock.symbol == symbol)
            .first()
        )
        
        if not stock:
            return None
        
        # 기간별 일수 계산
        days_map = {
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365
        }
        days = days_map.get(period, 180)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 가격 데이터 조회
        price_data = (
            self.db.query(StockPrice)
            .filter(
                and_(
                    StockPrice.stock_id == stock.id,
                    StockPrice.date >= start_date,
                    StockPrice.date <= end_date
                )
            )
            .order_by(StockPrice.date)
            .all()
        )
        
        # 기술적 지표 데이터 조회
        indicator_data = (
            self.db.query(TechnicalIndicator)
            .filter(
                and_(
                    TechnicalIndicator.stock_id == stock.id,
                    TechnicalIndicator.date >= start_date,
                    TechnicalIndicator.date <= end_date
                )
            )
            .order_by(TechnicalIndicator.date)
            .all()
        )
        
        # 데이터를 dict 형태로 변환하여 반환
        candles = []
        for price in price_data:
            candles.append({
                "date": price.date,
                "open": float(price.open),
                "high": float(price.high),
                "low": float(price.low),
                "close": float(price.close),
                "volume": int(price.volume)
            })
        
        indicators = []
        for indicator in indicator_data:
            indicators.append({
                "date": indicator.date,
                "rsi": float(indicator.rsi) if indicator.rsi else None,
                "macd": float(indicator.macd) if indicator.macd else None,
                "macd_signal": float(indicator.macd_signal) if indicator.macd_signal else None,
                "macd_histogram": float(indicator.macd_histogram) if indicator.macd_histogram else None,
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "candles": candles,
            "indicators": indicators
        }
    
    async def get_technical_indicators(
        self,
        symbol: str,
        period: str = "6M"
    ) -> List[Dict[str, Any]]:
        """기술적 지표 조회"""
        
        stock = (
            self.db.query(Stock)
            .filter(Stock.symbol == symbol)
            .first()
        )
        
        if not stock:
            return []
        
        # 기간별 일수 계산
        days_map = {
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365
        }
        days = days_map.get(period, 180)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        indicators = (
            self.db.query(TechnicalIndicator)
            .filter(
                and_(
                    TechnicalIndicator.stock_id == stock.id,
                    TechnicalIndicator.date >= start_date,
                    TechnicalIndicator.date <= end_date
                )
            )
            .order_by(TechnicalIndicator.date)
            .all()
        )
        
        # ORM 객체를 딕셔너리로 변환
        result = []
        for indicator in indicators:
            result.append({
                "date": indicator.date,
                "rsi": indicator.rsi,
                "macd": indicator.macd,
                "macd_signal": indicator.macd_signal,
                "macd_histogram": indicator.macd_histogram,
                "sma_20": indicator.sma_20,
                "sma_60": indicator.sma_60,
            })
        
        return result
    
    async def search_stocks(
        self,
        query: str,
        limit: int = 20
    ) -> List[StockSearchResult]:
        """종목 검색"""
        
        stocks = (
            self.db.query(Stock)
            .filter(
                or_(
                    Stock.name.ilike(f"%{query}%"),
                    Stock.symbol.ilike(f"%{query}%")
                )
            )
            .limit(limit)
            .all()
        )
        
        # ORM 객체를 Pydantic 모델로 변환
        result = []
        for stock in stocks:
            result.append(StockSearchResult(
                symbol=stock.symbol,
                name=stock.name,
                sector=stock.sector or "기타",
                market_type=stock.market
            ))
        
        return result
    
    async def get_stocks_list(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[StockSearchResult]:
        """전체 종목 리스트 조회 (시가총액 순)"""
        
        stocks = (
            self.db.query(Stock)
            .order_by(desc(Stock.market_cap))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # ORM 객체를 Pydantic 모델로 변환
        result = []
        for stock in stocks:
            result.append(StockSearchResult(
                symbol=stock.symbol,
                name=stock.name,
                sector=stock.sector or "기타",
                market_type=stock.market
            ))
        
        return result