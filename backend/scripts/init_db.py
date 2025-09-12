"""
데이터베이스 초기화 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, engine
from app.models import Stock, StockPrice, TechnicalIndicator, BuySignal, MarketIndex, MarketSummary


def create_tables():
    """테이블 생성"""
    print("📊 테이블 생성 중...")
    
    # 모든 테이블 생성
    init_db()
    
    print("✅ 테이블 생성 완료")
    print("생성된 테이블:")
    print("- stocks (종목 마스터)")
    print("- stock_prices (일별 주가)")
    print("- technical_indicators (기술적 지표)")
    print("- buy_signals (매수 신호)")
    print("- market_indices (시장 지수)")
    print("- market_summary (시장 요약)")


def insert_sample_data():
    """샘플 데이터 삽입 (개발용)"""
    from sqlalchemy.orm import sessionmaker
    from datetime import date, timedelta
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("📝 샘플 데이터 삽입 중...")
        
        # 샘플 종목 데이터
        sample_stocks = [
            Stock(
                symbol="005930", name="삼성전자", market="KOSPI", sector="반도체", 
                industry="반도체", market_cap=500000000000000,
                price=70500.0, change=1000.0, change_percent=1.44, volume=15000000
            ),
            Stock(
                symbol="000660", name="SK하이닉스", market="KOSPI", sector="반도체", 
                industry="반도체", market_cap=80000000000000,
                price=125000.0, change=-2500.0, change_percent=-1.96, volume=8000000
            ),
            Stock(
                symbol="035420", name="NAVER", market="KOSPI", sector="인터넷", 
                industry="인터넷 소프트웨어", market_cap=50000000000000,
                price=195000.0, change=5000.0, change_percent=2.63, volume=3000000
            ),
            Stock(
                symbol="005380", name="현대차", market="KOSPI", sector="자동차", 
                industry="완성차", market_cap=40000000000000,
                price=185000.0, change=-1000.0, change_percent=-0.54, volume=5000000
            ),
            Stock(
                symbol="035720", name="카카오", market="KOSPI", sector="인터넷", 
                industry="인터넷 플랫폼", market_cap=30000000000000,
                price=52000.0, change=1500.0, change_percent=2.97, volume=10000000
            ),
        ]
        
        for stock in sample_stocks:
            db.merge(stock)  # 중복시 업데이트
        
        db.commit()  # 종목 데이터 먼저 커밋
        
        # 삼성전자 ID 조회
        samsung = db.query(Stock).filter(Stock.symbol == "005930").first()
        
        if samsung:
            # 샘플 주가 데이터 (최근 7일)
            today = date.today()
            for i in range(7):
                trade_date = today - timedelta(days=i)
                
                sample_price = StockPrice(
                    stock_id=samsung.id,
                    date=trade_date,
                    open=70000.0,
                    high=71000.0,
                    low=69000.0,
                    close=70500.0,
                    volume=15000000,
                    change_amount=1000.0,
                    change_percent=1.44
                )
                db.merge(sample_price)
                
                # 샘플 기술적 지표
                sample_indicator = TechnicalIndicator(
                    stock_id=samsung.id,
                    date=trade_date,
                    rsi=28.5,  # 과매도 구간
                    macd=150.0,
                    macd_signal=100.0,
                    macd_histogram=50.0,
                    sma_20=69500.0,
                    sma_60=67800.0
                )
                db.merge(sample_indicator)
            
            # 샘플 매수 신호
            sample_signal = BuySignal(
                stock_id=samsung.id,
                date=today,
                signal_strength=85.0,
                reason="RSI 과매도(28.5) + MACD 골든크로스 발생",
                rsi=28.5,
                macd=150.0,
                macd_signal=100.0,
                price=70500.0,
                volume=15000000
            )
            db.merge(sample_signal)
        
        # 샘플 시장 지수
        kospi_index = MarketIndex(
            code="KOSPI",
            name="코스피",
            date=today,
            value=2615.51,
            change=22.15,
            change_percent=0.85
        )
        db.merge(kospi_index)
        
        kosdaq_index = MarketIndex(
            code="KOSDAQ",
            name="코스닥",
            date=today,
            value=871.23,
            change=-2.01,
            change_percent=-0.23
        )
        db.merge(kosdaq_index)
        
        # 샘플 시장 요약
        sample_market = MarketSummary(
            summary_date=today,
            kospi_index=2615.51,
            kospi_change_pct=0.85,
            kosdaq_index=871.23,
            kosdaq_change_pct=-0.23,
            total_signals=12,
            strong_signals=5,
            rising_stocks=95,
            declining_stocks=105,
            top_sectors="반도체:5,자동차:3,인터넷:2"
        )
        db.merge(sample_market)
        
        db.commit()
        print("✅ 샘플 데이터 삽입 완료")
        
    except Exception as e:
        print(f"❌ 샘플 데이터 삽입 실패: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """메인 함수"""
    print("🚀 데이터베이스 초기화 시작")
    
    try:
        # 테이블 생성
        create_tables()
        
        # 개발 환경에서만 샘플 데이터 삽입
        if os.getenv("ENVIRONMENT", "development") == "development":
            insert_sample_data()
        
        print("🎉 데이터베이스 초기화 완료!")
        
    except Exception as e:
        print(f"💥 초기화 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()