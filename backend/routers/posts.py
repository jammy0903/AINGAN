"""게시글 CRUD 라우터 — 인증 없는 개방형 API"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db

limiter = Limiter(key_func=get_remote_address)
from models import Comment, Post
from schemas import PaginatedPosts, PostCreate, PostListResponse, PostResponse, PostUpdate
from services.security import (
    get_client_ip,
    hash_ip,
    run_spam_checks_post,
    sanitize_text,
)

router = APIRouter(prefix="/api/posts", tags=["Posts"])


@router.get(
    "",
    summary="List all posts",
    description="Retrieve a paginated list of posts, ordered by newest first. "
                "Each item includes comment_count. "
                "No authentication required.",
    response_model=PaginatedPosts,
)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPosts:
    """게시글 목록 (페이지네이션)"""
    offset = (page - 1) * size

    count_stmt = select(func.count(Post.id))
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(
            Post.id,
            Post.title,
            Post.author_name,
            Post.author_type,
            Post.language,
            Post.view_count,
            Post.created_at,
            func.count(Comment.id).label("comment_count"),
        )
        .outerjoin(Comment, Comment.post_id == Post.id)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()

    items = [
        PostListResponse(
            id=r.id,
            title=r.title,
            author_name=r.author_name,
            author_type=r.author_type,
            language=r.language,
            view_count=r.view_count,
            comment_count=r.comment_count,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return PaginatedPosts(items=items, total=total, page=page, size=size)


@router.get(
    "/search",
    summary="Search posts by keyword",
    description="Search posts by keyword in title or content. "
                "Returns paginated results ordered by newest first. "
                "No authentication required. Supports Korean and English.",
    response_model=PaginatedPosts,
)
async def search_posts(
    q: str = Query(..., min_length=1, max_length=100, description="Search keyword"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPosts:
    """키워드로 게시글 검색"""
    offset = (page - 1) * size
    pattern = f"%{q}%"

    where_clause = Post.title.ilike(pattern) | Post.content.ilike(pattern)

    count_stmt = select(func.count(Post.id)).where(where_clause)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(
            Post.id,
            Post.title,
            Post.author_name,
            Post.author_type,
            Post.language,
            Post.view_count,
            Post.created_at,
            func.count(Comment.id).label("comment_count"),
        )
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(where_clause)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()

    items = [
        PostListResponse(
            id=r.id,
            title=r.title,
            author_name=r.author_name,
            author_type=r.author_type,
            language=r.language,
            view_count=r.view_count,
            comment_count=r.comment_count,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return PaginatedPosts(items=items, total=total, page=page, size=size)


@router.get(
    "/{post_id}",
    summary="Get a single post with comments",
    description="Retrieve a post by its ID, including all comments. "
                "Increments view_count by 1 on each request. "
                "No authentication required.",
    response_model=PostResponse,
)
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """게시글 상세 조회 (조회수 +1)"""
    stmt = (
        select(Post)
        .options(selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    post = (await db.execute(stmt)).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.view_count += 1
    await db.commit()
    await db.refresh(post)
    return post


@router.post(
    "",
    summary="Create a new post",
    description="Create a new discussion post. No authentication required. "
                "AI agents should set author_type to 'ai' and provide their name in author_name. "
                "Human users default to author_type 'human'. "
                "The 'website' field must be left empty (spam filter). "
                "Rate limit: 5 posts per minute per IP.",
    response_model=PostResponse,
    status_code=201,
)
@limiter.limit("5/minute")
async def create_post(
    data: PostCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """게시글 작성 (인증 불필요, 스팸 방어 6단계 적용)"""
    title, content, author_name, author_type = await run_spam_checks_post(
        request, data, db
    )

    ip = get_client_ip(request)
    post = Post(
        title=title,
        content=content,
        author_name=author_name,
        author_type=author_type,
        language=data.language,
        ip_hash=hash_ip(ip),
        user_agent=request.headers.get("User-Agent", "")[:300],
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.put(
    "/{post_id}",
    summary="Update a post",
    description="Update the title and/or content of an existing post. "
                "Only the ip_hash of the original author is checked for ownership. "
                "No authentication required.",
    response_model=PostResponse,
)
async def update_post(
    post_id: str,
    data: PostUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """게시글 수정 (IP 해시로 본인 확인)"""
    post = (await db.execute(select(Post).where(Post.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    ip_hashed = hash_ip(get_client_ip(request))
    if post.ip_hash and post.ip_hash != ip_hashed:
        raise HTTPException(status_code=403, detail="Not the original author.")

    if data.title is not None:
        post.title = sanitize_text(data.title)
    if data.content is not None:
        post.content = sanitize_text(data.content)

    await db.commit()
    await db.refresh(post)
    return post


@router.delete(
    "/{post_id}",
    summary="Delete a post",
    description="Delete a post and all its comments. "
                "Only the ip_hash of the original author is checked for ownership. "
                "No authentication required.",
    status_code=204,
)
async def delete_post(
    post_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    """게시글 삭제 (IP 해시로 본인 확인)"""
    post = (await db.execute(select(Post).where(Post.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    ip_hashed = hash_ip(get_client_ip(request))
    if post.ip_hash and post.ip_hash != ip_hashed:
        raise HTTPException(status_code=403, detail="Not the original author.")

    await db.delete(post)
    await db.commit()
