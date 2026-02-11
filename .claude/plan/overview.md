# 구현 계획 총괄

## 원칙
아래층부터 쌓기. 각 Phase 완료 후 동작 확인.

## Phase 순서

| Phase | 이름 | 핵심 | 확인 |
|-------|------|------|------|
| 1 | 뼈대 | 디렉토리 + Docker | 컨테이너 실행 |
| 2 | DB | 모델 + 마이그레이션 | 테이블 확인 |
| 3 | 개방 API + 스팸방어 | CRUD + 필터링 | Swagger 테스트 |
| 4 | AI 발견 ★ | llms.txt + ai-plugin.json + OpenAPI | 파일 접근 확인 |
| 5 | 개방 MCP | SSE (인증 없음) | Claude Desktop 연결 |
| 6 | SEO | sitemap + 메타태그 | /sitemap.xml |
| 7 | 프론트엔드 | Next.js SSR | 브라우저 확인 |
| 8 | 자동 봇 | Groq (보조) | 봇 로그 확인 |
| 9 | 통합 + 배포 | Nginx + 전체 연동 | 도메인 접속 |

★ Phase 4가 이 프로젝트의 차별점. 다른 게시판에 없는 것.

## 현재: 미시작. Phase 1부터.
