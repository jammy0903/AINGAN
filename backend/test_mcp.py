"""MCP 연결 테스트 스크립트

Usage (컨테이너 내부):
    python test_mcp.py

Usage (호스트):
    docker compose exec backend python test_mcp.py
"""

import asyncio
import sys

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


async def main():
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client

    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/mcp/sse"
    results = []

    print(f"Connecting to {url} ...\n")

    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. list_tools
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            expected = ["create_comment", "create_post", "get_post", "list_posts", "search_posts"]
            ok = names == expected
            results.append(("list_tools (5 tools)", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] list_tools → {names}")

            # 2. create_post
            r = await session.call_tool("create_post", {
                "title": "MCP Test",
                "content": "Automated test via test_mcp.py",
                "author_name": "test-bot",
            })
            text = r.content[0].text
            ok = "Post created!" in text
            results.append(("create_post", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] create_post → {text}")

            # extract post ID
            post_id = int(text.split("ID: ")[1].split(",")[0])

            # 3. get_post
            r = await session.call_tool("get_post", {"post_id": post_id})
            text = r.content[0].text
            ok = "MCP Test" in text and "test-bot (ai)" in text
            results.append(("get_post + author_type=ai", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] get_post → author_type=ai confirmed")

            # 4. create_comment
            r = await session.call_tool("create_comment", {
                "post_id": post_id,
                "content": "Test comment",
                "author_name": "test-bot",
            })
            text = r.content[0].text
            ok = "Comment created!" in text
            results.append(("create_comment", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] create_comment → {text}")

            # 5. search_posts
            r = await session.call_tool("search_posts", {"query": "MCP Test"})
            text = r.content[0].text
            ok = "MCP Test" in text
            results.append(("search_posts", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] search_posts → found")

            # 6. list_posts
            r = await session.call_tool("list_posts", {"page": 1, "size": 3})
            text = r.content[0].text
            ok = "Posts (page 1" in text
            results.append(("list_posts", ok))
            print(f"  [{'PASS' if ok else 'FAIL'}] list_posts → page 1 returned")

    # Summary
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("All tests passed!")
    else:
        print("Some tests failed:")
        for name, ok in results:
            if not ok:
                print(f"  FAIL: {name}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
