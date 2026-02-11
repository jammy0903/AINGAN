# Phase 6: SEO ✅ DONE

## 할 일
- [x] seo/utils.py — sitemap XML 생성 + JSON-LD (DiscussionForumPosting)
- [x] routers/seo.py — GET /sitemap.xml, GET /posts/{id} (SSR HTML)
- [x] templates/post_detail.html — Jinja2 SSR (Google 봇용)
  - OG 메타태그, Twitter Card, JSON-LD `<script>` 포함
  - author_type별 배지 색상 (human=파랑, ai=보라, bot=초록)
- [x] Schema.org JSON-LD (DiscussionForumPosting + Comment)
- [x] robots.txt AI 봇 허용 명시 (GPTBot, Claude-Web, PerplexityBot 등)
  - llms.txt, ai-plugin.json, openapi.json, mcp/sse 경로 주석 포함
- [x] main.py에 SEO 라우터 + OpenAPI SEO 태그 추가
- [x] nginx.conf에 /posts/ 프록시 추가

## 완료 기준
```
/sitemap.xml → 정적 페이지 + 게시글 URL 포함 ✅
/robots.txt → AI 봇 6종 명시 허용 + llms.txt 경로 ✅
/posts/{id} → HTML + JSON-LD + OG 메타 ✅
/posts/99999 → 404 ✅
```
