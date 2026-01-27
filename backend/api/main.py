from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Unified GenAI Platform API",
    description="API Gateway for CX, Sales, and Marketing Agents",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

from fastapi.middleware.gzip import GZipMiddleware
from backend.api.middleware import RateLimitMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)


from backend.api.routers import chat, health, analytics, marketing, payments, search, social, calendar

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["marketing"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(social.router, prefix="/api/v1/social", tags=["social"])
app.include_router(calendar.router, prefix="/api/v1/calendar", tags=["calendar"])
app.include_router(health.router, tags=["health"])

@app.get("/")
async def root():
    return {"message": "Unified GenAI Platform API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
