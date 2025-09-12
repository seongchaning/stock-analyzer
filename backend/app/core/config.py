"""
설정 관리 - 무료 플랜 최적화
"""
import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 프로젝트 정보
    PROJECT_NAME: str = "Stock Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # 데이터베이스
    DATABASE_URL: str
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://*.vercel.app"
    ]
    
    # 로깅
    LOG_LEVEL: str = "info"
    
    # 캐시 설정 (메모리 기반)
    CACHE_TTL_SECONDS: int = 3600
    
    # 데이터 수집 설정
    DATA_COLLECTION_ENABLED: bool = True
    MAX_STOCKS: int = 200  # 무료 플랜: 상위 200개 종목만
    DATA_RETENTION_DAYS: int = 180  # 6개월
    
    # 보안
    SECRET_KEY: str = "change-this-secret-key"
    
    # 에러 모니터링 (선택사항)
    SENTRY_DSN: Optional[str] = None
    
    # Railway 환경 감지
    RAILWAY_ENVIRONMENT_NAME: Optional[str] = None
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("DEBUG", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENVIRONMENT == "production" or self.RAILWAY_ENVIRONMENT_NAME is not None
    
    @property
    def database_config(self) -> dict:
        """데이터베이스 연결 설정 - 무료 플랜 최적화"""
        return {
            "pool_size": 3,        # 기본값 5 → 3 (메모리 절약)
            "max_overflow": 2,     # 기본값 10 → 2
            "pool_recycle": 3600,  # 1시간마다 연결 재활용
            "pool_pre_ping": True, # 연결 상태 확인
            "echo": not self.is_production  # 프로덕션에서는 로그 최소화
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()