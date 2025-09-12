"""
시장 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.market import MarketStatsResponse
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/stats", response_model=MarketStatsResponse)
async def get_market_stats(db: Session = Depends(get_db)):
    """
    시장 통계 정보 조회
    
    코스피/코스닥 지수, 매수 신호 통계, 섹터 분포 등을 제공합니다.
    """
    try:
        service = MarketService(db)
        stats = await service.get_market_stats()
        
        return MarketStatsResponse(
            data=stats,
            message="시장 통계 조회 완료",
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"시장 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/indices")
async def get_market_indices(db: Session = Depends(get_db)):
    """
    주요 지수 정보 조회 (코스피, 코스닥)
    """
    try:
        service = MarketService(db)
        indices = await service.get_market_indices()
        
        return {
            "data": indices,
            "message": "지수 정보 조회 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"지수 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/sectors")
async def get_sector_stats(db: Session = Depends(get_db)):
    """
    섹터별 통계 정보 조회
    """
    try:
        service = MarketService(db)
        sector_stats = await service.get_sector_stats()
        
        return {
            "data": sector_stats,
            "message": "섹터 통계 조회 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"섹터 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def market_health_check(db: Session = Depends(get_db)):
    """
    시장 데이터 상태 확인
    
    데이터 업데이트 시간, 활성 종목 수 등을 확인합니다.
    """
    try:
        service = MarketService(db)
        health = await service.get_data_health()
        
        return {
            "data": health,
            "message": "시장 데이터 상태 확인 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 상태 확인 중 오류가 발생했습니다: {str(e)}"
        )