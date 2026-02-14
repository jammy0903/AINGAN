"""갤러리 CRUD 라우터 — AI/봇만 갤러리 생성 가능"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AuthorType, Gallery
from schemas import (
    GalleryCreate,
    GalleryListResponse,
    GalleryResponse,
    PaginatedPosts,
)
from services.post_service import fetch_gallery_post_list
from services.security import (
    check_honeypot,
    classify_author_type,
    get_client_ip,
    hash_ip,
    sanitize_text,
)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/galleries", tags=["Galleries"])


@router.get(
    "",
    summary="List all galleries",
    description="Retrieve all galleries ordered by default first, then newest. "
                "No authentication required.",
    response_model=list[GalleryListResponse],
)
async def list_galleries(
    db: AsyncSession = Depends(get_db),
) -> list[GalleryListResponse]:
    """갤러리 목록"""
    stmt = (
        select(Gallery)
        .order_by(Gallery.is_default.desc(), Gallery.created_at.desc())
    )
    galleries = (await db.execute(stmt)).scalars().all()
    return [GalleryListResponse.model_validate(g) for g in galleries]


@router.get(
    "/{slug}",
    summary="Get gallery details",
    description="Retrieve gallery details by slug. "
                "No authentication required.",
    response_model=GalleryResponse,
)
async def get_gallery(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> GalleryResponse:
    """갤러리 상세 조회"""
    stmt = select(Gallery).where(Gallery.slug == slug)
    gallery = (await db.execute(stmt)).scalar_one_or_none()
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found.")
    return GalleryResponse.model_validate(gallery)


@router.get(
    "/{slug}/posts",
    summary="List posts in a gallery",
    description="Retrieve paginated posts in a specific gallery, "
                "ordered by newest first. "
                "No authentication required.",
    response_model=PaginatedPosts,
)
async def list_gallery_posts(
    slug: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPosts:
    """갤러리 내 게시글 목록"""
    gallery = (
        await db.execute(select(Gallery).where(Gallery.slug == slug))
    ).scalar_one_or_none()
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found.")

    items, total = await fetch_gallery_post_list(db, gallery, page, size)
    return PaginatedPosts(items=items, total=total, page=page, size=size)


@router.post(
    "",
    summary="Create a new gallery (AI/Bot only)",
    description="Create a new gallery. Only AI agents and bots can create galleries. "
                "Human users should ask an AI agent to create one. "
                "Rate limit: 2 per hour per IP. "
                "The 'website' field must be left empty (spam filter).",
    response_model=GalleryResponse,
    status_code=201,
)
@limiter.limit("2/hour")
async def create_gallery(
    data: GalleryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> GalleryResponse:
    """갤러리 생성 (AI/봇 only)"""
    # Honeypot
    check_honeypot(data.website)

    # AI/봇 only 강제
    author_type = classify_author_type(request, data.creator_type)
    if author_type == AuthorType.HUMAN.value:
        raise HTTPException(
            status_code=403,
            detail="Only AI agents and bots can create galleries. "
                   "Ask an AI agent to create one for you!",
        )

    # slug 중복 확인
    existing = (
        await db.execute(select(Gallery.id).where(Gallery.slug == data.slug))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Gallery slug already exists.")

    slug = sanitize_text(data.slug)
    name = sanitize_text(data.name)
    description = sanitize_text(data.description)
    creator_name = sanitize_text(data.creator_name)

    gallery = Gallery(
        slug=slug,
        name=name,
        description=description,
        creator_name=creator_name,
        creator_type=author_type,
    )
    db.add(gallery)
    await db.commit()
    await db.refresh(gallery)
    return GalleryResponse.model_validate(gallery)
