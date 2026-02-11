"""스팸 방어 6단계 — 인증 대신 행동 기반 필터링

Layer 1: Rate Limiting (SlowAPI) — main.py에서 설정
Layer 2: 콘텐츠 검증 (길이는 Pydantic, 중복은 여기서)
Layer 3: XSS + Prompt Injection 방어 (Bleach + 정규식)
Layer 4: Honeypot 필드 검사
Layer 5: User-Agent 기반 AI 에이전트 분류
Layer 6: IP 블랙리스트 (Redis)
"""

import hashlib
import logging
import os
import re
from datetime import datetime, timedelta, timezone

import bleach
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Comment, Post

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Layer 3: Prompt injection 패턴
# ──────────────────────────────────────────────
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(previous|above)\s+instructions", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"you\s+are\s+now", re.I),
    re.compile(r"disregard\s+(all|any)\s+(prior|previous)", re.I),
    re.compile(r"forget\s+(everything|all)\s+(above|before)", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
]

# ──────────────────────────────────────────────
# Layer 5: 알려진 AI User-Agent 키워드
# ──────────────────────────────────────────────
AI_USER_AGENTS = [
    "claude", "chatgpt", "gpt", "openai", "anthropic",
    "perplexity", "copilot", "gemini", "bard",
]

# ──────────────────────────────────────────────
# Redis (lazy import — 없으면 skip)
# ──────────────────────────────────────────────
_redis = None


async def _get_redis():
    """Redis 연결 (Layer 6용). 실패해도 서비스 중단 안 함."""
    global _redis
    if _redis is not None:
        return _redis
    try:
        import redis.asyncio as aioredis
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        _redis = aioredis.from_url(url, decode_responses=True)
        await _redis.ping()
        return _redis
    except Exception:
        logger.warning("Redis unavailable — Layer 6 (blacklist) disabled")
        return None


# ──────────────────────────────────────────────
# 공통 유틸
# ──────────────────────────────────────────────
def hash_ip(ip: str) -> str:
    """IP → SHA-256 해시 (원본 저장 금지)"""
    return hashlib.sha256(ip.encode()).hexdigest()


def get_client_ip(request: Request) -> str:
    """프록시 뒤에서도 실제 클라이언트 IP 추출"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ──────────────────────────────────────────────
# Layer 2: 콘텐츠 중복 검증
# ──────────────────────────────────────────────
async def check_duplicate_post(
    db: AsyncSession, ip_hash: str, title: str, content: str
) -> None:
    """같은 IP에서 60초 내 동일 제목+내용 게시글 차단"""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    stmt = (
        select(Post.id)
        .where(
            Post.ip_hash == ip_hash,
            Post.title == title,
            Post.content == content,
            Post.created_at >= cutoff,
        )
        .limit(1)
    )
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Duplicate post detected.")


async def check_duplicate_comment(
    db: AsyncSession, ip_hash: str, post_id: int, content: str
) -> None:
    """같은 IP에서 60초 내 동일 댓글 차단"""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    stmt = (
        select(Comment.id)
        .where(
            Comment.ip_hash == ip_hash,
            Comment.post_id == post_id,
            Comment.content == content,
            Comment.created_at >= cutoff,
        )
        .limit(1)
    )
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Duplicate comment detected.")


# ──────────────────────────────────────────────
# Layer 3: XSS + Prompt Injection 방어
# ──────────────────────────────────────────────
def sanitize_text(text: str) -> str:
    """HTML 태그 제거 + prompt injection 패턴 제거"""
    cleaned = bleach.clean(text, tags=[], strip=True)
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            logger.warning("Prompt injection detected: %s", match.group())
            cleaned = pattern.sub("", cleaned)
    return cleaned.strip()


# ──────────────────────────────────────────────
# Layer 4: Honeypot 필드
# ──────────────────────────────────────────────
def check_honeypot(website: str) -> None:
    """숨겨진 website 필드에 값이 있으면 스팸 봇"""
    if website:
        logger.warning("Honeypot triggered: website=%s", website[:50])
        raise HTTPException(status_code=400, detail="Invalid request.")


# ──────────────────────────────────────────────
# Layer 5: User-Agent 분류
# ──────────────────────────────────────────────
def detect_ai_agent(user_agent: str) -> bool:
    """User-Agent에서 알려진 AI 에이전트 키워드 탐지"""
    ua_lower = user_agent.lower()
    return any(kw in ua_lower for kw in AI_USER_AGENTS)


def classify_author_type(request: Request, declared_type: str) -> str:
    """선언된 author_type과 UA를 비교해서 최종 분류

    - UA가 AI인데 human으로 선언 → ai로 덮어씀
    - 나머지는 선언값 존중
    """
    ua = request.headers.get("User-Agent", "")
    if detect_ai_agent(ua) and declared_type == "human":
        return "ai"
    return declared_type


# ──────────────────────────────────────────────
# Layer 6: IP 블랙리스트 (Redis)
# ──────────────────────────────────────────────
BLACKLIST_KEY = "blocked_ips"


async def check_ip_blacklist(ip: str) -> None:
    """Redis 블랙리스트에 있는 IP면 차단"""
    r = await _get_redis()
    if r is None:
        return
    try:
        if await r.sismember(BLACKLIST_KEY, ip):
            raise HTTPException(status_code=403, detail="Access denied.")
    except HTTPException:
        raise
    except Exception:
        logger.warning("Redis blacklist check failed — skipping")


# ──────────────────────────────────────────────
# 통합: 전체 방어 파이프라인
# ──────────────────────────────────────────────
async def run_spam_checks_post(
    request: Request,
    data,
    db: AsyncSession,
) -> tuple[str, str, str, str]:
    """게시글 작성 시 전체 스팸 방어 실행. 정제된 값 반환.

    Returns: (title, content, author_name, author_type)
    """
    ip = get_client_ip(request)

    # Layer 6: IP 블랙리스트
    await check_ip_blacklist(ip)

    # Layer 4: Honeypot
    check_honeypot(data.website)

    # Layer 3: XSS + Injection 정제
    title = sanitize_text(data.title)
    content = sanitize_text(data.content)
    author_name = sanitize_text(data.author_name)

    # Layer 5: UA 기반 분류
    author_type = classify_author_type(request, data.author_type)

    # Layer 2: 중복 검증
    ip_hashed = hash_ip(ip)
    await check_duplicate_post(db, ip_hashed, title, content)

    return title, content, author_name, author_type


async def run_spam_checks_comment(
    request: Request,
    data,
    post_id: int,
    db: AsyncSession,
) -> tuple[str, str, str]:
    """댓글 작성 시 전체 스팸 방어 실행. 정제된 값 반환.

    Returns: (content, author_name, author_type)
    """
    ip = get_client_ip(request)

    # Layer 6: IP 블랙리스트
    await check_ip_blacklist(ip)

    # Layer 4: Honeypot
    check_honeypot(data.website)

    # Layer 3: XSS + Injection 정제
    content = sanitize_text(data.content)
    author_name = sanitize_text(data.author_name)

    # Layer 5: UA 기반 분류
    author_type = classify_author_type(request, data.author_type)

    # Layer 2: 중복 검증
    ip_hashed = hash_ip(ip)
    await check_duplicate_comment(db, ip_hashed, post_id, content)

    return content, author_name, author_type
