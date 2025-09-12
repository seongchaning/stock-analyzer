"""
스크리닝 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.screening_simple import BuySignal
from app.services.screening_service import ScreeningService

router = APIRouter()


@router.get("/signals")
async def get_buy_signals(
    limit: int = 10,
    sector: str = None,
    min_signal_strength: float = 50.0,
    db: Session = Depends(get_db)
):
    """
    매수 신호 목록 조회
    
    - **limit**: 반환할 최대 종목 수 (기본값: 10)
    - **sector**: 섹터 필터 (선택사항)
    - **min_signal_strength**: 최소 신호 강도 (기본값: 50.0)
    """
    try:
        service = ScreeningService(db)
        signals = await service.get_buy_signals(
            limit=limit,
            sector=sector,
            min_signal_strength=min_signal_strength
        )
        
        return {
            "data": signals,
            "message": f"{len(signals)}개의 매수 신호 조회 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"매수 신호 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/signals/history")
async def get_signal_history(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    특정 종목의 신호 이력 조회
    
    - **symbol**: 종목 코드 (예: "005930")
    - **days**: 조회할 기간 (기본값: 30일)
    """
    try:
        service = ScreeningService(db)
        history = await service.get_signal_history(symbol, days)
        
        return {
            "data": history,
            "message": f"{symbol} 종목의 {days}일간 신호 이력",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"신호 이력 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/stats")
async def get_screening_stats(db: Session = Depends(get_db)):
    """
    스크리닝 통계 정보
    """
    try:
        service = ScreeningService(db)
        stats = await service.get_screening_stats()
        
        return {
            "data": stats,
            "message": "스크리닝 통계 조회 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )