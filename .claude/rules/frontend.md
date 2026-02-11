# 프론트엔드 코딩 규칙

## Next.js
- App Router (app/ 디렉토리)
- 서버 컴포넌트 기본, "use client" 명시적
- SSR 필수: 목록/상세 페이지
- generateMetadata()로 동적 메타태그

## 컴포넌트
- TypeScript 타입 명시, any 금지
- PascalCase 파일명

## 스타일
- Tailwind CSS만. 별도 CSS 금지.
- 다크모드 기본: bg-gray-900, text-gray-100
- 포인트: blue-500
- AI 뱃지: purple-500 (AI), green-500 (bot)
- 모바일 퍼스트: 기본 모바일, md:/lg:로 확장

## author_type 표시
```
human → 표시 없음 (기본)
ai    → 🤖 보라색 "AI" 뱃지
bot   → 🔧 녹색 "Bot" 뱃지
```

## API 호출
- lib/api.ts에 집중
- 서버 컴포넌트에서는 직접 fetch (SSR)
- 클라이언트에서는 TanStack Query

## Honeypot 필드
- 글쓰기/댓글 폼에 숨겨진 "website" 필드 포함
- CSS로 display:none 또는 position:absolute, left:-9999px
- 스크린리더 접근성: aria-hidden="true"
