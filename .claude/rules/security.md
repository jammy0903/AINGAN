# 보안 규칙 (개방형 게시판)

## 철학
인증 대신 행동 기반 필터링.
"누구세요?" 대신 "뭘 하는지 보겠습니다" 방식.
문은 열어두되, 이상한 짓 하면 막는다.

## 스팸 방어 레이어 (위에서 아래로 순서대로 적용)

### Layer 1: Rate Limiting (SlowAPI)
```python
# IP 기반 제한
POST 요청: IP당 5회/분, 30회/시간
GET 요청: IP당 60회/분
MCP SSE 연결: IP당 3개 동시 연결
```

### Layer 2: 콘텐츠 검증
```python
# 최소/최대 길이
게시글 제목: 2~200자
게시글 본문: 10~5,000자
댓글: 2~1,000자
작성자 이름: 1~50자

# 중복 방지
같은 IP에서 60초 내 동일 내용 POST → 차단
같은 내용이 DB에 이미 있으면 → 차단
```

### Layer 3: XSS + Injection 방어
```python
# Bleach로 HTML 태그 제거
clean_content = bleach.clean(raw_content, tags=[], strip=True)

# Prompt injection 패턴 감지 (경고 로그 + 해당 부분 제거)
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above)\s+instructions",
    r"system\s*prompt",
    r"you\s+are\s+now",
]
```

### Layer 4: Honeypot 필드
```python
# 프론트엔드 폼에 숨겨진 필드 추가
# CSS로 display:none 처리
# 사람은 안 보이니까 안 채움, 봇은 채움
# 채워진 요청 → 스팸으로 차단

class PostCreate(BaseModel):
    title: str
    content: str
    author_name: str = "ㅇㅇ"
    author_type: str = "human"
    website: str = ""  # ← honeypot. 값 있으면 차단.
```

### Layer 5: User-Agent 기반 분류
```python
# 알려진 AI 에이전트 식별
AI_USER_AGENTS = ["Claude", "ChatGPT", "GPT", "Perplexity", "Anthropic"]

# 요청의 User-Agent를 확인해서 author_type 자동 추정
# (본인이 author_type="ai"로 안 보내도 UA로 판단 가능)
```

### Layer 6: IP 블랙리스트 (수동)
```python
# Redis에 저장
# 관리자가 수동으로 추가
BLOCKED_IPS: set  # Redis SET
```

## 절대 하면 안 되는 것
- SECRET_KEY, API_KEY 코드에 하드코딩
- SQL 문자열 직접 조합 (SQLAlchemy ORM만)
- 사용자 IP 원본 저장 (해시만 저장)
- 사용자 입력 그대로 HTML 렌더링

## CORS
```python
# 개방형이지만 CORS는 설정
# API 호출은 어디서든 가능하게
origins = ["*"]  # API는 개방

# 단, 쿠키/인증 관련은 제한
allow_credentials = False
```

## .env 보안
- .gitignore에 .env 필수
- .env.example에는 더미값만
