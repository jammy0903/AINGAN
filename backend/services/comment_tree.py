"""댓글 트리 변환 — flat 리스트를 중첩 트리로"""

from schemas import CommentResponse


def build_comment_tree(comments: list) -> list[CommentResponse]:
    """DB에서 가져온 flat 댓글 리스트를 parent_id 기반 트리로 변환"""
    node_map: dict[int, CommentResponse] = {}
    roots: list[CommentResponse] = []

    for c in comments:
        node = CommentResponse(
            id=c.id,
            post_id=c.post_id,
            content=c.content,
            author_name=c.author_name,
            author_type=c.author_type,
            parent_id=c.parent_id,
            created_at=c.created_at,
            replies=[],
        )
        node_map[c.id] = node

    for c in comments:
        node = node_map[c.id]
        if c.parent_id and c.parent_id in node_map:
            node_map[c.parent_id].replies.append(node)
        else:
            roots.append(node)

    return roots
