"""관리자 인증 라우터 — 세션 기반 로그인 (bcrypt 해싱)"""
import os
import secrets
from datetime import timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from redis import asyncio as aioredis

router = APIRouter(prefix="/api/auth", tags=["Auth"])

ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "dev-secret-key")
SESSION_COOKIE_NAME = "admin_session"
SESSION_EXPIRE_SECONDS = 3600 * 24  # 24시간


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str


async def get_redis():
    """Redis 클라이언트 가져오기"""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return await aioredis.from_url(redis_url, decode_responses=True)


async def create_session(redis: aioredis.Redis) -> str:
    """새 세션 생성"""
    session_id = secrets.token_urlsafe(32)
    await redis.setex(
        f"session:{session_id}",
        SESSION_EXPIRE_SECONDS,
        "admin"
    )
    return session_id


async def verify_session(session_id: str | None, redis: aioredis.Redis) -> bool:
    """세션 유효성 검증"""
    if not session_id:
        return False

    user = await redis.get(f"session:{session_id}")
    return user == "admin"


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, response: Response) -> LoginResponse:
    """관리자 로그인 (bcrypt 검증)"""
    if not ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Admin password not configured")

    # bcrypt로 비밀번호 검증
    try:
        password_bytes = data.password.encode('utf-8')
        hash_bytes = ADMIN_PASSWORD_HASH.encode('utf-8')
        is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        is_valid = False

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid password")

    redis = await get_redis()
    try:
        session_id = await create_session(redis)

        # 쿠키 설정
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_EXPIRE_SECONDS,
            httponly=True,
            samesite="lax",
        )

        return LoginResponse(success=True, message="Logged in successfully")
    finally:
        await redis.close()


@router.post("/logout")
async def logout(request: Request, response: Response):
    """관리자 로그아웃"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    if session_id:
        redis = await get_redis()
        try:
            await redis.delete(f"session:{session_id}")
        finally:
            await redis.close()

    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"success": True, "message": "Logged out successfully"}


@router.get("/check")
async def check_auth(request: Request):
    """현재 인증 상태 확인"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    redis = await get_redis()
    try:
        is_authenticated = await verify_session(session_id, redis)
        return {"authenticated": is_authenticated}
    finally:
        await redis.close()
