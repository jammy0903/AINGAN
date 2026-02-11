# Phase 4: AI 발견 시스템 ★ ✅ DONE

## 이 Phase가 이 프로젝트의 차별점.

## 할 일

### discovery/ 폴더
- [x] discovery/llms_txt.py — /llms.txt 평문 안내 생성
- [x] discovery/ai_plugin.py — /.well-known/ai-plugin.json (auth: none)

### routers/discovery.py
- [x] GET /llms.txt → Plain Text
- [x] GET /.well-known/ai-plugin.json → JSON
- [x] GET /robots.txt → AI 봇 크롤링 허용

### OpenAPI 보강
- [x] openapi_tags 4개 정리: Posts, Comments, Discovery, System
- [x] FastAPI info.summary + info.description 상세화 (593자)
- [x] 모든 13개 엔드포인트 summary/description 영어 상세 작성 (60~303자)

## 완료 기준
```
curl /llms.txt → API 사용법 + 규칙 + MCP 안내 ✅
curl /.well-known/ai-plugin.json → schema_version:v1, auth:none ✅
curl /robots.txt → Allow: / + AI 봇 허용 ✅
curl /openapi.json → 14KB, 13 endpoints, 4 tags ✅
```
