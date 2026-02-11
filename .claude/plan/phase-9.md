# Phase 9: 통합 + 배포 ✅ DONE

## 할 일

### Nginx
- [x] nginx.conf 최종: / → frontend, /api/ → backend, /mcp/ → backend
- [x] /llms.txt, /.well-known/, /sitemap.xml, /robots.txt → backend
- [x] /openapi.json, /docs, /health, /posts/ → backend
- [x] gzip on (text/plain, css, json, js, xml)
- [x] SSL placeholder (주석, Let's Encrypt 준비)
- [x] MCP SSE: proxy_buffering off, proxy_read_timeout 86400s
- [x] Frontend WebSocket upgrade (HMR 지원)

### Docker
- [x] frontend/Dockerfile (node:20-alpine)
- [x] docker-compose.yml — frontend 서비스 + nginx depends_on frontend
- [x] docker-compose up --build 전체 6개 서비스 정상

### MCP Host 검증
- [x] mcp 1.26.0 DNS rebinding protection → allowed_hosts 설정
- [x] TransportSecuritySettings(allowed_hosts=["localhost", "localhost:8000", "localhost:80"])

### 최종 체크리스트 (전부 nginx:80 경유)
- [x] GET /health → `{"status":"ok"}`
- [x] GET /api/posts → JSON (total=18, items 정상)
- [x] POST /api/posts → 인증 없이 성공 (id=18)
- [x] GET /llms.txt → AI 안내문
- [x] GET /.well-known/ai-plugin.json → name=AI-Human Board, auth=none
- [x] GET /openapi.json → paths=11
- [x] GET /sitemap.xml → XML
- [x] GET /robots.txt → AI 봇 허용
- [x] MCP SSE → event: endpoint, data: session_id
- [x] Frontend / → SSR 게시글 목록
- [x] Frontend /write → 글쓰기 폼
- [x] Frontend /post/14 → Bot 뱃지 (bg-green-900)
- [x] Bot worker → 4.3시간 주기 동작 중

## Nginx 라우팅 맵
```
nginx:80
├── /api/*          → backend:8000  (REST API)
├── /health         → backend:8000
├── /docs           → backend:8000  (Swagger)
├── /openapi.json   → backend:8000
├── /llms.txt       → backend:8000  (AI discovery)
├── /.well-known/*  → backend:8000  (ai-plugin.json)
├── /mcp/*          → backend:8000  (MCP SSE, buffering off)
├── /posts/*        → backend:8000  (SEO HTML)
├── /sitemap.xml    → backend:8000
├── /robots.txt     → backend:8000
└── /*              → frontend:3000 (Next.js, catch-all)
```

### 배포 (미완 — 도메인 확보 후)
- [ ] 도메인 연결
- [ ] SSL (Let's Encrypt)
- [ ] Google Search Console 등록
