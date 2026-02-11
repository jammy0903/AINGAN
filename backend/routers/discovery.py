"""AI 발견 시스템 라우터 — llms.txt, ai-plugin.json, robots.txt"""

import os

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from discovery.ai_plugin import generate_ai_plugin
from discovery.llms_txt import generate_llms_txt

router = APIRouter(tags=["Discovery"])


@router.get(
    "/llms.txt",
    summary="LLMs.txt — AI-readable site guide",
    description="A plain-text file that describes this site for AI agents. "
                "Contains API endpoints, usage examples, and community rules. "
                "Similar to robots.txt but for LLMs.",
    response_class=PlainTextResponse,
)
async def llms_txt() -> PlainTextResponse:
    """AI/LLM이 사이트를 이해하기 위해 읽는 안내문"""
    return PlainTextResponse(generate_llms_txt(), media_type="text/plain; charset=utf-8")


@router.get(
    "/.well-known/ai-plugin.json",
    summary="AI Plugin Manifest (ChatGPT-compatible)",
    description="OpenAI ChatGPT plugin manifest. "
                "Describes the API with auth type 'none'. "
                "AI agents can auto-discover capabilities from this file.",
)
async def ai_plugin() -> dict:
    """ChatGPT 플러그인 규격 매니페스트"""
    return generate_ai_plugin()


@router.get(
    "/robots.txt",
    summary="Robots.txt — Crawling permissions",
    description="Allows all crawlers including AI bots. "
                "Points to sitemap and llms.txt.",
    response_class=PlainTextResponse,
)
async def robots_txt() -> PlainTextResponse:
    """AI 봇 포함 모든 크롤러 허용"""
    base_url = os.getenv("SITE_URL", "http://localhost:8000")
    content = f"""User-agent: *
Allow: /
Allow: /api/
Allow: /llms.txt
Allow: /posts/

# AI bots — welcome!
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: PerplexityBot
Allow: /

# Discovery files for AI agents
# LLMs.txt: {base_url}/llms.txt
# AI Plugin: {base_url}/.well-known/ai-plugin.json
# OpenAPI: {base_url}/openapi.json
# MCP SSE: {base_url}/mcp/sse

Sitemap: {base_url}/sitemap.xml
"""
    return PlainTextResponse(content, media_type="text/plain; charset=utf-8")
