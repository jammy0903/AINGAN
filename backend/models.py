"""SQLAlchemy 모델 — Post, Comment"""

import enum
from datetime import datetime

from nanoid import generate
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

_NANOID_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_NANOID_SIZE = 12


def _generate_nanoid() -> str:
    """URL-safe 12자리 nanoid 생성"""
    return generate(_NANOID_ALPHABET, _NANOID_SIZE)


class AuthorType(str, enum.Enum):
    HUMAN = "human"
    AI = "ai"
    BOT = "bot"


class Post(Base):
    """게시글 모델"""

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_generate_nanoid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False, default="ㅇㅇ")
    author_type: Mapped[AuthorType] = mapped_column(
        Enum(AuthorType, name="author_type_enum"),
        nullable=False,
        default=AuthorType.HUMAN,
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="ko")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_posts_created_at", "created_at"),
        Index("ix_posts_author_type", "author_type"),
    )


class Comment(Base):
    """댓글 모델 — 대댓글은 parent_id 자기참조"""

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=_generate_nanoid)
    post_id: Mapped[str] = mapped_column(
        String(12), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False, default="ㅇㅇ")
    author_type: Mapped[AuthorType] = mapped_column(
        Enum(AuthorType, name="author_type_enum", create_type=False),
        nullable=False,
        default=AuthorType.HUMAN,
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(12), ForeignKey("comments.id", ondelete="CASCADE")
    )
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    post: Mapped["Post"] = relationship(back_populates="comments")
    parent: Mapped["Comment | None"] = relationship(
        remote_side=[id], backref="replies"
    )

    __table_args__ = (
        Index("ix_comments_post_id", "post_id"),
        Index("ix_comments_created_at", "created_at"),
    )
