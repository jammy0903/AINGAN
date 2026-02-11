# Phase 1: 프로젝트 뼈대

## 할 일
- [x] 전체 디렉토리 구조 생성
- [x] backend/requirements.txt
- [x] backend/Dockerfile (Python 3.11)
- [x] docker-compose.yml (backend, bot-worker, db, redis, nginx)
- [x] .env.example
- [x] .gitignore
- [x] backend/main.py (GET /health만)
- [x] nginx/nginx.conf (기본)
- [x] backend/bot/run.py (bot-worker placeholder)

## 완료 기준
```bash
docker-compose up --build -d
curl http://localhost:8000/health → {"status": "ok"}  ✅
curl http://localhost/health → {"status": "ok"}        ✅ (nginx 경유)
http://localhost:8000/docs → Swagger UI                ✅ (200)
5개 서비스 Running: backend, bot-worker, db, redis, nginx ✅
```
