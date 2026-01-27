from fastapi import Request
import time
from shared.utils import logger

# TODO: Create logger utility first or import standard logging
import logging
logger = logging.getLogger("api")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response
