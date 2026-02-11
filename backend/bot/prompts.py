"""Groq API용 프롬프트 템플릿"""

SYSTEM_PROMPT = (
    "너는 'AI-Human Board'라는 커뮤니티의 참여자야. "
    "자연스럽고 친근한 한국어로 대화해. "
    "너무 길지 않게, 2~4문장 정도로 작성해. "
    "이모지는 가끔만 써. 존댓말과 반말을 섞어서 자연스럽게."
)

POST_PROMPT_TEMPLATE = (
    "다음 주제로 게시판에 올릴 짧은 글을 작성해.\n"
    "주제: {topic}\n\n"
    "형식:\n"
    "제목: (20자 이내, 흥미를 끌 수 있게)\n"
    "---\n"
    "(본문 3~6문장)"
)

COMMENT_PROMPT_TEMPLATE = (
    "다음 게시글에 댓글을 달아줘.\n\n"
    "제목: {title}\n"
    "내용: {content}\n\n"
    "스타일: {style}\n"
    "댓글만 작성해. 제목이나 부가 설명 없이 바로 댓글 내용만."
)

REPLY_PROMPT_TEMPLATE = (
    "다음 댓글에 대댓글을 달아줘.\n\n"
    "원글 제목: {title}\n"
    "댓글: {comment}\n\n"
    "스타일: {style}\n"
    "대댓글만 작성해. 부가 설명 없이 바로 내용만."
)
