"""
스크리닝 서비스 - 매수 신호 관련 비즈니스 로직
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.models import Stock, TechnicalIndicator, BuySignal
from app.schemas.screening_simple import BuySignal as BuySignalSchema


class ScreeningService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_buy_signals(
        self,
        limit: int = 10,
        sector: Optional[str] = None,
        min_signal_strength: float = 50.0
    ) -> List[BuySignalSchema]:
        """매수 신호 목록 조회"""
        
        query = (
            self.db.query(BuySignal)
            .join(Stock, BuySignal.stock_id == Stock.id)
            .filter(
                and_(
                    BuySignal.signal_strength >= min_signal_strength,
                    BuySignal.is_active == True
                )
            )
        )
        
        if sector:
            query = query.filter(Stock.sector == sector)
        
        signals = (
            query
            .order_by(desc(BuySignal.signal_strength))
            .limit(limit)
            .all()
        )
        
        # ORM 객체를 Pydantic 스키마로 변환
        result = []
        for signal in signals:
            buy_signal_schema = BuySignalSchema(
                symbol=signal.stock.symbol,
                name=signal.stock.name,
                price=signal.stock.price or 0.0,
                change=signal.stock.change or 0.0,
                change_percent=signal.stock.change_percent or 0.0,
                market_cap=signal.stock.market_cap or 0,
                sector=signal.stock.sector or "기타",
                signal_strength=signal.signal_strength,
                rsi=signal.rsi,
                macd=signal.macd,
                macd_signal=signal.macd_signal,
                reason=signal.reason,
                date=str(signal.date)
            )
            result.append(buy_signal_schema)
        
        return result
    
    def _build_stock_info(self, stock: Stock):
        """Stock ORM 객체를 StockInfo 스키마로 변환"""
        from app.schemas.screening import StockInfo
        
        return StockInfo(
            symbol=stock.symbol,
            name=stock.name,
            price=stock.price or 0.0,
            change=stock.change or 0.0,
            change_percent=stock.change_percent or 0.0,
            market_cap=stock.market_cap or 0,
            sector=stock.sector or "기타"
        )
    
    async def get_signal_history(
        self,
        symbol: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """특정 종목의 신호 이력 조회"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        history = (
            self.db.query(BuySignal)
            .join(Stock, BuySignal.stock_id == Stock.id)
            .filter(
                and_(
                    Stock.symbol == symbol,
                    BuySignal.date >= start_date.date(),
                    BuySignal.date <= end_date.date()
                )
            )
            .order_by(desc(BuySignal.date))
            .all()
        )
        
        # ORM 객체를 딕셔너리로 변환
        result = []
        for signal in history:
            result.append({
                "date": signal.date,
                "signal_type": signal.signal_type,
                "signal_strength": signal.signal_strength,
                "rsi": signal.rsi,
                "macd": signal.macd,
                "price": signal.price,
            })
        
        return result
    
    async def get_screening_stats(self):
        """스크리닝 통계 조회"""
        
        # 활성 신호만 대상
        active_signals_query = self.db.query(BuySignal).filter(BuySignal.is_active == True)
        
        # 총 신호 개수
        total_signals = active_signals_query.count()
        
        # 강한 신호 개수 (80점 이상)
        strong_signals = (
            active_signals_query
            .filter(BuySignal.signal_strength >= 80.0)
            .count()
        )
        
        # 섹터별 분포
        sector_distribution = {}
        sector_query = (
            self.db.query(Stock.sector, func.count(BuySignal.id))
            .join(Stock, BuySignal.stock_id == Stock.id)
            .filter(BuySignal.is_active == True)
            .group_by(Stock.sector)
            .all()
        )
        
        for sector, count in sector_query:
            sector_distribution[sector] = count
        
        # 평균 신호 강도
        avg_strength_result = (
            active_signals_query
            .with_entities(func.avg(BuySignal.signal_strength))
            .scalar()
        )
        avg_signal_strength = float(avg_strength_result or 0)
        
        # 마지막 업데이트 시간
        last_signal = (
            active_signals_query
            .order_by(desc(BuySignal.updated_at))
            .first()
        )
        last_updated = last_signal.updated_at if last_signal else datetime.utcnow()
        
        return {
            "total_signals": total_signals,
            "strong_signals": strong_signals,
            "sector_distribution": sector_distribution,
            "avg_signal_strength": avg_signal_strength,
            "last_updated": last_updated
        }