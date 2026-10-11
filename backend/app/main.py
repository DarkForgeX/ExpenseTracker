import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analytics import router as analytics_router
from app.routers.expenses import router as expenses_router

load_dotenv()

app = FastAPI(
    title="ExpenseFlow API",
    description="API for managing personal expenses",
    version="1.0.0",
)

frontend_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}
configured_origin = os.getenv("FRONTEND_ORIGIN")
if configured_origin:
    frontend_origins.update(
        origin.strip()
        for origin in configured_origin.split(",")
        if origin.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(frontend_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses_router)
app.include_router(analytics_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ExpenseFlow API",
    }
