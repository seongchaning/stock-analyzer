"""
시장 요약 정보 업데이트 스크립트
"""
import sys
import os
from datetime import datetime, date
import logging
from collections import Counter

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import FinanceDataReader as fdr
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from app.core.database import engine
from app.models.stock import Stock, StockPrice, BuySignal, MarketSummary

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_market_indices() -> dict:
    """코스피/코스닥 지수 정보 조회"""
    try:
        logger.info("📊 시장 지수 조회 중...")
        
        # 최근 거래일 데이터 조회 (최대 5일)
        from datetime import timedelta
        today = date.today()
        start_date = today - timedelta(days=5)
        
        # 코스피 지수
        kospi = fdr.DataReader('KS11', start=start_date, end=today)
        kospi_today = kospi.iloc[-1] if not kospi.empty else None
        
        # 코스닥 지수  
        kosdaq = fdr.DataReader('KQ11', start=start_date, end=today)
        kosdaq_today = kosdaq.iloc[-1] if not kosdaq.empty else None
        
        # 전일 대비 변동률 계산
        indices = {}
        
        if kospi_today is not None:
            kospi_prev = fdr.DataReader('KS11', start=date.today().replace(day=1), end=date.today())
            kospi_change = 0
            if len(kospi_prev) >= 2:
                kospi_change = ((kospi_today['Close'] - kospi_prev.iloc[-2]['Close']) / kospi_prev.iloc[-2]['Close']) * 100
            
            indices['kospi'] = {
                'index': float(kospi_today['Close']),
                'change_pct': round(kospi_change, 2)
            }
        
        if kosdaq_today is not None:
            kosdaq_prev = fdr.DataReader('KQ11', start=date.today().replace(day=1), end=date.today())
            kosdaq_change = 0
            if len(kosdaq_prev) >= 2:
                kosdaq_change = ((kosdaq_today['Close'] - kosdaq_prev.iloc[-2]['Close']) / kosdaq_prev.iloc[-2]['Close']) * 100
                
            indices['kosdaq'] = {
                'index': float(kosdaq_today['Close']),
                'change_pct': round(kosdaq_change, 2)
            }
        
        logger.info("✅ 시장 지수 조회 완료")
        return indices
        
    except Exception as e:
        logger.error(f"❌ 시장 지수 조회 실패: {e}")
        return {}


def get_market_statistics() -> dict:
    """시장 통계 조회"""
    db = SessionLocal()
    try:
        logger.info("📈 시장 통계 계산 중...")
        
        today = date.today()
        stats = {}
        
        # 전체 종목 변동 통계 (SQLite 호환)
        try:
            rising_count = db.query(func.count(StockPrice.id)).filter(
                StockPrice.date == today,
                StockPrice.change_percent > 0
            ).scalar() or 0
            
            declining_count = db.query(func.count(StockPrice.id)).filter(
                StockPrice.date == today,
                StockPrice.change_percent < 0
            ).scalar() or 0
            
            stats['rising_stocks'] = rising_count
            stats['declining_stocks'] = declining_count
        except Exception as e:
            logger.warning(f"주식 통계 계산 오류: {e}")
            stats['rising_stocks'] = 0
            stats['declining_stocks'] = 0
        
        # 신호 통계 (SQLite 호환)
        try:
            total_signals = db.query(func.count(BuySignal.id)).filter(
                BuySignal.date == today
            ).scalar() or 0
            
            strong_signals = db.query(func.count(BuySignal.id)).filter(
                BuySignal.date == today,
                BuySignal.signal_strength >= 80
            ).scalar() or 0
            
            stats['total_signals'] = total_signals
            stats['strong_signals'] = strong_signals
        except Exception as e:
            logger.warning(f"신호 통계 계산 오류: {e}")
            stats['total_signals'] = 0
            stats['strong_signals'] = 0
        
        # 섹터별 신호 분포
        sector_signals = db.query(Stock.sector, func.count(BuySignal.id)).join(
            BuySignal, Stock.id == BuySignal.stock_id
        ).filter(BuySignal.date == today).group_by(Stock.sector).all()
        
        # 상위 5개 섹터만
        sector_counter = Counter(dict(sector_signals))
        top_sectors = sector_counter.most_common(5)
        stats['top_sectors'] = ','.join([f"{sector}:{count}" for sector, count in top_sectors])
        
        logger.info("✅ 시장 통계 계산 완료")
        return stats
        
    except Exception as e:
        logger.error(f"❌ 시장 통계 계산 실패: {e}")
        return {}
    finally:
        db.close()


def update_market_summary(indices: dict, stats: dict) -> None:
    """시장 요약 정보 업데이트"""
    db = SessionLocal()
    try:
        logger.info("💾 시장 요약 정보 저장 중...")
        
        today = date.today()
        
        # 기존 데이터 확인
        existing = db.query(MarketSummary).filter(MarketSummary.summary_date == today).first()
        
        if existing:
            # 기존 데이터 업데이트
            if 'kospi' in indices:
                existing.kospi_index = indices['kospi']['index']
                existing.kospi_change_pct = indices['kospi']['change_pct']
            if 'kosdaq' in indices:
                existing.kosdaq_index = indices['kosdaq']['index']
                existing.kosdaq_change_pct = indices['kosdaq']['change_pct']
            
            existing.total_signals = stats.get('total_signals', 0)
            existing.strong_signals = stats.get('strong_signals', 0)
            existing.rising_stocks = stats.get('rising_stocks', 0)
            existing.declining_stocks = stats.get('declining_stocks', 0)
            existing.top_sectors = stats.get('top_sectors', '')
        else:
            # 새 데이터 생성
            market_summary = MarketSummary(
                summary_date=today,
                kospi_index=indices.get('kospi', {}).get('index'),
                kospi_change_pct=indices.get('kospi', {}).get('change_pct'),
                kosdaq_index=indices.get('kosdaq', {}).get('index'),
                kosdaq_change_pct=indices.get('kosdaq', {}).get('change_pct'),
                total_signals=stats.get('total_signals', 0),
                strong_signals=stats.get('strong_signals', 0),
                rising_stocks=stats.get('rising_stocks', 0),
                declining_stocks=stats.get('declining_stocks', 0),
                top_sectors=stats.get('top_sectors', '')
            )
            db.add(market_summary)
        
        db.commit()
        logger.info("✅ 시장 요약 정보 저장 완료")
        
        # 요약 출력
        if 'kospi' in indices:
            logger.info(f"📈 코스피: {indices['kospi']['index']:.2f} ({indices['kospi']['change_pct']:+.2f}%)")
        if 'kosdaq' in indices:
            logger.info(f"📈 코스닥: {indices['kosdaq']['index']:.2f} ({indices['kosdaq']['change_pct']:+.2f}%)")
        logger.info(f"📊 상승: {stats.get('rising_stocks', 0)}개, 하락: {stats.get('declining_stocks', 0)}개")
        logger.info(f"🎯 매수신호: {stats.get('total_signals', 0)}개 (강신호: {stats.get('strong_signals', 0)}개)")
        
    except Exception as e:
        logger.error(f"❌ 시장 요약 정보 저장 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """메인 함수"""
    try:
        logger.info("🚀 시장 요약 정보 업데이트 시작")
        start_time = datetime.now()
        
        # 1. 시장 지수 조회
        indices = get_market_indices()
        
        # 2. 시장 통계 계산
        stats = get_market_statistics()
        
        # 3. 시장 요약 정보 저장
        if indices or stats:
            update_market_summary(indices, stats)
        else:
            logger.warning("⚠️ 업데이트할 데이터가 없습니다.")
        
        elapsed_time = datetime.now() - start_time
        logger.info(f"⏱️ 시장 요약 업데이트 완료 (소요시간: {elapsed_time})")
        
    except Exception as e:
        logger.error(f"💥 시장 요약 업데이트 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()