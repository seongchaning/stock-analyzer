"""
데이터베이스 연결 설정 - 무료 플랜 최적화
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# 무료 플랜 최적화 설정
engine = create_engine(
    settings.DATABASE_URL,
    **settings.database_config,
    # Railway PostgreSQL 무료 플랜 최적화
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db() -> None:
    """데이터베이스 초기화"""
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    print("데이터베이스 초기화 완료")