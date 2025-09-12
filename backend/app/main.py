"""
FastAPI 메인 애플리케이션 - 무료 플랜 최적화
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.database import init_db


# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작시 초기화
    logger.info("🚀 Stock Analyzer 시작")
    logger.info(f"환경: {settings.ENVIRONMENT}")
    logger.info(f"디버그 모드: {settings.DEBUG}")
    
    try:
        # 데이터베이스 초기화
        init_db()
        logger.info("✅ 데이터베이스 초기화 완료")
        
        # Sentry 초기화 (선택사항)
        if settings.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration(auto_enable=True)],
                traces_sample_rate=0.1,  # 샘플링으로 무료 할당량 절약
                environment=settings.ENVIRONMENT
            )
            logger.info("✅ Sentry 초기화 완료")
            
    except Exception as e:
        logger.error(f"❌ 초기화 실패: {e}")
        raise
    
    yield
    
    # 종료시 정리
    logger.info("🛑 Stock Analyzer 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="한국 주식 기술적 분석 서비스 - 무료 버전",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Gzip 압축 (무료 플랜 대역폭 절약)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"🚀 {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


# API 라우터 등록
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    # Railway 환경에서는 PORT 환경변수 사용
    port = int(settings.PORT)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG and not settings.is_production,
        log_level=settings.LOG_LEVEL
    )