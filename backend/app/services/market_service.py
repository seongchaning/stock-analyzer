"""
시장 서비스 - 시장 통계 관련 비즈니스 로직
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.models import Stock, BuySignal, MarketIndex, TechnicalIndicator
from app.schemas.market import MarketStats, MarketIndex as MarketIndexSchema, DataHealth, SectorStats


class MarketService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_market_stats(self) -> MarketStats:
        """시장 통계 정보 조회"""
        
        # 코스피/코스닥 지수 조회
        kospi = (
            self.db.query(MarketIndex)
            .filter(MarketIndex.code == "KOSPI")
            .order_by(desc(MarketIndex.date))
            .first()
        )
        
        kosdaq = (
            self.db.query(MarketIndex)
            .filter(MarketIndex.code == "KOSDAQ")
            .order_by(desc(MarketIndex.date))
            .first()
        )
        
        # 매수 신호 통계
        total_signals = self.db.query(BuySignal).count()
        strong_signals = (
            self.db.query(BuySignal)
            .filter(BuySignal.signal_strength >= 80.0)
            .count()
        )
        
        # 섹터별 신호 분포
        sector_distribution = {}
        sector_query = (
            self.db.query(Stock.sector, func.count(BuySignal.id))
            .join(BuySignal)
            .group_by(Stock.sector)
            .order_by(desc(func.count(BuySignal.id)))
            .all()
        )
        
        for sector, count in sector_query:
            sector_distribution[sector] = count
        
        # 상위 섹터 (신호가 많은 순)
        top_sectors = [sector for sector, _ in sector_query[:5]]
        
        # 마지막 업데이트 시간
        last_signal = (
            self.db.query(BuySignal)
            .order_by(desc(BuySignal.created_at))
            .first()
        )
        last_updated = last_signal.created_at if last_signal else datetime.utcnow()
        
        return MarketStats(
            kospi_index=kospi.value if kospi else 0.0,
            kospi_change=kospi.change if kospi else 0.0,
            kosdaq_index=kosdaq.value if kosdaq else 0.0,
            kosdaq_change=kosdaq.change if kosdaq else 0.0,
            signal_count=total_signals,
            strong_signal_count=strong_signals,
            top_sectors=top_sectors,
            sector_distribution=sector_distribution,
            last_updated=last_updated
        )
    
    async def get_market_indices(self) -> List[MarketIndexSchema]:
        """주요 지수 정보 조회"""
        
        indices = (
            self.db.query(MarketIndex)
            .filter(MarketIndex.code.in_(["KOSPI", "KOSDAQ"]))
            .order_by(desc(MarketIndex.date))
            .limit(2)
            .all()
        )
        
        # ORM 객체를 Pydantic 모델로 변환
        result = []
        for index in indices:
            result.append(MarketIndexSchema(
                code=index.code,
                name=index.name,
                value=index.value,
                change=index.change or 0.0,
                change_percent=index.change_percent or 0.0,
                date=index.date
            ))
        
        return result
    
    async def get_sector_stats(self) -> List[SectorStats]:
        """섹터별 통계 조회"""
        
        # 섹터별 기본 통계
        sector_stats = (
            self.db.query(
                Stock.sector,
                func.count(Stock.id).label('stock_count'),
                func.count(BuySignal.id).label('signal_count'),
                func.avg(Stock.change_percent).label('avg_change_percent'),
                func.sum(Stock.market_cap).label('total_market_cap')
            )
            .outerjoin(BuySignal, BuySignal.stock_id == Stock.id)
            .group_by(Stock.sector)
            .all()
        )
        
        # 전체 시가총액 계산
        total_market_cap = self.db.query(func.sum(Stock.market_cap)).scalar() or 0
        
        results = []
        for stat in sector_stats:
            market_cap_ratio = (stat.total_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0
            
            results.append(SectorStats(
                sector=stat.sector or "기타",
                stock_count=stat.stock_count,
                signal_count=stat.signal_count or 0,
                avg_change_percent=float(stat.avg_change_percent or 0),
                market_cap_ratio=market_cap_ratio
            ))
        
        return sorted(results, key=lambda x: x.signal_count, reverse=True)
    
    async def get_data_health(self) -> DataHealth:
        """데이터 상태 확인"""
        
        # 전체/활성 종목 수
        total_stocks = self.db.query(Stock).count()
        
        # 최근 7일 이내 데이터가 있는 종목
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_stocks = (
            self.db.query(Stock)
            .filter(Stock.updated_at >= seven_days_ago)
            .count()
        )
        
        # 마지막 데이터 업데이트
        last_update = (
            self.db.query(func.max(Stock.updated_at))
            .scalar()
        ) or datetime.utcnow()
        
        # 데이터 신선도 (시간 단위)
        data_freshness = (datetime.utcnow() - last_update).total_seconds() / 3600
        
        # 데이터 품질 지표
        missing_price_count = (
            self.db.query(Stock)
            .filter(Stock.price.is_(None))
            .count()
        )
        
        missing_indicator_count = (
            self.db.query(Stock)
            .outerjoin(TechnicalIndicator)
            .filter(TechnicalIndicator.id.is_(None))
            .count()
        )
        
        # 데이터 품질 점수 계산
        quality_score = 100.0
        if total_stocks > 0:
            price_quality = (1 - missing_price_count / total_stocks) * 50
            indicator_quality = (1 - missing_indicator_count / total_stocks) * 30
            freshness_quality = max(0, (24 - data_freshness) / 24) * 20
            quality_score = price_quality + indicator_quality + freshness_quality
        
        # 데이터베이스 및 API 상태 판정
        db_status = "healthy" if quality_score > 70 else "warning" if quality_score > 50 else "error"
        api_status = "healthy" if data_freshness < 24 else "warning" if data_freshness < 48 else "error"
        
        return DataHealth(
            total_stocks=total_stocks,
            active_stocks=active_stocks,
            last_data_update=last_update,
            data_freshness_hours=round(data_freshness, 2),
            missing_price_count=missing_price_count,
            missing_indicator_count=missing_indicator_count,
            data_quality_score=round(quality_score, 2),
            database_status=db_status,
            api_status=api_status
        )