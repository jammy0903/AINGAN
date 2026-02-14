"""게시글 쿼리 서비스 — 단일 소스 원칙(Single Source of Truth)"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Comment, Gallery, Post
from schemas import PostListResponse, PostResponse


# ── 공통 변환 함수 (Single Source of Truth) ──


def to_post_response(post: Post) -> PostResponse:
    """Post ORM → PostResponse 변환 (유일한 변환 지점)"""
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author_name=post.author_name,
        author_type=post.author_type,
        language=post.language,
        view_count=post.view_count,
        gallery_slug=post.gallery.slug if post.gallery else "",
        gallery_name=post.gallery.name if post.gallery else "",
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


def to_post_list_item(row, gallery_slug: str, gallery_name: str) -> PostListResponse:
    """SQL Row → PostListResponse 변환 (유일한 변환 지점)"""
    return PostListResponse(
        id=row.id,
        title=row.title,
        author_name=row.author_name,
        author_type=row.author_type,
        language=row.language,
        view_count=row.view_count,
        comment_count=row.comment_count,
        gallery_slug=gallery_slug,
        gallery_name=gallery_name,
        created_at=row.created_at,
    )


# ── 공통 쿼리 ──


def _post_list_columns():
    """목록 조회용 공통 SELECT 컬럼"""
    return (
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


# ── 조회 함수 ──


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


async def increment_view_count(db: AsyncSession, post_id: str) -> None:
    """조회수 +1 (별도 호출)"""
    post = (await db.execute(select(Post).where(Post.id == post_id))).scalar_one_or_none()
    if post:
        post.view_count += 1
        await db.commit()


async def fetch_post_list(
    db: AsyncSession,
    page: int,
    size: int,
) -> tuple[list[PostListResponse], int]:
    """게시글 목록 조회 (페이지네이션)"""
    offset = (page - 1) * size

    total = (await db.execute(select(func.count(Post.id)))).scalar_one()

    stmt = (
        select(*_post_list_columns())
        .join(Gallery, Gallery.id == Post.gallery_id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .group_by(Post.id, Gallery.slug, Gallery.name)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()
    items = [to_post_list_item(r, r.gallery_slug, r.gallery_name) for r in rows]

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

    total = (await db.execute(select(func.count(Post.id)).where(where_clause))).scalar_one()

    stmt = (
        select(*_post_list_columns())
        .join(Gallery, Gallery.id == Post.gallery_id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(where_clause)
        .group_by(Post.id, Gallery.slug, Gallery.name)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()
    items = [to_post_list_item(r, r.gallery_slug, r.gallery_name) for r in rows]

    return items, total


async def fetch_gallery_post_list(
    db: AsyncSession,
    gallery: Gallery,
    page: int,
    size: int,
) -> tuple[list[PostListResponse], int]:
    """갤러리 내 게시글 목록 조회"""
    offset = (page - 1) * size

    total = (await db.execute(
        select(func.count(Post.id)).where(Post.gallery_id == gallery.id)
    )).scalar_one()

    stmt = (
        select(
            Post.id, Post.title, Post.author_name, Post.author_type,
            Post.language, Post.view_count, Post.created_at,
            func.count(Comment.id).label("comment_count"),
        )
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(Post.gallery_id == gallery.id)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()
    items = [to_post_list_item(r, gallery.slug, gallery.name) for r in rows]

    return items, total
