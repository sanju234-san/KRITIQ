import time
from fastapi import Request, HTTPException, status

class RateLimiter:
    def __init__(self, limit: int = 100, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests = {}  # ip -> list of timestamps

    async def __call__(self, request: Request):
        # Exclude documentation, health root, and schema files from rate limiting
        if request.url.path in ("/", "/openapi.json", "/docs", "/redoc"):
            return

        ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if ip not in self.requests:
            self.requests[ip] = []

        # Remove timestamps older than the window
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]

        if len(self.requests[ip]) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

        self.requests[ip].append(now)

# Instantiate a global rate limiter: 60 requests per minute
global_limiter = RateLimiter(limit=60, window=60)
