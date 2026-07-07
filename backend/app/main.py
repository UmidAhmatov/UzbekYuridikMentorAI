from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.career import router as career_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.legal import router as legal_router
from app.api.roadmap import router as roadmap_router
from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.services.scheduler import scheduler_status, start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    lifespan=lifespan,
)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(roadmap_router, prefix="/api")
app.include_router(career_router, prefix="/api")
app.include_router(legal_router, prefix="/api")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.project_name,
        "environment": settings.environment,
        "scheduler": scheduler_status(),
    }
