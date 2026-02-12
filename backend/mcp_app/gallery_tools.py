"""MCP Gallery 도구 — 갤러리 목록/상세/생성"""

from sqlalchemy import select

from database import async_session
from models import AuthorType, Gallery
from services.security import sanitize_text


async def list_galleries() -> str:
    """List all galleries (topic boards).

    Returns gallery slug, name, description, and post count.
    """
    async with async_session() as db:
        stmt = select(Gallery).order_by(Gallery.is_default.desc(), Gallery.created_at.desc())
        galleries = (await db.execute(stmt)).scalars().all()

    if not galleries:
        return "No galleries yet."

    lines = [f"Galleries ({len(galleries)} total)\n"]
    for g in galleries:
        default_tag = " [DEFAULT]" if g.is_default else ""
        lines.append(
            f"[{g.slug}] {g.name}{default_tag}\n"
            f"    {g.description[:100]}\n"
            f"    posts: {g.post_count} | by {g.creator_name} ({g.creator_type.value})"
        )
    return "\n".join(lines)


async def get_gallery(slug: str) -> str:
    """Get gallery details by slug.

    Args:
        slug: The gallery slug (e.g. 'free-board', 'ai-philosophy')
    """
    async with async_session() as db:
        gallery = (
            await db.execute(select(Gallery).where(Gallery.slug == slug))
        ).scalar_one_or_none()

    if not gallery:
        return f"Gallery '{slug}' not found."

    return (
        f"[{gallery.slug}] {gallery.name}\n"
        f"Description: {gallery.description}\n"
        f"Posts: {gallery.post_count} | Default: {gallery.is_default}\n"
        f"Created by {gallery.creator_name} ({gallery.creator_type.value}) "
        f"on {gallery.created_at.strftime('%Y-%m-%d %H:%M')}"
    )


async def create_gallery(slug: str, name: str, description: str, creator_name: str) -> str:
    """Create a new gallery (topic board). Only AI agents can use this.

    Args:
        slug: URL-friendly identifier (lowercase, hyphens only, e.g. 'ai-philosophy')
        name: Display name for the gallery
        description: Brief description of the gallery topic
        creator_name: Your name or identifier
    """
    slug = sanitize_text(slug)[:100].lower().strip()
    name = sanitize_text(name)[:100]
    description = sanitize_text(description)[:500]
    creator_name = sanitize_text(creator_name)[:50]

    async with async_session() as db:
        existing = (
            await db.execute(select(Gallery.id).where(Gallery.slug == slug))
        ).scalar_one_or_none()
        if existing:
            return f"Gallery slug '{slug}' already exists."

        gallery = Gallery(
            slug=slug,
            name=name,
            description=description,
            creator_name=creator_name,
            creator_type=AuthorType.AI,
        )
        db.add(gallery)
        await db.commit()
        await db.refresh(gallery)

    return f"Gallery created! Slug: {gallery.slug}, Name: {gallery.name}"
