"""게시글 쿼리 서비스 — 복잡한 SQLAlchemy 로직 분리"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Comment, Gallery, Post
from schemas import PostListResponse


async def fetch_post_list(
    db: AsyncSession,
    page: int,
    size: int,
) -> tuple[list[PostListResponse], int]:
    """게시글 목록 조회 (페이지네이션)"""
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
            Gallery.slug.label("gallery_slug"),
            Gallery.name.label("gallery_name"),
        )
        .join(Gallery, Gallery.id == Post.gallery_id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .group_by(Post.id, Gallery.slug, Gallery.name)
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
            gallery_slug=r.gallery_slug,
            gallery_name=r.gallery_name,
            created_at=r.created_at,
        )
        for r in rows
    ]

    return items, total


async def search_post_list(
    db: AsyncSession,
    query: str,
    page: int,
    size: int,
) -> tuple[list[PostListResponse], int]:
    """게시글 검색 (키워드)"""
    offset = (page - 1) * size
    pattern = f"%{query}%"

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
            Gallery.slug.label("gallery_slug"),
            Gallery.name.label("gallery_name"),
        )
        .join(Gallery, Gallery.id == Post.gallery_id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(where_clause)
        .group_by(Post.id, Gallery.slug, Gallery.name)
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
            gallery_slug=r.gallery_slug,
            gallery_name=r.gallery_name,
            created_at=r.created_at,
        )
        for r in rows
    ]

    return items, total


async def get_post_with_gallery(
    db: AsyncSession,
    post_id: str,
) -> Post | None:
    """게시글 상세 조회 (갤러리 정보 포함)"""
    stmt = (
        select(Post)
        .options(selectinload(Post.comments), selectinload(Post.gallery))
        .where(Post.id == post_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()
