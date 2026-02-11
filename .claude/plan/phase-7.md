# Phase 7: 프론트엔드 ✅ DONE

## 할 일

### 세팅
- [x] Next.js 14.2.21 (App Router, Turbo) + Tailwind 3.4 + TanStack Query 5
- [x] lib/api.ts — SSR/CSR 자동 분기 (서버: backend:8000, 브라우저: localhost:8000)
- [x] types/index.ts — Post, Comment, PaginatedPosts 등 타입 정의
- [x] components/Providers.tsx — TanStack QueryClientProvider
- [x] Dockerfile + docker-compose.yml frontend 서비스 추가
- [x] app/layout.tsx — 다크 테마 기본 (`<html class="dark">`), OG 메타태그

### 페이지
- [x] app/page.tsx — 홈 (게시글 목록, SSR, 페이지네이션, AuthorBadge)
- [x] app/post/[id]/page.tsx — 상세 (SSR, 댓글 트리, generateMetadata)
- [x] app/write/page.tsx — 글쓰기 (honeypot, author_type 토글, 모바일 반응형)

### 컴포넌트
- [x] components/AuthorBadge.tsx — AI 보라(purple-900), Bot 녹색(green-900), Human 없음
- [x] components/CommentTree.tsx — 재귀 CommentNode (대댓글 들여쓰기)
- [ ] CommentForm, DarkModeToggle (미구현 — 추후 개선)

### 스팸 방어 (프론트)
- [x] 폼에 honeypot 필드 (숨김) 포함 — absolute left:-9999px, aria-hidden, tabIndex=-1

### SEO — generateMetadata()
- [x] app/page.tsx — 정적 메타 (title, description, og)
- [x] app/post/[id]/page.tsx — 동적 메타 (제목, 본문 미리보기, og:article, published_time, author)

## 완료 기준
- [x] localhost:3000 접속 → 목록 SSR 렌더링 + 페이지네이션
- [x] localhost:3000/post/1 → 상세 + 댓글 트리 + AI 보라색 뱃지
- [x] AI 글에 보라색 뱃지 (목록 4개 + 상세 모두)
- [x] Ctrl+U에서 HTML 콘텐츠 보임 (SSR) — `<h2>` 제목, 본문, 댓글 모두 서버 렌더링
- [x] OG 메타태그 (목록: 정적, 상세: 동적 og:title, og:description, og:article)
- [x] /post/99999 → 404
- [x] 글쓰기 페이지 — title, content, author_name, author_type 토글, honeypot
- [x] 모바일 레이아웃 검증 (grid-cols-1 md:grid-cols-2 반응형)

## 검증 결과 (2026-02-11)
| 항목 | 결과 |
|------|------|
| 목록 SSR | ✅ 12개 게시글 HTML에 직접 렌더링 |
| 상세 + 댓글 | ✅ post/1: 제목, 본문, 댓글 3개 (대댓글 ml-6 들여쓰기) |
| 글쓰기 | ✅ 폼 렌더링 + API 연동 (post 13 생성 확인) |
| AI 뱃지 | ✅ 목록 4개, 상세 bg-purple-900 text-purple-300 |
| SSR (Ctrl+U) | ✅ 제목·본문·댓글 모두 HTML 소스에 포함 |
| OG 메타 | ✅ og:title, og:description, og:type=article |
