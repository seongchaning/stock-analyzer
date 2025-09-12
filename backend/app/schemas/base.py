"""
기본 스키마 클래스들
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# 제네릭 타입 변수
DataType = TypeVar('DataType')


class BaseResponse(BaseModel, Generic[DataType]):
    """API 응답 기본 구조"""
    data: DataType
    message: Optional[str] = None
    success: bool = True
    

class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    page: int = Field(..., ge=1, description="현재 페이지")
    size: int = Field(..., ge=1, le=100, description="페이지 크기")
    total: int = Field(..., ge=0, description="전체 항목 수")
    pages: int = Field(..., ge=0, description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")


class PaginatedResponse(BaseResponse[DataType]):
    """페이지네이션이 포함된 응답"""
    meta: PaginationMeta


class ErrorResponse(BaseModel):
    """에러 응답 구조"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    success: bool = False