"""
API v1 라우터 - 모든 엔드포인트 통합
"""
from fastapi import APIRouter

from app.api.v1.endpoints import screening, stocks, market

api_router = APIRouter()

# 각 도메인별 라우터 등록
api_router.include_router(
    screening.router, 
    prefix="/screening", 
    tags=["screening"]
)

api_router.include_router(
    stocks.router, 
    prefix="/stocks", 
    tags=["stocks"]
)

api_router.include_router(
    market.router, 
    prefix="/market", 
    tags=["market"]
)