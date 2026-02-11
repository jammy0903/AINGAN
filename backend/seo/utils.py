"""SEO 유틸 — sitemap.xml 생성 + JSON-LD 스키마 마크업"""

import os
from datetime import datetime

from models import Comment, Post


def get_base_url() -> str:
    return os.getenv("SITE_URL", "http://localhost:8000")


def generate_sitemap_xml(posts: list[Post]) -> str:
    """동적 sitemap.xml 생성. 게시글 URL + 정적 페이지 포함."""
    base = get_base_url()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    urls = [
        f"""  <url>
    <loc>{base}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{base}/llms.txt</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""",
    ]

    for post in posts:
        lastmod = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else today
        urls.append(
            f"""  <url>
    <loc>{base}/posts/{post.id}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def generate_json_ld(post: Post, comments: list[Comment], comment_count: int) -> dict:
    """Schema.org DiscussionForumPosting JSON-LD 생성."""
    base = get_base_url()

    ld = {
        "@context": "https://schema.org",
        "@type": "DiscussionForumPosting",
        "headline": post.title,
        "text": post.content[:500],
        "url": f"{base}/posts/{post.id}",
        "author": {
            "@type": "Person",
            "name": post.author_name,
        },
        "datePublished": post.created_at.isoformat(),
        "dateModified": post.updated_at.isoformat() if post.updated_at else post.created_at.isoformat(),
        "interactionStatistic": {
            "@type": "InteractionCounter",
            "interactionType": "https://schema.org/CommentAction",
            "userInteractionCount": comment_count,
        },
    }

    if comments:
        ld["comment"] = [
            {
                "@type": "Comment",
                "text": c.content[:300],
                "author": {"@type": "Person", "name": c.author_name},
                "datePublished": c.created_at.isoformat(),
            }
            for c in comments[:20]
        ]

    return ld
