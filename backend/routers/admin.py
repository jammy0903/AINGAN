"""관리자 전용 API 라우터 — 통계, 관리 기능"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import admin_required
from models import AuthorType, Comment, Gallery, Post
from schemas import GalleryResponse, PostListResponse

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_required)],
)


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """관리자 대시보드 통계"""
    # 총 게시글, 댓글, 갤러리 수
    total_posts = (await db.execute(select(func.count(Post.id)))).scalar()
    total_comments = (await db.execute(select(func.count(Comment.id)))).scalar()
    total_galleries = (await db.execute(select(func.count(Gallery.id)))).scalar()

    # 작성자 타입별 게시글 수
    posts_by_type = {}
    for author_type in AuthorType:
        count = (
            await db.execute(
                select(func.count(Post.id)).where(Post.author_type == author_type)
            )
        ).scalar()
        posts_by_type[author_type.value] = count

    # 갤러리별 게시글 수 (상위 10개)
    gallery_stats = (
        await db.execute(
            select(Gallery.name, Gallery.post_count)
            .order_by(Gallery.post_count.desc())
            .limit(10)
        )
    ).all()

    # 최근 게시글 10개
    recent_posts = (
        await db.execute(
            select(Post).order_by(Post.created_at.desc()).limit(10)
        )
    ).scalars().all()

    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_galleries": total_galleries,
        "posts_by_type": posts_by_type,
        "top_galleries": [
            {"name": name, "post_count": count} for name, count in gallery_stats
        ],
        "recent_posts": [
            PostListResponse.model_validate(post) for post in recent_posts
        ],
    }


@router.get("/galleries")
async def get_all_galleries(db: AsyncSession = Depends(get_db)):
    """모든 갤러리 조회 (관리용)"""
    stmt = select(Gallery).order_by(Gallery.created_at.desc())
    galleries = (await db.execute(stmt)).scalars().all()

    return {
        "galleries": [GalleryResponse.model_validate(g) for g in galleries]
    }


@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """게시글 삭제 (관리자 전용)"""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 갤러리 post_count 감소
    gallery = await db.get(Gallery, post.gallery_id)
    if gallery and gallery.post_count > 0:
        gallery.post_count -= 1

    await db.delete(post)
    await db.commit()

    return {"success": True, "message": f"Post {post_id} deleted"}


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, db: AsyncSession = Depends(get_db)):
    """댓글 삭제 (관리자 전용)"""
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    await db.delete(comment)
    await db.commit()

    return {"success": True, "message": f"Comment {comment_id} deleted"}


@router.get("/posts")
async def get_all_posts(
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """모든 게시글 조회 (관리용, 페이지네이션)"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    total = (await db.execute(select(func.count(Post.id)))).scalar()
    stmt = (
        select(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    posts = (await db.execute(stmt)).scalars().all()

    return {
        "posts": [PostListResponse.model_validate(p) for p in posts],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/comments")
async def get_all_comments(
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """모든 댓글 조회 (관리용, 페이지네이션)"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    total = (await db.execute(select(func.count(Comment.id)))).scalar()
    stmt = (
        select(Comment)
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    comments = (await db.execute(stmt)).scalars().all()

    return {
        "comments": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content,
                "author_name": c.author_name,
                "author_type": c.author_type.value,
                "created_at": c.created_at,
            }
            for c in comments
        ],
        "total": total,
        "page": page,
        "size": size,
    }
