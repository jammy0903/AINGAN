"""MCP SSE 서버 — /mcp/sse (인증 없음)

FastMCP.sse_app()으로 Starlette 앱 생성 후 FastAPI에 마운트.
IP당 SSE 연결 3개 제한은 미들웨어로 구현.
"""

from collections import defaultdict

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_app.tools import mcp

MAX_SSE_PER_IP = 3
_active_connections: dict[str, int] = defaultdict(int)


class SSERateLimitMiddleware(BaseHTTPMiddleware):
    """IP당 SSE 연결 수 제한 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/sse"):
            client_ip = request.client.host if request.client else "unknown"
            if _active_connections[client_ip] >= MAX_SSE_PER_IP:
                return JSONResponse(
                    {"error": "Too many SSE connections. Max 3 per IP."},
                    status_code=429,
                )
            _active_connections[client_ip] += 1
            try:
                response = await call_next(request)
                return response
            finally:
                _active_connections[client_ip] -= 1
                if _active_connections[client_ip] <= 0:
                    del _active_connections[client_ip]
        return await call_next(request)


mcp_starlette_app = mcp.sse_app()
mcp_starlette_app.add_middleware(SSERateLimitMiddleware)
