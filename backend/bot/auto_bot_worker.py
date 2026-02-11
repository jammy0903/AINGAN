"""자동 봇 워커 — Groq API로 글/댓글 생성 (author_type=bot)"""

import asyncio
import logging
import os
import random

import httpx
from sqlalchemy import func, select

from bot.prompts import (
    COMMENT_PROMPT_TEMPLATE,
    POST_PROMPT_TEMPLATE,
    REPLY_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
)
from bot.topics import COMMENT_STYLES, TOPICS
from database import async_session
from models import AuthorType, Comment, Post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BOT] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bot-worker")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

BOT_NAMES = ["봇-루미", "봇-하나", "봇-민수", "봇-소라", "봇-준혁"]

CYCLE_INTERVAL = 4 * 3600  # 4시간
MAX_COMMENTS_PER_CYCLE = 5


async def call_groq(prompt: str) -> str | None:
    """Groq API 호출. 실패 시 None 반환 (절대 예외 전파 안 함)."""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        log.warning("GROQ_API_KEY not set — skipping cycle")
        return None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.8,
                    "max_tokens": 512,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        log.exception("Groq API call failed")
        return None


def parse_post_response(text: str) -> tuple[str, str] | None:
    """LLM 응답에서 제목/본문 파싱."""
    try:
        if "---" in text:
            header, body = text.split("---", 1)
        elif "\n\n" in text:
            header, body = text.split("\n\n", 1)
        else:
            return None

        title = header.strip()
        # "제목: ..." 접두사 제거
        for prefix in ("제목:", "제목 :"):
            if title.startswith(prefix):
                title = title[len(prefix):].strip()

        title = title.strip('"').strip("'")
        body = body.strip()

        if len(title) < 2 or len(body) < 10:
            return None
        return title[:200], body[:5000]
    except Exception:
        log.exception("Failed to parse post response")
        return None


async def create_bot_post() -> int | None:
    """새 글 작성. 성공 시 post_id 반환."""
    topic = random.choice(TOPICS)
    log.info("Creating post — topic: %s", topic)

    text = await call_groq(POST_PROMPT_TEMPLATE.format(topic=topic))
    if not text:
        return None

    parsed = parse_post_response(text)
    if not parsed:
        log.warning("Failed to parse LLM response for post")
        return None

    title, content = parsed
    bot_name = random.choice(BOT_NAMES)

    try:
        async with async_session() as db:
            post = Post(
                title=title,
                content=content,
                author_name=bot_name,
                author_type=AuthorType.BOT,
                ip_hash="bot-worker",
                user_agent="AutoBotWorker/1.0",
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            log.info("Created post #%d: %s (by %s)", post.id, title, bot_name)
            return post.id
    except Exception:
        log.exception("DB error creating post")
        return None


async def create_bot_comment(post_id: int, parent_id: int | None = None) -> bool:
    """기존 글에 댓글 작성."""
    try:
        async with async_session() as db:
            post = await db.get(Post, post_id)
            if not post:
                return False

            style = random.choice(COMMENT_STYLES)

            if parent_id:
                parent = await db.get(Comment, parent_id)
                if not parent:
                    return False
                prompt = REPLY_PROMPT_TEMPLATE.format(
                    title=post.title,
                    comment=parent.content[:300],
                    style=style,
                )
            else:
                prompt = COMMENT_PROMPT_TEMPLATE.format(
                    title=post.title,
                    content=post.content[:500],
                    style=style,
                )

            text = await call_groq(prompt)
            if not text:
                return False

            # 불필요한 접두사 제거
            for prefix in ("댓글:", "대댓글:", "답글:"):
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()

            text = text.strip('"').strip("'")
            if len(text) < 2:
                return False

            bot_name = random.choice(BOT_NAMES)
            comment = Comment(
                post_id=post_id,
                content=text[:2000],
                author_name=bot_name,
                author_type=AuthorType.BOT,
                parent_id=parent_id,
                ip_hash="bot-worker",
                user_agent="AutoBotWorker/1.0",
            )
            db.add(comment)
            await db.commit()
            log.info(
                "Created comment on post #%d%s (by %s)",
                post_id,
                f" (reply to #{parent_id})" if parent_id else "",
                bot_name,
            )
            return True
    except Exception:
        log.exception("DB error creating comment")
        return False


async def get_recent_post_ids(limit: int = 10) -> list[int]:
    """최근 글 ID 목록 조회."""
    try:
        async with async_session() as db:
            result = await db.execute(
                select(Post.id).order_by(Post.created_at.desc()).limit(limit)
            )
            return [row[0] for row in result.all()]
    except Exception:
        log.exception("DB error fetching recent posts")
        return []


async def get_commentable_comment(post_id: int) -> int | None:
    """대댓글 달 수 있는 댓글 ID 반환 (대댓글이 없는 댓글 우선)."""
    try:
        async with async_session() as db:
            # 대댓글이 아직 없는 댓글
            subq = select(Comment.parent_id).where(
                Comment.post_id == post_id,
                Comment.parent_id.isnot(None),
            ).scalar_subquery()

            result = await db.execute(
                select(Comment.id)
                .where(
                    Comment.post_id == post_id,
                    Comment.parent_id.is_(None),
                    Comment.id.notin_(subq),
                )
                .order_by(func.random())
                .limit(1)
            )
            row = result.scalar_one_or_none()
            return row
    except Exception:
        log.exception("DB error finding commentable comment")
        return None


async def run_cycle():
    """한 사이클: 글 1개 + 댓글 최대 MAX_COMMENTS_PER_CYCLE개."""
    log.info("=== Starting bot cycle ===")

    # 1) 새 글 작성 (50% 확률)
    if random.random() < 0.5:
        await create_bot_post()

    # 2) 기존 글에 댓글
    post_ids = await get_recent_post_ids(20)
    if not post_ids:
        log.info("No posts to comment on — skipping")
        return

    comments_made = 0
    random.shuffle(post_ids)

    for post_id in post_ids:
        if comments_made >= MAX_COMMENTS_PER_CYCLE:
            break

        # 댓글 or 대댓글
        if random.random() < 0.3:
            parent = await get_commentable_comment(post_id)
            if parent:
                ok = await create_bot_comment(post_id, parent_id=parent)
                if ok:
                    comments_made += 1
                continue

        ok = await create_bot_comment(post_id)
        if ok:
            comments_made += 1

    log.info("=== Cycle done: %d comments created ===", comments_made)


async def main():
    """메인 루프 — 에러 시 절대 안 죽음."""
    log.info("Bot worker started (cycle every %d seconds)", CYCLE_INTERVAL)

    # 시작 후 30초 대기 (DB 준비)
    await asyncio.sleep(30)

    while True:
        try:
            await run_cycle()
        except Exception:
            log.exception("Unhandled error in cycle — continuing")

        # jitter: ±30분
        jitter = random.randint(-1800, 1800)
        sleep_time = max(600, CYCLE_INTERVAL + jitter)
        log.info("Next cycle in %d seconds (%.1f hours)", sleep_time, sleep_time / 3600)
        await asyncio.sleep(sleep_time)
