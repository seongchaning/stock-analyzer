"""
시장 지수 데이터 수집 스크립트
"""
import sys
import os
from datetime import datetime, date, timedelta
import logging

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import FinanceDataReader as fdr
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.models import MarketIndex

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def collect_market_index(index_code: str, index_name: str, days: int = 30) -> None:
    """시장 지수 데이터 수집"""
    db = SessionLocal()
    try:
        logger.info(f"📈 {index_name}({index_code}) 데이터 수집 중...")
        
        # 지수 데이터 수집
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # FinanceDataReader로 지수 데이터 수집
        df = fdr.DataReader(index_code, start=start_date, end=end_date)
        
        if df.empty:
            logger.warning(f"⚠️ {index_code}: 지수 데이터 없음")
            return
        
        # 인덱스를 컬럼으로 변환
        df = df.reset_index()
        
        # 변화량 계산
        df['Change'] = df['Close'].diff()
        df['Change_Pct'] = df['Close'].pct_change() * 100
        
        saved_count = 0
        for _, row in df.iterrows():
            trade_date = row['Date'].date()
            
            # 기존 데이터 확인
            existing = db.query(MarketIndex).filter(
                MarketIndex.code == index_code,
                MarketIndex.date == trade_date
            ).first()
            
            if existing:
                # 기존 데이터 업데이트
                existing.value = float(row['Close'])
                existing.change = float(row['Change']) if pd.notna(row['Change']) else None
                existing.change_percent = float(row['Change_Pct']) if pd.notna(row['Change_Pct']) else None
                existing.volume = int(row['Volume']) if 'Volume' in row and pd.notna(row['Volume']) else None
            else:
                # 새 데이터 추가
                market_index = MarketIndex(
                    code=index_code,
                    name=index_name,
                    date=trade_date,
                    value=float(row['Close']),
                    change=float(row['Change']) if pd.notna(row['Change']) else None,
                    change_percent=float(row['Change_Pct']) if pd.notna(row['Change_Pct']) else None,
                    volume=int(row['Volume']) if 'Volume' in row and pd.notna(row['Volume']) else None
                )
                db.add(market_index)
            
            saved_count += 1
        
        db.commit()
        logger.info(f"✅ {index_name}: {saved_count}개 데이터 저장 완료")
        
    except Exception as e:
        logger.error(f"❌ {index_code} 지수 데이터 수집 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """메인 함수"""
    try:
        logger.info("🚀 시장 지수 데이터 수집 시작")
        start_time = datetime.now()
        
        # 주요 지수 수집
        indices = [
            ("KS11", "코스피"),  # KOSPI
            ("KQ11", "코스닥")   # KOSDAQ
        ]
        
        for index_code, index_name in indices:
            try:
                collect_market_index(index_code, index_name, days=30)
            except Exception as e:
                logger.error(f"❌ {index_name} 수집 실패: {e}")
                continue
        
        elapsed_time = datetime.now() - start_time
        logger.info(f"🎉 시장 지수 데이터 수집 완료! 소요시간: {elapsed_time}")
        
    except Exception as e:
        logger.error(f"💥 시장 지수 수집 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()