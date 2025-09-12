"""
주식 서비스 - 종목 관련 비즈니스 로직
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func

from app.models import Stock, StockPrice, TechnicalIndicator
from app.schemas.stock import StockDetail, ChartData, StockSearchResult


class StockService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_stock_detail(self, symbol: str) -> Optional[StockDetail]:
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
        
        # ORM 객체를 Pydantic 모델로 변환
        return StockDetail(
            symbol=stock.symbol,
            name=stock.name,
            price=stock.price or 0.0,
            change=stock.change or 0.0,
            change_percent=stock.change_percent or 0.0,
            volume=stock.volume or 0,
            market_cap=stock.market_cap or 0,
            sector=stock.sector or "기타",
            industry=stock.industry,
            listing_date=stock.listing_date,
            description=stock.description,
            current_rsi=latest_indicator.rsi if latest_indicator else None,
            current_macd=latest_indicator.macd if latest_indicator else None,
            current_macd_signal=latest_indicator.macd_signal if latest_indicator else None,
        )
    
    async def get_chart_data(
        self,
        symbol: str,
        period: str = "6M"
    ) -> Optional[ChartData]:
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
        
        # ORM 객체를 Pydantic 모델로 변환
        from app.schemas.stock import CandleData, TechnicalIndicator as TechnicalIndicatorSchema
        
        # 가격 데이터 변환
        candles = []
        for price in price_data:
            candles.append(CandleData(
                date=price.date,
                open=price.open,
                high=price.high,
                low=price.low,
                close=price.close,
                volume=price.volume
            ))
        
        # 기술적 지표 데이터 변환
        indicators = []
        for indicator in indicator_data:
            indicators.append(TechnicalIndicatorSchema(
                date=indicator.date,
                rsi=indicator.rsi,
                macd=indicator.macd,
                macd_signal=indicator.macd_signal,
                macd_histogram=indicator.macd_histogram,
            ))
        
        return ChartData(
            symbol=symbol,
            period=period,
            candles=candles,
            indicators=indicators
        )
    
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