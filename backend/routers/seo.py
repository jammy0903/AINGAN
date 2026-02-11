"""SEO 라우터 — sitemap.xml + 게시글 SSR HTML (JSON-LD 포함)"""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Comment, Post
from seo.utils import generate_json_ld, generate_sitemap_xml

router = APIRouter()


@router.get(
    "/sitemap.xml",
    tags=["SEO"],
    summary="XML Sitemap",
    description="Dynamic sitemap listing all posts and key pages. "
                "Used by Google and other search engines for indexing.",
)
async def sitemap_xml(db: AsyncSession = Depends(get_db)) -> Response:
    """검색엔진용 동적 사이트맵"""
    stmt = select(Post).order_by(Post.created_at.desc()).limit(1000)
    posts = (await db.execute(stmt)).scalars().all()
    xml = generate_sitemap_xml(posts)
    return Response(content=xml, media_type="application/xml; charset=utf-8")


@router.get(
    "/posts/{post_id}",
    tags=["SEO"],
    summary="Post HTML page with JSON-LD",
    description="Server-rendered HTML page for a single post. "
                "Includes Schema.org DiscussionForumPosting JSON-LD, "
                "Open Graph meta tags, and full content for search engine indexing.",
    response_class=HTMLResponse,
)
async def post_detail_html(
    post_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Google 봇용 SSR 페이지 — JSON-LD + OG 메타태그"""
    post = (
        await db.execute(select(Post).where(Post.id == post_id))
    ).scalar_one_or_none()
    if not post:
        return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)

    comments = (
        await db.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
    ).scalars().all()

    comment_count = (
        await db.execute(
            select(func.count(Comment.id)).where(Comment.post_id == post_id)
        )
    ).scalar()

    json_ld = generate_json_ld(post, comments, comment_count)

    from jinja2 import Environment, FileSystemLoader
    import os

    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("post_detail.html")

    html = template.render(
        post=post,
        comments=comments,
        comment_count=comment_count,
        json_ld_str=json.dumps(json_ld, ensure_ascii=False),
    )
    return HTMLResponse(html)
