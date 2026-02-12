"""FastAPI dependencies — 인증 체크 등"""
from fastapi import HTTPException, Request

from routers.auth import SESSION_COOKIE_NAME, get_redis, verify_session


async def admin_required(request: Request):
    """관리자 인증 필수 체크"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    redis = await get_redis()
    try:
        is_authenticated = await verify_session(session_id, redis)
        if not is_authenticated:
            raise HTTPException(
                status_code=401,
                detail="Admin authentication required"
            )
    finally:
        await redis.close()
