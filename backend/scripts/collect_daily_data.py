"""
일별 주식 데이터 수집 스크립트 - 무료 플랜 최적화
"""
import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict
import logging

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import FinanceDataReader as fdr
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.models import Stock, StockPrice, TechnicalIndicator, MarketIndex
from app.core.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_top_stocks(limit: int = 200) -> List[Dict]:
    """시가총액 상위 종목 리스트 가져오기"""
    try:
        logger.info(f"📈 시가총액 상위 {limit}개 종목 조회 중...")
        
        # KRX 전체 종목 정보
        stocks_df = fdr.StockListing('KRX')
        
        # 시가총액 상위 종목 선별
        stocks_df = stocks_df.dropna(subset=['Market'])
        stocks_df = stocks_df[stocks_df['Market'].isin(['KOSPI', 'KOSDAQ'])]
        stocks_df = stocks_df.nlargest(limit, 'Marcap')
        
        stocks_list = []
        for _, row in stocks_df.iterrows():
            stocks_list.append({
                'symbol': row['Code'],
                'name': row['Name'],
                'market': row['Market'],
                'sector': row.get('Sector', '기타'),
                'industry': row.get('Industry', '기타'),
                'market_cap': int(row['Marcap']) if pd.notna(row['Marcap']) else None
            })
        
        logger.info(f"✅ {len(stocks_list)}개 종목 조회 완료")
        return stocks_list
        
    except Exception as e:
        logger.error(f"❌ 종목 리스트 조회 실패: {e}")
        raise


def update_stocks_master(stocks_list: List[Dict]) -> None:
    """종목 마스터 테이블 업데이트"""
    db = SessionLocal()
    try:
        logger.info("📝 종목 마스터 테이블 업데이트 중...")
        
        updated_count = 0
        for stock_info in stocks_list:
            stock = db.query(Stock).filter(Stock.symbol == stock_info['symbol']).first()
            
            if stock:
                # 기존 종목 업데이트
                stock.name = stock_info['name']
                stock.market = stock_info['market']
                stock.sector = stock_info['sector']
                stock.industry = stock_info['industry']
                stock.market_cap = stock_info['market_cap']
                stock.is_active = True
            else:
                # 새 종목 추가
                stock = Stock(
                    symbol=stock_info['symbol'],
                    name=stock_info['name'],
                    market=stock_info['market'],
                    sector=stock_info['sector'],
                    industry=stock_info['industry'],
                    market_cap=stock_info['market_cap'],
                    is_active=True
                )
                db.add(stock)
            
            updated_count += 1
        
        # 상위 종목에서 제외된 종목들 비활성화
        active_symbols = [s['symbol'] for s in stocks_list]
        db.query(Stock).filter(~Stock.symbol.in_(active_symbols)).update({'is_active': False})
        
        db.commit()
        logger.info(f"✅ 종목 마스터 업데이트 완료: {updated_count}개")
        
    except Exception as e:
        logger.error(f"❌ 종목 마스터 업데이트 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """기술적 지표 계산"""
    try:
        # RSI 계산 (14일)
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        df['rsi'] = calculate_rsi(df['Close'])
        
        # MACD 계산
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # 이동평균
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_60'] = df['Close'].rolling(window=60).mean()
        
        # 변동률 계산
        df['change_amount'] = df['Close'].diff()
        df['change_percent'] = df['Close'].pct_change() * 100
        
        return df
        
    except Exception as e:
        logger.error(f"❌ 기술적 지표 계산 실패: {e}")
        raise


def collect_stock_data(symbol: str, days: int = 200) -> pd.DataFrame:
    """개별 종목 데이터 수집"""
    try:
        # 과거 데이터 수집 (6개월 + 여유분)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # FinanceDataReader로 데이터 수집
        df = fdr.DataReader(symbol, start=start_date, end=end_date)
        
        if df.empty:
            logger.warning(f"⚠️ {symbol}: 데이터 없음")
            return pd.DataFrame()
        
        # 인덱스를 컬럼으로 변환
        df = df.reset_index()
        
        # 기술적 지표 계산
        df = calculate_technical_indicators(df)
        
        # 6개월만 유지 (최근 180일)
        df = df.tail(180)
        
        return df
        
    except Exception as e:
        logger.error(f"❌ {symbol} 데이터 수집 실패: {e}")
        return pd.DataFrame()


def save_stock_data(symbol: str, df: pd.DataFrame) -> None:
    """주가 및 기술적 지표 데이터 저장"""
    db = SessionLocal()
    try:
        # 종목 정보 조회
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.warning(f"⚠️ {symbol}: 종목 정보 없음")
            return
        
        saved_price_count = 0
        saved_indicator_count = 0
        
        for _, row in df.iterrows():
            trade_date = row['Date'].date()
            
            # 주가 데이터 저장/업데이트
            existing_price = db.query(StockPrice).filter(
                StockPrice.stock_id == stock.id,
                StockPrice.date == trade_date
            ).first()
            
            if existing_price:
                # 기존 데이터 업데이트
                existing_price.open = float(row['Open'])
                existing_price.high = float(row['High'])
                existing_price.low = float(row['Low'])
                existing_price.close = float(row['Close'])
                existing_price.volume = int(row['Volume'])
                existing_price.change_amount = float(row['change_amount']) if pd.notna(row['change_amount']) else None
                existing_price.change_percent = float(row['change_percent']) if pd.notna(row['change_percent']) else None
            else:
                # 새 주가 데이터 추가
                stock_price = StockPrice(
                    stock_id=stock.id,
                    date=trade_date,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    change_amount=float(row['change_amount']) if pd.notna(row['change_amount']) else None,
                    change_percent=float(row['change_percent']) if pd.notna(row['change_percent']) else None
                )
                db.add(stock_price)
            
            saved_price_count += 1
            
            # 기술적 지표 저장/업데이트
            existing_indicator = db.query(TechnicalIndicator).filter(
                TechnicalIndicator.stock_id == stock.id,
                TechnicalIndicator.date == trade_date
            ).first()
            
            if existing_indicator:
                # 기존 지표 업데이트
                existing_indicator.rsi = float(row['rsi']) if pd.notna(row['rsi']) else None
                existing_indicator.macd = float(row['macd']) if pd.notna(row['macd']) else None
                existing_indicator.macd_signal = float(row['macd_signal']) if pd.notna(row['macd_signal']) else None
                existing_indicator.macd_histogram = float(row['macd_histogram']) if pd.notna(row['macd_histogram']) else None
                existing_indicator.sma_20 = float(row['sma_20']) if pd.notna(row['sma_20']) else None
                existing_indicator.sma_60 = float(row['sma_60']) if pd.notna(row['sma_60']) else None
            else:
                # 새 지표 데이터 추가
                indicator = TechnicalIndicator(
                    stock_id=stock.id,
                    date=trade_date,
                    rsi=float(row['rsi']) if pd.notna(row['rsi']) else None,
                    macd=float(row['macd']) if pd.notna(row['macd']) else None,
                    macd_signal=float(row['macd_signal']) if pd.notna(row['macd_signal']) else None,
                    macd_histogram=float(row['macd_histogram']) if pd.notna(row['macd_histogram']) else None,
                    sma_20=float(row['sma_20']) if pd.notna(row['sma_20']) else None,
                    sma_60=float(row['sma_60']) if pd.notna(row['sma_60']) else None
                )
                db.add(indicator)
            
            saved_indicator_count += 1
        
        # 종목의 현재가 정보 업데이트 (최신 데이터 기준)
        if not df.empty:
            latest_row = df.iloc[-1]
            stock.price = float(latest_row['Close'])
            stock.change = float(latest_row['change_amount']) if pd.notna(latest_row['change_amount']) else 0.0
            stock.change_percent = float(latest_row['change_percent']) if pd.notna(latest_row['change_percent']) else 0.0
            stock.volume = int(latest_row['Volume'])
        
        db.commit()
        logger.info(f"✅ {symbol}: 주가 {saved_price_count}개, 지표 {saved_indicator_count}개 저장 완료")
        
    except Exception as e:
        logger.error(f"❌ {symbol} 데이터 저장 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """메인 함수"""
    try:
        logger.info("🚀 일별 주식 데이터 수집 시작")
        start_time = datetime.now()
        
        # 1. 상위 종목 리스트 가져오기
        stocks_list = get_top_stocks(settings.MAX_STOCKS)
        
        # 2. 종목 마스터 업데이트
        update_stocks_master(stocks_list)
        
        # 3. 개별 종목 데이터 수집
        success_count = 0
        fail_count = 0
        
        for i, stock_info in enumerate(stocks_list):
            symbol = stock_info['symbol']
            logger.info(f"📊 {i+1}/{len(stocks_list)} - {symbol} ({stock_info['name']}) 수집 중...")
            
            try:
                df = collect_stock_data(symbol)
                if not df.empty:
                    save_stock_data(symbol, df)
                    success_count += 1
                else:
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"❌ {symbol} 처리 실패: {e}")
                fail_count += 1
                continue
        
        # 완료 통계
        elapsed_time = datetime.now() - start_time
        logger.info(f"🎉 데이터 수집 완료!")
        logger.info(f"성공: {success_count}개, 실패: {fail_count}개")
        logger.info(f"소요 시간: {elapsed_time}")
        
        if fail_count > success_count * 0.1:  # 실패율 10% 초과시 경고
            logger.warning(f"⚠️ 실패율이 높습니다: {fail_count/len(stocks_list)*100:.1f}%")
        
    except Exception as e:
        logger.error(f"💥 데이터 수집 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()