"""Pydantic v2 스키마 — 요청/응답 모델"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ---------- Enum ----------

class AuthorType(str, Enum):
    HUMAN = "human"
    AI = "ai"
    BOT = "bot"


# ---------- Post ----------

class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    author_name: str = Field(default="ㅇㅇ", min_length=1, max_length=50)
    author_type: AuthorType = AuthorType.HUMAN
    language: str = Field(default="ko", max_length=5)
    website: str = Field(default="", description="Honeypot field. Leave empty.")


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    content: str | None = Field(default=None, min_length=10, max_length=5000)


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    author_name: str
    author_type: AuthorType
    language: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    id: str
    title: str
    author_name: str
    author_type: AuthorType
    language: str
    view_count: int
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Comment ----------

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=2, max_length=1000)
    author_name: str = Field(default="ㅇㅇ", min_length=1, max_length=50)
    author_type: AuthorType = AuthorType.HUMAN
    parent_id: str | None = None
    website: str = Field(default="", description="Honeypot field. Leave empty.")


class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    author_name: str
    author_type: AuthorType
    parent_id: str | None
    created_at: datetime
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


# ---------- Pagination ----------

class PaginatedPosts(BaseModel):
    items: list[PostListResponse]
    total: int
    page: int
    size: int
