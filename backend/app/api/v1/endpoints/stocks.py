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
async def get_stocks_list(
    query: str = Query(None, description="검색어 (선택사항)"),
    limit: int = Query(50, ge=1, le=200, description="반환할 최대 종목 수"),
    offset: int = Query(0, ge=0, description="페이지 오프셋"),
    db: Session = Depends(get_db)
):
    """
    종목 리스트 조회 또는 검색
    
    - **query**: 검색어 (종목명 또는 종목코드, 선택사항)
    - **limit**: 반환할 최대 종목 수 (기본값: 50)
    - **offset**: 페이지 오프셋 (기본값: 0)
    """
    try:
        service = StockService(db)
        
        if query:
            # 검색 모드
            results = await service.search_stocks(query, limit)
            message = f"'{query}' 검색 결과 {len(results)}개"
        else:
            # 전체 리스트 조회
            results = await service.get_stocks_list(limit, offset)
            message = f"종목 리스트 {len(results)}개 조회"
        
        return {
            "data": results,
            "message": message,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"종목 조회 중 오류가 발생했습니다: {str(e)}"
        )