# 한국 주식 기술적 분석 서비스

무료로 운영되는 한국 주식 기술적 분석 및 매수 신호 제공 서비스

## 🎯 프로젝트 개요

- **대상**: 중장기 투자 개인투자자
- **범위**: 시가총액 상위 200개 종목
- **신호**: RSI 과매도 + MACD 골든크로스
- **데이터**: 6개월 히스토리
- **비용**: 100% 무료 운영

## 🏗️ 기술 스택

### 백엔드
- **Python 3.11+** - 백엔드 언어
- **FastAPI** - 웹 프레임워크
- **PostgreSQL** - 데이터베이스 (Railway 무료)
- **FinanceDataReader** - 주식 데이터 수집
- **pandas** - 데이터 처리
- **SQLAlchemy** - ORM

### 프론트엔드
- **React 18+** - UI 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **TradingView Charts** - 차트 라이브러리
- **Zustand** - 상태 관리

### 인프라
- **Railway** - 백엔드 + DB 호스팅 (무료)
- **Vercel** - 프론트엔드 호스팅 (무료)
- **GitHub Actions** - 데이터 수집 자동화 (무료)

## 🚀 빠른 시작

### 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 DATABASE_URL 설정

# 데이터베이스 마이그레이션
python scripts/init_db.py

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 설정
```bash
cd frontend
npm install
npm start
```

### 전체 시스템 실행 (권장)
```bash
# 터미널 1: 백엔드 서버
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 터미널 2: 프론트엔드 서버  
cd frontend
npm start

# 터미널 3: 데이터 수집 (선택사항)
cd backend
source venv/bin/activate
python scripts/collect_daily_data.py
```

### 서비스 접속
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🔄 재실행 방법

### 전체 재시작
```bash
# 실행 중인 프로세스 종료 (Ctrl+C)
# 또는 포트 강제 종료
pkill -f "uvicorn\|npm"

# 백엔드 재시작
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# 프론트엔드 재시작  
cd frontend && npm start &
```

### 데이터 업데이트
```bash
cd backend
source venv/bin/activate

# 일별 주식 데이터 수집
python scripts/collect_daily_data.py

# 시장 지수 업데이트
python scripts/update_market_summary.py

# 매수 신호 스크리닝
python scripts/run_screening.py
```

### 문제 해결
```bash
# 포트 충돌 시 프로세스 확인
lsof -i :3000  # 프론트엔드 포트
lsof -i :8000  # 백엔드 포트

# 프로세스 강제 종료
kill -9 <PID>

# 데이터베이스 재설정 (필요시)
cd backend
python scripts/init_db.py
```

## 📊 주요 기능

### 1. 매수 신호 스크리닝
- 매일 자동으로 RSI 과매도 + MACD 골든크로스 조건 검색
- 신호 강도별 상위 10개 종목 제공
- 실시간 업데이트 (GitHub Actions 스케줄)

### 2. 종목 차트 분석
- 6개월간 일봉 캔들차트
- RSI, MACD 기술적 지표 오버레이
- 모바일 최적화된 터치 인터랙션

### 3. 시장 현황
- 코스피/코스닥 지수 현황
- 신호 발생 종목 통계
- 섹터별 분포

## 🔄 데이터 수집 과정

1. **GitHub Actions** (매일 18:00 UTC)
2. **FinanceDataReader**로 상위 200개 종목 데이터 수집
3. **기술적 지표** 계산 (RSI, MACD)
4. **스크리닝 조건** 적용
5. **Railway PostgreSQL**에 결과 저장

## 📱 지원 환경

- **모바일**: iOS Safari, Android Chrome
- **데스크톱**: Chrome, Safari, Firefox, Edge
- **반응형**: 320px ~ 1920px

## 🎛️ API 엔드포인트

```
GET /api/v1/screening/signals     # 매수 신호 목록
GET /api/v1/stocks/{symbol}       # 종목 상세 정보  
GET /api/v1/stocks/{symbol}/chart # 차트 데이터
GET /api/v1/market/stats          # 시장 통계
```

## 🚨 제약사항 (무료 플랜)

- **종목 수**: 200개 (시가총액 상위)
- **히스토리**: 6개월
- **동시 사용자**: ~10명 (Railway 수면 모드)
- **일간 사용자**: ~50명 (500시간 한도)
- **웨이크업 시간**: 5-10초 (첫 접속시)

## 📈 성능 목표

- **API 응답**: < 500ms (웨이크업 후)
- **차트 로딩**: < 5초
- **첫 페이지**: < 10초 (웨이크업 포함)
- **데이터 정확도**: > 99%

## 🔒 면책 조항

본 서비스는 정보 제공 목적이며, 투자 조언이 아닙니다. 
모든 투자 결정은 사용자의 책임입니다.

## 📄 라이선스

MIT License

---
**개발 기간**: 4주 (MVP)  
**런치 목표**: 2024년 10월