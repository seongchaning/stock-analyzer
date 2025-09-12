# 한국 주식 기술적 분석 서비스 - 프로젝트 이전 가이드

## 프로젝트 개요
- **프로젝트명**: 한국 주식 기술적 분석 서비스
- **기술 스택**: FastAPI + React + TypeScript + PostgreSQL
- **주요 기능**: RSI 과매도 + MACD 골든크로스 매수 신호 분석 (시총 상위 200개 종목)

## 1. 필수 사전 설치 프로그램

### Node.js & npm
```bash
# Node.js 18+ 설치 (공식 웹사이트에서 다운로드)
# https://nodejs.org/

# 설치 확인
node --version
npm --version
```

### Python 3.9+
```bash
# Python 3.9+ 설치
# https://www.python.org/downloads/

# 설치 확인
python --version
pip --version
```

### Git
```bash
# Git 설치
# https://git-scm.com/downloads

# 설치 확인
git --version
```

## 2. 프로젝트 구조

```
stock-analyzer/
├── README.md
├── PROJECT_MIGRATION_GUIDE.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── screening.py
│   │   │           ├── stocks.py
│   │   │           └── market.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── stock.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── screening.py
│   │   │   ├── stock.py
│   │   │   └── market.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── screening_service.py
│   │       ├── stock_service.py
│   │       └── market_service.py
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── init_db.py
│   │   ├── collect_daily_data.py
│   │   ├── collect_market_indices.py
│   │   └── run_screening.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   ├── MarketOverview.tsx
    │   │   ├── StockCard.tsx
    │   │   └── FilterControls.tsx
    │   ├── pages/
    │   │   └── HomePage.tsx
    │   ├── services/
    │   │   └── api.ts
    │   ├── store/
    │   │   └── useStore.ts
    │   ├── types/
    │   │   └── index.ts
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── index.css
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    └── tailwind.config.js
```

## 3. 백엔드 설정

### 3.1 Python 가상환경 설정
```bash
# 프로젝트 루트에서
cd stock-analyzer/backend

# 가상환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3.2 환경변수 설정
```bash
# .env 파일 생성 (backend/.env)
cp .env.example .env

# .env 파일 내용 수정
DATABASE_URL=postgresql://username:password@localhost/stock_analyzer
SECRET_KEY=your-secret-key-here
```

### 3.3 PostgreSQL 데이터베이스 설정
```bash
# PostgreSQL 설치 (로컬) 또는 Railway 사용

# 데이터베이스 생성
createdb stock_analyzer

# 테이블 생성 및 초기 데이터
python scripts/init_db.py
```

## 4. 프론트엔드 설정

### 4.1 의존성 설치
```bash
cd stock-analyzer/frontend

# 의존성 설치
npm install
```

### 4.2 환경변수 설정
```bash
# .env 파일 생성 (frontend/.env)
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
```

## 5. 프로젝트 실행

### 5.1 백엔드 실행
```bash
cd stock-analyzer/backend

# 가상환경 활성화
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# FastAPI 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 프론트엔드 실행
```bash
cd stock-analyzer/frontend

# React 개발서버 실행
npm start
```

## 6. 데이터 수집 스크립트 실행

### 6.1 시장 지수 데이터 수집
```bash
cd stock-analyzer/backend
python scripts/collect_market_indices.py
```

### 6.2 종목 데이터 및 기술적 지표 수집
```bash
cd stock-analyzer/backend
python scripts/collect_daily_data.py
```

### 6.3 매수 신호 생성
```bash
cd stock-analyzer/backend
python scripts/run_screening.py
```

## 7. 접속 URL

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 8. 트러블슈팅

### 8.1 일반적인 문제들

**PostgreSQL 연결 오류**
```bash
# PostgreSQL 서비스 상태 확인
# Windows: services.msc에서 PostgreSQL 서비스 확인
# macOS: brew services list | grep postgresql
# Linux: sudo systemctl status postgresql

# 데이터베이스 존재 확인
psql -U your_username -l
```

**Python 의존성 오류**
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**npm 의존성 오류**
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 8.2 포트 충돌 해결
```bash
# 백엔드 포트 변경
uvicorn app.main:app --reload --port 8001

# 프론트엔드 포트 변경
PORT=3001 npm start
```

## 9. 배포 준비

### 9.1 Railway (백엔드)
```bash
# Railway CLI 설치
npm install -g @railway/cli

# Railway 로그인
railway login

# 프로젝트 생성 및 배포
railway link
railway up
```

### 9.2 Vercel (프론트엔드)
```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel --prod
```

## 10. 체크리스트

### 이전 완료 체크리스트
- [ ] Node.js 18+ 설치
- [ ] Python 3.9+ 설치
- [ ] PostgreSQL 설치 또는 Railway 계정 준비
- [ ] Git 설치
- [ ] 프로젝트 폴더 복사
- [ ] 백엔드 가상환경 생성 및 의존성 설치
- [ ] 프론트엔드 의존성 설치
- [ ] 환경변수 파일 설정
- [ ] 데이터베이스 생성 및 초기화
- [ ] 백엔드 실행 확인
- [ ] 프론트엔드 실행 확인
- [ ] API 연결 테스트
- [ ] 데이터 수집 스크립트 실행

### 기능 테스트 체크리스트
- [ ] 매수 신호 목록 조회
- [ ] 종목별 상세 정보 조회
- [ ] 차트 데이터 표시
- [ ] 시장 통계 정보
- [ ] 섹터별 필터링
- [ ] 신호 강도별 정렬

이 가이드를 따라하시면 다른 PC에서도 동일한 환경으로 프로젝트를 실행할 수 있습니다.