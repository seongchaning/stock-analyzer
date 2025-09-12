"""
주식 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.stock_simple import StockDetail, ChartData
from app.services.stock_service import StockService

router = APIRouter()


@router.get("/{symbol}", response_model=StockDetail)
async def get_stock_detail(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    종목 상세 정보 조회
    
    - **symbol**: 종목 코드 (예: "005930")
    """
    try:
        service = StockService(db)
        stock_detail = await service.get_stock_detail(symbol)
        
        if not stock_detail:
            raise HTTPException(
                status_code=404,
                detail=f"종목 {symbol}을(를) 찾을 수 없습니다."
            )
        
        return stock_detail
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"종목 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{symbol}/chart", response_model=ChartData)
async def get_chart_data(
    symbol: str,
    period: str = Query("6M", regex="^(1M|3M|6M|1Y)$"),
    db: Session = Depends(get_db)
):
    """
    종목 차트 데이터 조회
    
    - **symbol**: 종목 코드 (예: "005930")
    - **period**: 조회 기간 (1M, 3M, 6M, 1Y)
    """
    try:
        service = StockService(db)
        chart_data = await service.get_chart_data(symbol, period)
        
        if not chart_data:
            raise HTTPException(
                status_code=404,
                detail=f"종목 {symbol}의 차트 데이터를 찾을 수 없습니다."
            )
        
        return ChartDataResponse(
            data=chart_data,
            message=f"{symbol} 종목 {period} 차트 데이터 조회 완료",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"차트 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    period: str = Query("6M", regex="^(1M|3M|6M|1Y)$"),
    db: Session = Depends(get_db)
):
    """
    종목 기술적 지표 조회
    
    - **symbol**: 종목 코드 (예: "005930")
    - **period**: 조회 기간 (1M, 3M, 6M, 1Y)
    """
    try:
        service = StockService(db)
        indicators = await service.get_technical_indicators(symbol, period)
        
        return {
            "data": indicators,
            "message": f"{symbol} 종목 기술적 지표 조회 완료",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"기술적 지표 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/")
async def search_stocks(
    query: str = Query(..., min_length=1, description="검색어"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 종목 수"),
    db: Session = Depends(get_db)
):
    """
    종목 검색
    
    - **query**: 검색어 (종목명 또는 종목코드)
    - **limit**: 반환할 최대 종목 수 (기본값: 20)
    """
    try:
        service = StockService(db)
        results = await service.search_stocks(query, limit)
        
        return {
            "data": results,
            "message": f"'{query}' 검색 결과 {len(results)}개",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"종목 검색 중 오류가 발생했습니다: {str(e)}"
        )