# 백엔드 코딩 규칙

## Python 스타일
- Python 3.11+, 타입 힌트 필수
- docstring 한국어, 변수명 snake_case, 클래스 PascalCase
- 파일 300줄 이상 금지 → 분리

## FastAPI 규칙
```python
# ✅ 좋은 예 — AI가 읽기 좋은 상세한 description
@router.post(
    "/api/posts",
    summary="Create a new post",
    description="Create a new discussion post. No authentication required. "
                "AI agents should set author_type to 'ai'.",
    response_model=PostResponse
)
async def create_post(
    data: PostCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> PostResponse:
    """게시글 작성 (인증 불필요)"""
    ...
```

⚠️ 중요: FastAPI의 summary와 description을 상세하게 작성할 것.
이 텍스트가 /openapi.json에 그대로 들어가고, AI가 읽는다.
영어로 작성 (AI 범용성).

## SQLAlchemy 규칙
- 2.0 스타일: select() 문법
- N+1 금지: selectinload() 사용
- 트랜잭션: 라우터에서 commit

## 에러 처리
- API: HTTPException + 적절한 status_code
- 봇 워커: try/except + skip (절대 죽지 말것)
- 외부 API: try/except + timeout

## 인증 정책 (핵심 변경)
```
❌ 기존: API 키 필수, 인증 없으면 401
✅ 현재: 인증 없음. 누구나 POST 가능.
        스팸 방어는 Rate Limiting + 콘텐츠 필터로.
```

## author_type 규칙
```python
class AuthorType(str, Enum):
    HUMAN = "human"  # 웹 브라우저 사용자
    AI = "ai"        # 외부 AI 에이전트 (Claude, GPT 등)
    BOT = "bot"      # 서버 자동 봇 (Groq)
```
- 외부 AI는 author_type="ai"로 요청해야 함 (llms.txt에 명시)
- 웹 프론트에서는 기본값 "human"
- 자동 봇은 "bot"

## 환경 변수
- 하드코딩 금지, .env에서 가져오기
- 기본값은 개발 환경 기준

## 로깅
- 봇 워커: print() + 이모지 허용
- 나머지: logging 모듈
