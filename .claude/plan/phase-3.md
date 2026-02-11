# Phase 3: 개방형 REST API + 스팸 방어 ✅ DONE

## 핵심
인증 없이 누구나 글/댓글 작성 가능.
대신 스팸 방어 6단계 적용.

## 할 일

### API 엔드포인트 (인증 없음!)
- [x] routers/posts.py (6개 엔드포인트)
- [x] routers/comments.py (3개 엔드포인트)
- [x] services/comment_tree.py (트리 변환 로직 분리)

### 스팸 방어 6단계
- [x] Layer 1: Rate Limiting (SlowAPI) — POST 5회/분, GET 60회/분
- [x] Layer 2: 콘텐츠 중복 검증 — 60초 내 동일 내용 차단
- [x] Layer 3: XSS(Bleach) + Prompt Injection(정규식 6패턴) 방어
- [x] Layer 4: Honeypot 필드 검사
- [x] Layer 5: User-Agent 기반 AI 분류 (Claude→ai 자동)
- [x] Layer 6: IP 블랙리스트 (Redis SET)
- [x] main.py에 SlowAPI + CORS(origins=["*"]) 등록
- [x] 통합 파이프라인: run_spam_checks_post / run_spam_checks_comment

## Swagger 테스트 결과
| # | 테스트 | 기대 | 결과 |
|---|--------|------|------|
| 1 | POST /api/posts 인증 없이 글 작성 | 201 | ✅ PASS |
| 2 | 같은 내용 다시 POST | 409 | ✅ PASS |
| 3 | `<script>alert(1)</script>` 입력 | 태그 제거 | ✅ PASS |
| 4 | 1분에 6번 POST | 429 | ✅ PASS |
| 5 | author_type="ai" DB 저장 | AI로 저장 | ✅ PASS |
