# 프로젝트 파일 복사 가이드

## 방법 1: 전체 폴더 압축 (추천)

### Windows
```cmd
# 프로젝트 상위 폴더로 이동
cd C:\Users\allow\

# 7-Zip 사용 (7-Zip 설치 필요)
7z a -tzip stock-analyzer.zip stock-analyzer\

# Windows 기본 압축
# stock-analyzer 폴더 우클릭 → "보내기" → "압축(zip) 폴더"
```

### PowerShell
```powershell
# 프로젝트 상위 폴더로 이동
cd C:\Users\allow\

# PowerShell 압축
Compress-Archive -Path "stock-analyzer" -DestinationPath "stock-analyzer.zip"
```

## 방법 2: Git을 사용한 복사 (추천)

### 현재 PC에서 Git 저장소 초기화
```bash
cd C:\Users\allow\stock-analyzer

# Git 저장소 초기화
git init

# .gitignore 파일 생성
echo "node_modules/" > .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "*.pyc" >> .gitignore

# 모든 파일 추가
git add .

# 첫 번째 커밋
git commit -m "Initial commit - Korean Stock Analyzer"
```

### GitHub에 업로드 (옵션)
```bash
# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/stock-analyzer.git
git branch -M main
git push -u origin main
```

### 새 PC에서 복사
```bash
# Git으로 복사
git clone https://github.com/YOUR_USERNAME/stock-analyzer.git

# 또는 USB/네트워크 드라이브에서 복사 후
cd stock-analyzer
git init
git add .
git commit -m "Project copied"
```

## 방법 3: 필수 파일만 수동 복사

### 복사해야 할 폴더 구조
```
stock-analyzer/
├── README.md
├── PROJECT_MIGRATION_GUIDE.md
├── COPY_FILES_GUIDE.md
├── backend/
│   ├── app/          (전체 폴더)
│   ├── scripts/      (전체 폴더)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── public/       (전체 폴더)
    ├── src/          (전체 폴더)
    ├── package.json
    ├── tsconfig.json
    └── tailwind.config.js
```

### 제외해야 할 폴더/파일 (용량 절약)
```
❌ 제외할 것들:
- backend/venv/           (가상환경 - 새로 만들어야 함)
- backend/__pycache__/    (Python 캐시)
- backend/.env           (실제 환경변수 - 보안상 제외)
- frontend/node_modules/ (npm 의존성 - 새로 설치)
- frontend/build/        (빌드 결과물)
- .git/                 (Git 저장소, 선택사항)
```

## 방법 4: 클라우드 스토리지 사용

### Google Drive / OneDrive
1. 압축된 파일을 클라우드에 업로드
2. 새 PC에서 다운로드 후 압축 해제

### GitHub (무료, 추천)
1. GitHub 계정 생성
2. 새 저장소 생성 (Public 또는 Private)
3. 파일 업로드 또는 Git으로 push
4. 새 PC에서 clone

## 새 PC에서 실행 순서

### 1. 프로젝트 복사 후 백엔드 설정
```bash
cd stock-analyzer/backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 DATABASE_URL 등 설정
```

### 2. 프론트엔드 설정
```bash
cd stock-analyzer/frontend

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env
```

### 3. 데이터베이스 설정
```bash
# PostgreSQL 설치 후
createdb stock_analyzer

# 초기화
cd stock-analyzer/backend
python scripts/init_db.py
```

### 4. 실행 테스트
```bash
# 터미널 1: 백엔드
cd stock-analyzer/backend
uvicorn app.main:app --reload

# 터미널 2: 프론트엔드
cd stock-analyzer/frontend
npm start
```

## 체크리스트

### 파일 복사 전
- [ ] 프로젝트가 정상 실행되는지 확인
- [ ] 중요한 .env 파일 백업 (실제 환경변수 값들)
- [ ] 데이터베이스 스키마 백업 (필요시)

### 파일 복사 방법 선택
- [ ] Git 사용 (권장)
- [ ] 전체 폴더 압축
- [ ] 클라우드 스토리지
- [ ] USB/외장하드

### 새 PC에서 설정 완료 후
- [ ] Python 가상환경 생성 및 의존성 설치
- [ ] Node.js 의존성 설치
- [ ] 환경변수 파일 설정
- [ ] 데이터베이스 연결 확인
- [ ] 백엔드 실행 테스트 (http://localhost:8000/docs)
- [ ] 프론트엔드 실행 테스트 (http://localhost:3000)
- [ ] API 연결 확인

## 트러블슈팅

### 권한 오류 (Windows)
```cmd
# 관리자 권한으로 PowerShell 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python 경로 오류
```bash
# Python 경로 확인
which python
python --version

# 가상환경 재생성
rm -rf venv
python -m venv venv
```

### Node.js 버전 호환성
```bash
# Node.js 버전 확인 (18+ 필요)
node --version

# nvm 사용시
nvm use 18
```

이 가이드를 따라하시면 안전하게 프로젝트를 이전할 수 있습니다!