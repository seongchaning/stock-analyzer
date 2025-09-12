"""
스크리닝 분석 스크립트 - RSI 과매도 + MACD 골든크로스
"""
import sys
import os
from datetime import datetime, date, timedelta
import logging

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from app.core.database import engine
from app.models import Stock, TechnicalIndicator, BuySignal

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_signal_strength(rsi: float, macd: float, macd_signal: float, volume_ratio: float = 1.0) -> int:
    """신호 강도 계산 (1-100)"""
    try:
        strength = 0
        
        # RSI 점수 (40점 만점)
        if rsi <= 20:
            strength += 40  # 극도 과매도
        elif rsi <= 25:
            strength += 35
        elif rsi <= 30:
            strength += 30  # 과매도
        elif rsi <= 35:
            strength += 20
        
        # MACD 점수 (30점 만점)
        macd_diff = macd - macd_signal
        if macd_diff > 0:  # 골든크로스
            if macd_diff > macd_signal * 0.1:  # 강한 골든크로스
                strength += 30
            elif macd_diff > macd_signal * 0.05:
                strength += 25
            else:
                strength += 20
        
        # 거래량 점수 (20점 만점)
        if volume_ratio >= 2.0:
            strength += 20  # 거래량 급증
        elif volume_ratio >= 1.5:
            strength += 15
        elif volume_ratio >= 1.2:
            strength += 10
        elif volume_ratio >= 1.0:
            strength += 5
        
        # 추가 보정 (10점)
        if rsi <= 25 and macd_diff > 0:  # RSI 극도 과매도 + MACD 골든크로스
            strength += 10
        
        return min(strength, 100)  # 최대 100점
        
    except Exception as e:
        logger.error(f"신호 강도 계산 실패: {e}")
        return 0


def get_volume_ratio(symbol: str, current_volume: int, db) -> float:
    """최근 20일 평균 거래량 대비 비율"""
    try:
        # 최근 20일 평균 거래량 조회
        twenty_days_ago = date.today() - timedelta(days=30)
        
        avg_volume = db.query(DailyPrice.volume).filter(
            and_(
                DailyPrice.symbol == symbol,
                DailyPrice.trade_date >= twenty_days_ago,
                DailyPrice.trade_date < date.today()
            )
        ).limit(20).all()
        
        if not avg_volume:
            return 1.0
        
        avg_volume = sum([v[0] for v in avg_volume]) / len(avg_volume)
        return current_volume / avg_volume if avg_volume > 0 else 1.0
        
    except Exception as e:
        logger.error(f"거래량 비율 계산 실패: {e}")
        return 1.0


def run_screening() -> list:
    """스크리닝 실행"""
    db = SessionLocal()
    try:
        logger.info("🔍 스크리닝 분석 시작")
        
        # 오늘 날짜
        today = date.today()
        
        # 스크리닝 조건: RSI <= 30 AND MACD > MACD_SIGNAL
        query = db.query(TechnicalIndicator, Stock.name, Stock.sector, Stock.symbol, Stock.price).join(
            Stock, TechnicalIndicator.stock_id == Stock.id
        ).filter(
            and_(
                TechnicalIndicator.date == today,
                TechnicalIndicator.rsi.isnot(None),
                TechnicalIndicator.macd.isnot(None),
                TechnicalIndicator.macd_signal.isnot(None),
                TechnicalIndicator.rsi <= 30,  # RSI 과매도
                TechnicalIndicator.macd > TechnicalIndicator.macd_signal,  # MACD 골든크로스
                Stock.is_active == True
            )
        )
        
        candidates = query.all()
        logger.info(f"📋 스크리닝 조건 만족: {len(candidates)}개 종목")
        
        if not candidates:
            logger.info("조건을 만족하는 종목이 없습니다.")
            return []
        
        # 신호 강도 계산 및 정렬
        signals = []
        for indicator, stock_name, sector, symbol, price in candidates:
            try:
                # 거래량 비율 계산 (임시로 1.0으로 설정)
                volume_ratio = 1.0  # TODO: 실제 거래량 비율 계산 구현
                
                # 신호 강도 계산
                signal_strength = calculate_signal_strength(
                    rsi=float(indicator.rsi),
                    macd=float(indicator.macd),
                    macd_signal=float(indicator.macd_signal),
                    volume_ratio=volume_ratio
                )
                
                if signal_strength >= 50:  # 최소 신호 강도
                    signals.append({
                        'symbol': symbol,
                        'name': stock_name,
                        'sector': sector,
                        'signal_strength': signal_strength,
                        'entry_price': price or 0.0,
                        'rsi_value': float(indicator.rsi),
                        'macd_value': float(indicator.macd),
                        'macd_signal_value': float(indicator.macd_signal),
                        'volume_ratio': volume_ratio
                    })
                    
            except Exception as e:
                logger.error(f"❌ {symbol} 신호 처리 실패: {e}")
                continue
        
        # 신호 강도순 정렬
        signals.sort(key=lambda x: x['signal_strength'], reverse=True)
        
        logger.info(f"🎯 유효한 매수 신호: {len(signals)}개")
        
        # 상위 15개만 저장 (여유분 포함)
        return signals[:15]
        
    except Exception as e:
        logger.error(f"❌ 스크리닝 실행 실패: {e}")
        return []
    finally:
        db.close()


def save_screening_results(signals: list) -> None:
    """스크리닝 결과 저장"""
    db = SessionLocal()
    try:
        logger.info("💾 스크리닝 결과 저장 중...")
        
        today = date.today()
        saved_count = 0
        
        # 기존 오늘 결과 비활성화
        db.query(BuySignal).filter(BuySignal.date != today).update({'is_active': False})
        
        # 새 결과 저장
        for signal in signals:
            # 종목 ID 조회
            stock = db.query(Stock).filter(Stock.symbol == signal['symbol']).first()
            if not stock:
                continue
                
            # 기존 신호 확인
            existing_signal = db.query(BuySignal).filter(
                and_(
                    BuySignal.stock_id == stock.id,
                    BuySignal.date == today,
                    BuySignal.signal_type == 'rsi_oversold_macd_golden'
                )
            ).first()
            
            if existing_signal:
                # 기존 신호 업데이트
                existing_signal.signal_strength = signal['signal_strength']
                existing_signal.rsi = signal['rsi_value']
                existing_signal.macd = signal['macd_value']
                existing_signal.macd_signal = signal['macd_signal_value']
                existing_signal.price = signal['entry_price']
                existing_signal.is_active = True
            else:
                # 새 신호 생성
                buy_signal = BuySignal(
                    stock_id=stock.id,
                    date=today,
                    signal_type='rsi_oversold_macd_golden',
                    signal_strength=signal['signal_strength'],
                    reason=f"RSI 과매도({signal['rsi_value']:.1f}) + MACD 골든크로스",
                    rsi=signal['rsi_value'],
                    macd=signal['macd_value'],
                    macd_signal=signal['macd_signal_value'],
                    price=signal['entry_price'],
                    is_active=True
                )
                db.add(buy_signal)
            
            saved_count += 1
            
            logger.info(f"📊 {signal['symbol']} ({signal['name']}): {signal['signal_strength']}점")
        
        db.commit()
        logger.info(f"✅ 스크리닝 결과 저장 완료: {saved_count}개")
        
    except Exception as e:
        logger.error(f"❌ 스크리닝 결과 저장 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """메인 함수"""
    try:
        logger.info("🚀 스크리닝 분석 시작")
        start_time = datetime.now()
        
        # 스크리닝 실행
        signals = run_screening()
        
        if signals:
            # 결과 저장
            save_screening_results(signals)
            
            # 상위 10개 출력
            logger.info("🏆 오늘의 Top 10 매수 신호:")
            for i, signal in enumerate(signals[:10], 1):
                logger.info(
                    f"{i:2d}. {signal['symbol']} ({signal['name']}) "
                    f"- 강도: {signal['signal_strength']}점, "
                    f"RSI: {signal['rsi_value']:.1f}, "
                    f"거래량: {signal['volume_ratio']:.1f}배"
                )
        else:
            logger.info("📭 오늘은 조건을 만족하는 종목이 없습니다.")
        
        elapsed_time = datetime.now() - start_time
        logger.info(f"⏱️ 스크리닝 완료 (소요시간: {elapsed_time})")
        
    except Exception as e:
        logger.error(f"💥 스크리닝 분석 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()