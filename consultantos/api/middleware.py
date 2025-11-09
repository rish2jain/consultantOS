"""
API middleware for performance optimizations

Features:
- Response caching headers (Cache-Control, ETag)
- Compression (handled by Uvicorn/Starlette)
- Request timing
- Conditional requests (If-None-Match)
"""
import hashlib
import json
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
import time

logger = logging.getLogger(__name__)


class CachingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add caching headers to API responses

    Features:
    - Automatic ETag generation for GET requests
    - Conditional request handling (304 Not Modified)
    - Cache-Control headers based on route type
    """

    # Cache-Control policies by route pattern
    CACHE_POLICIES = {
        "/health": "public, max-age=60",  # 1 minute
        "/reports/": "private, max-age=3600",  # 1 hour for report metadata
        "/metrics": "private, no-cache",  # Always fresh
        "/analyze": "no-store",  # Never cache analysis requests
        "/api/": "private, max-age=300",  # 5 minutes for API data
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record start time
        start_time = time.time()

        # For GET requests, check If-None-Match header
        if request.method == "GET":
            if_none_match = request.headers.get("If-None-Match")

            # Call the endpoint
            response = await call_next(request)

            # Only process successful JSON responses
            if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
                # Generate ETag from response body with size limit to prevent OOM
                MAX_ETAG_SIZE = 10 * 1024 * 1024  # 10MB limit
                response_body = b""
                body_size = 0
                chunks = []
                
                async for chunk in response.body_iterator:
                    chunks.append(chunk)
                    body_size += len(chunk)
                    if body_size > MAX_ETAG_SIZE:
                        # Body too large, skip ETag generation
                        # Rebuild response stream from collected chunks
                        from starlette.responses import StreamingResponse
                        async def stream_chunks():
                            for c in chunks:
                                yield c
                            async for c in response.body_iterator:
                                yield c
                        
                        duration_ms = (time.time() - start_time) * 1000
                        headers = MutableHeaders(response.headers)
                        headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
                        return StreamingResponse(
                            stream_chunks(),
                            status_code=response.status_code,
                            headers=headers,
                            media_type=response.media_type
                        )
                
                # Combine all chunks
                response_body = b"".join(chunks)
                etag = self._generate_etag(response_body)

                # Check if client has the same version
                if if_none_match and if_none_match == etag:
                    return Response(status_code=304, headers={"ETag": etag})

                # Add cache headers
                cache_control = self._get_cache_control(request.url.path)
                headers = MutableHeaders(response.headers)
                headers["ETag"] = etag
                headers["Cache-Control"] = cache_control

                # Add timing header
                duration_ms = (time.time() - start_time) * 1000
                headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type
                )

            return response
        else:
            # For non-GET requests, just add timing
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            return response

    def _generate_etag(self, content: bytes) -> str:
        """
        Generate ETag from response content

        Args:
            content: Response body bytes

        Returns:
            ETag string (MD5 hash)
        """
        return f'"{hashlib.md5(content).hexdigest()}"'

    def _get_cache_control(self, path: str) -> str:
        """
        Get Cache-Control header value for route

        Args:
            path: Request path

        Returns:
            Cache-Control header value
        """
        # Check for exact matches first
        for pattern, policy in self.CACHE_POLICIES.items():
            if path.startswith(pattern):
                return policy

        # Default: no caching
        return "no-cache, no-store, must-revalidate"


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add compression hints

    Note: Actual compression is handled by Uvicorn with --use-colors flag
    This middleware just ensures proper headers are set
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add Vary header for proper caching with compression
        if "Accept-Encoding" in request.headers:
            response.headers["Vary"] = "Accept-Encoding"

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request timing and log slow requests

    Logs warnings for requests exceeding threshold
    """

    SLOW_REQUEST_THRESHOLD_MS = 1000  # 1 second

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        # Log slow requests
        if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"({duration_ms:.2f}ms, threshold: {self.SLOW_REQUEST_THRESHOLD_MS}ms)"
            )

        return response
