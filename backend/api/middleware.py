from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import time
import logging
from collections import defaultdict
from backend.config.settings import settings

logger = logging.getLogger("api")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = defaultdict(list)
        self.limit = settings.RATE_LIMIT_PER_MINUTE

    async def dispatch(self, request: StarletteRequest, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old records
        self.rate_limit_records[client_ip] = [
            t for t in self.rate_limit_records[client_ip] 
            if current_time - t < 60
        ]
        
        if len(self.rate_limit_records[client_ip]) >= self.limit:
            return Response(content="Rate limit exceeded", status_code=429)
            
        self.rate_limit_records[client_ip].append(current_time)
        return await call_next(request)

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

