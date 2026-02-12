"""migrate posts id to nanoid

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-02-12 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "b1c2d3e4f5g6"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 임시 컬럼 생성
    op.add_column("posts", sa.Column("id_new", sa.String(length=12), nullable=True))
    op.add_column("comments", sa.Column("id_new", sa.String(length=12), nullable=True))
    op.add_column("comments", sa.Column("post_id_new", sa.String(length=12), nullable=True))
    op.add_column("comments", sa.Column("parent_id_new", sa.String(length=12), nullable=True))

    conn = op.get_bind()

    # Python으로 nanoid 생성
    from nanoid import generate

    # 2. posts에 nanoid 할당
    posts_result = conn.execute(text("SELECT id FROM posts ORDER BY id"))
    posts = posts_result.fetchall()

    post_id_mapping = {}
    for (old_id,) in posts:
        new_id = generate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", 12)
        post_id_mapping[old_id] = new_id
        conn.execute(text("UPDATE posts SET id_new = :new_id WHERE id = :old_id"), {"new_id": new_id, "old_id": old_id})

    # 3. comments에 nanoid 할당
    comments_result = conn.execute(text("SELECT id, post_id, parent_id FROM comments ORDER BY id"))
    comments = comments_result.fetchall()

    comment_id_mapping = {}
    for (old_id, old_post_id, old_parent_id) in comments:
        new_id = generate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", 12)
        comment_id_mapping[old_id] = new_id
        new_post_id = post_id_mapping.get(old_post_id)
        new_parent_id = comment_id_mapping.get(old_parent_id) if old_parent_id else None

        conn.execute(
            text("UPDATE comments SET id_new = :new_id, post_id_new = :new_post_id, parent_id_new = :new_parent_id WHERE id = :old_id"),
            {"new_id": new_id, "new_post_id": new_post_id, "new_parent_id": new_parent_id, "old_id": old_id}
        )

    # 4. FK 삭제
    op.drop_constraint("comments_parent_id_fkey", "comments", type_="foreignkey")
    op.drop_constraint("comments_post_id_fkey", "comments", type_="foreignkey")

    # 5. posts의 PK 삭제 후 컬럼 교체
    op.drop_constraint("posts_pkey", "posts", type_="primary")
    op.drop_column("posts", "id")
    op.alter_column("posts", "id_new", new_column_name="id", nullable=False)
    op.execute("DROP SEQUENCE IF EXISTS posts_id_seq")
    op.create_primary_key("posts_pkey", "posts", ["id"])

    # 6. comments의 PK 삭제 후 컬럼 교체
    op.drop_constraint("comments_pkey", "comments", type_="primary")
    op.drop_column("comments", "id")
    op.drop_column("comments", "post_id")
    op.drop_column("comments", "parent_id")
    op.alter_column("comments", "id_new", new_column_name="id", nullable=False)
    op.alter_column("comments", "post_id_new", new_column_name="post_id", nullable=False)
    op.alter_column("comments", "parent_id_new", new_column_name="parent_id", nullable=True)
    op.execute("DROP SEQUENCE IF EXISTS comments_id_seq")
    op.create_primary_key("comments_pkey", "comments", ["id"])

    # 7. FK 재생성
    op.create_foreign_key("comments_post_id_fkey", "comments", "posts", ["post_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("comments_parent_id_fkey", "comments", "comments", ["parent_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    # downgrade는 구현하지 않음 (데이터 손실 위험)
    pass
