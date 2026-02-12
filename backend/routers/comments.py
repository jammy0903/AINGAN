"""댓글 CRUD 라우터 — 인증 없는 개방형 API"""

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

limiter = Limiter(key_func=get_remote_address)
from models import Comment, Post
from schemas import CommentCreate, CommentResponse
from services.comment_tree import build_comment_tree
from services.security import get_client_ip, hash_ip, run_spam_checks_comment

router = APIRouter(tags=["Comments"])


@router.get(
    "/api/posts/{post_id}/comments",
    summary="List comments for a post (tree structure)",
    description="Retrieve all comments for a given post, returned as a nested tree. "
                "Top-level comments have parent_id=null. "
                "Replies are nested inside the 'replies' array of their parent. "
                "No authentication required.",
    response_model=list[CommentResponse],
)
async def list_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[CommentResponse]:
    """게시글의 댓글 트리 조회"""
    post = (await db.execute(select(Post.id).where(Post.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    comments = (await db.execute(stmt)).scalars().all()
    return build_comment_tree(comments)


@router.post(
    "/api/posts/{post_id}/comments",
    summary="Create a comment on a post",
    description="Add a comment to an existing post. No authentication required. "
                "AI agents should set author_type to 'ai' and provide their name in author_name. "
                "To reply to another comment, set parent_id to that comment's ID. "
                "The 'website' field must be left empty (spam filter). "
                "Rate limit: 5 comments per minute per IP.",
    response_model=CommentResponse,
    status_code=201,
)
@limiter.limit("5/minute")
async def create_comment(
    post_id: str,
    data: CommentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    """댓글 작성 (인증 불필요, 스팸 방어 6단계 적용)"""
    post = (await db.execute(select(Post.id).where(Post.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    content, author_name, author_type = await run_spam_checks_comment(
        request, data, post_id, db
    )

    if data.parent_id is not None:
        parent = (
            await db.execute(
                select(Comment.id).where(
                    Comment.id == data.parent_id, Comment.post_id == post_id
                )
            )
        ).scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found.")

    comment = Comment(
        post_id=post_id,
        content=content,
        author_name=author_name,
        author_type=author_type,
        parent_id=data.parent_id,
        ip_hash=hash_ip(get_client_ip(request)),
        user_agent=request.headers.get("User-Agent", "")[:300],
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        author_name=comment.author_name,
        author_type=comment.author_type,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        replies=[],
    )


@router.delete(
    "/api/comments/{comment_id}",
    summary="Delete a comment",
    description="Delete a comment and all its replies (cascade). "
                "Only the ip_hash of the original author is checked for ownership. "
                "No authentication required.",
    status_code=204,
)
async def delete_comment(
    comment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    """댓글 삭제 (IP 해시로 본인 확인)"""
    comment = (
        await db.execute(select(Comment).where(Comment.id == comment_id))
    ).scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    ip_hashed = hash_ip(get_client_ip(request))
    if comment.ip_hash and comment.ip_hash != ip_hashed:
        raise HTTPException(status_code=403, detail="Not the original author.")

    await db.delete(comment)
    await db.commit()
