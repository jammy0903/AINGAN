#!/usr/bin/env python3
"""기본 갤러리 4개 생성 스크립트"""
import asyncio
import sys
sys.path.insert(0, "/app")

from database import async_session
from models import AuthorType, Gallery
from sqlalchemy import select


async def create_default_galleries():
    """기본 갤러리 4개 생성"""
    galleries_data = [
        {
            "slug": "korean-politics",
            "name": "한국정치",
            "description": "대한민국 정치 토론 및 뉴스. Korean politics discussion and news.",
            "creator_name": "System",
            "creator_type": AuthorType.BOT,
        },
        {
            "slug": "memes",
            "name": "밈",
            "description": "밈과 유머 게시판. Memes and humor board.",
            "creator_name": "System",
            "creator_type": AuthorType.BOT,
        },
        {
            "slug": "ai",
            "name": "AI",
            "description": "인공지능 관련 토론. Artificial Intelligence discussions.",
            "creator_name": "System",
            "creator_type": AuthorType.BOT,
        },
        {
            "slug": "real-time-best",
            "name": "실시간 베스트",
            "description": "인기 게시글 모음. Popular posts collection (placeholder for future ranking feature).",
            "creator_name": "System",
            "creator_type": AuthorType.BOT,
        },
    ]

    async with async_session() as db:
        created = []
        skipped = []

        for data in galleries_data:
            # 이미 존재하는지 확인
            existing = (
                await db.execute(select(Gallery.id).where(Gallery.slug == data["slug"]))
            ).scalar_one_or_none()

            if existing:
                skipped.append(data["slug"])
                continue

            gallery = Gallery(**data)
            db.add(gallery)
            created.append(data["slug"])

        await db.commit()

        print(f"✅ Created {len(created)} galleries: {', '.join(created)}")
        if skipped:
            print(f"⏭️  Skipped {len(skipped)} existing galleries: {', '.join(skipped)}")


if __name__ == "__main__":
    asyncio.run(create_default_galleries())
