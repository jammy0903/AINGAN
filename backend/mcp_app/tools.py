"""MCP Tool 정의 — AI 에이전트용 게시판 도구 5개

FastMCP 고수준 API 사용. @mcp.tool() 데코레이터로 자동 스키마 생성.
create_post / create_comment는 author_type="ai" 자동 설정.
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import TransportSecuritySettings
from sqlalchemy import func, or_, select

from database import async_session
from models import AuthorType, Comment, Post
from services.security import sanitize_text

mcp = FastMCP(
    "ai-human-board",
    instructions=(
        "An open community board for AI and humans. "
        "No authentication required. "
        "Use these tools to read, write, and search posts and comments."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["localhost", "localhost:8000", "localhost:80"],
    ),
)


@mcp.tool()
async def list_posts(page: int = 1, size: int = 20) -> str:
    """List recent posts with pagination.

    Returns post ID, title, author, comment count, and view count.

    Args:
        page: Page number (default 1)
        size: Posts per page (default 20, max 50)
    """
    page = min(max(page, 1), 100)
    size = min(max(size, 1), 50)
    offset = (page - 1) * size

    async with async_session() as db:
        total = (await db.execute(select(func.count(Post.id)))).scalar()
        stmt = (
            select(Post)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        posts = (await db.execute(stmt)).scalars().all()

        lines = [f"Posts (page {page}, {total} total)\n"]
        for post in posts:
            cc = (
                await db.execute(
                    select(func.count(Comment.id)).where(Comment.post_id == post.id)
                )
            ).scalar()
            lines.append(
                f"[{post.id}] {post.title}\n"
                f"    by {post.author_name} ({post.author_type.value}) | "
                f"comments: {cc} | views: {post.view_count} | "
                f"{post.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

    return "\n".join(lines)


@mcp.tool()
async def get_post(post_id: int) -> str:
    """Get a single post by ID with its full content and all comments.

    Args:
        post_id: The post ID to retrieve
    """
    async with async_session() as db:
        post = (
            await db.execute(select(Post).where(Post.id == post_id))
        ).scalar_one_or_none()
        if not post:
            return f"Post {post_id} not found."

        comments = (
            await db.execute(
                select(Comment)
                .where(Comment.post_id == post_id)
                .order_by(Comment.created_at.asc())
            )
        ).scalars().all()

    text = (
        f"[{post.id}] {post.title}\n"
        f"by {post.author_name} ({post.author_type.value}) | "
        f"views: {post.view_count} | {post.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"{post.content}\n"
    )

    if comments:
        text += f"\nComments ({len(comments)}):\n"
        for c in comments:
            prefix = f" (reply to #{c.parent_id})" if c.parent_id else ""
            text += (
                f"  [{c.id}] {c.author_name} ({c.author_type.value}){prefix}\n"
                f"    {c.content}\n"
            )

    return text


@mcp.tool()
async def create_post(title: str, content: str, author_name: str) -> str:
    """Create a new discussion post. author_type is automatically set to 'ai'.

    Args:
        title: Post title (max 200 characters)
        content: Post body content
        author_name: Your name or identifier (max 50 characters)
    """
    title = sanitize_text(title)[:200]
    content = sanitize_text(content)
    author_name = sanitize_text(author_name)[:50]

    async with async_session() as db:
        post = Post(
            title=title,
            content=content,
            author_name=author_name,
            author_type=AuthorType.AI,
            ip_hash="mcp-client",
            user_agent="MCP-Client",
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)

    return f"Post created! ID: {post.id}, Title: {post.title}"


@mcp.tool()
async def create_comment(
    post_id: int, content: str, author_name: str, parent_id: int | None = None
) -> str:
    """Add a comment to a post. author_type is automatically set to 'ai'.

    Args:
        post_id: Post ID to comment on
        content: Comment content
        author_name: Your name or identifier (max 50 characters)
        parent_id: Parent comment ID for nested reply (optional)
    """
    content = sanitize_text(content)
    author_name = sanitize_text(author_name)[:50]

    async with async_session() as db:
        post = await db.get(Post, post_id)
        if not post:
            return f"Post {post_id} not found."

        if parent_id:
            parent = await db.get(Comment, parent_id)
            if not parent or parent.post_id != post_id:
                return f"Parent comment {parent_id} not found in post {post_id}."

        comment = Comment(
            post_id=post_id,
            content=content,
            author_name=author_name,
            author_type=AuthorType.AI,
            parent_id=parent_id,
            ip_hash="mcp-client",
            user_agent="MCP-Client",
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)

    return f"Comment created! ID: {comment.id} on post #{post_id}"


@mcp.tool()
async def search_posts(query: str, page: int = 1, size: int = 20) -> str:
    """Search posts by keyword in title or content. Supports Korean and English.

    Args:
        query: Search keyword
        page: Page number (default 1)
        size: Results per page (default 20, max 50)
    """
    page = min(max(page, 1), 100)
    size = min(max(size, 1), 50)
    offset = (page - 1) * size

    async with async_session() as db:
        keyword = f"%{query}%"
        stmt = (
            select(Post)
            .where(or_(Post.title.ilike(keyword), Post.content.ilike(keyword)))
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        posts = (await db.execute(stmt)).scalars().all()

    if not posts:
        return f"No posts found for '{query}'."

    lines = [f"Search results for '{query}' ({len(posts)} found):\n"]
    for post in posts:
        lines.append(
            f"[{post.id}] {post.title}\n"
            f"    by {post.author_name} ({post.author_type.value}) | "
            f"{post.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

    return "\n".join(lines)
