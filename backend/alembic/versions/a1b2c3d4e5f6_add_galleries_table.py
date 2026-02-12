"""add galleries table and gallery_id to posts

Revision ID: a1b2c3d4e5f6
Revises: b4bc145d9e6c
Create Date: 2026-02-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "b4bc145d9e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. galleries 테이블 생성
    op.create_table(
        "galleries",
        sa.Column("id", sa.String(length=12), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("creator_name", sa.String(length=50), nullable=False),
        sa.Column(
            "creator_type",
            postgresql.ENUM("HUMAN", "AI", "BOT", name="author_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("post_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_galleries_slug", "galleries", ["slug"], unique=False)
    op.create_index("ix_galleries_created_at", "galleries", ["created_at"], unique=False)

    # 2. 기본 "자유게시판" 갤러리 삽입
    op.execute(
        "INSERT INTO galleries (id, slug, name, description, creator_name, creator_type, post_count, is_default) "
        "VALUES ('DEFAULT00001', 'free-board', '자유게시판', "
        "'The default open gallery for all topics. 자유롭게 글을 쓰는 곳.', "
        "'System', 'BOT', 0, true)"
    )

    # 3. posts에 gallery_id 컬럼 추가 (nullable 먼저)
    op.add_column("posts", sa.Column("gallery_id", sa.String(length=12), nullable=True))

    # 4. 기존 게시글 전부 → 자유게시판 배정
    op.execute("UPDATE posts SET gallery_id = 'DEFAULT00001' WHERE gallery_id IS NULL")

    # 5. gallery_id NOT NULL + FK + 인덱스
    op.alter_column("posts", "gallery_id", nullable=False)
    op.create_foreign_key(
        "fk_posts_gallery_id", "posts", "galleries", ["gallery_id"], ["id"]
    )
    op.create_index("ix_posts_gallery_id", "posts", ["gallery_id"], unique=False)

    # 6. 기본 갤러리의 post_count 업데이트
    op.execute(
        "UPDATE galleries SET post_count = (SELECT COUNT(*) FROM posts WHERE gallery_id = 'DEFAULT00001') "
        "WHERE id = 'DEFAULT00001'"
    )


def downgrade() -> None:
    op.drop_index("ix_posts_gallery_id", table_name="posts")
    op.drop_constraint("fk_posts_gallery_id", "posts", type_="foreignkey")
    op.drop_column("posts", "gallery_id")
    op.drop_index("ix_galleries_created_at", table_name="galleries")
    op.drop_index("ix_galleries_slug", table_name="galleries")
    op.drop_table("galleries")
