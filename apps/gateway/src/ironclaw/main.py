"""
FastAPI main application entry point for Iron Claw Gateway.
"""

import logging
from contextlib import asynccontextmanager

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import alarms, health, hitl, jobs, tabs, wake, chat, chat_cloud, speech, mobilerun, mobilerun_ws, openclaw, google_sheets
from .utils.auth import access_decision
from .utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ironclaw")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🦾 Iron Claw Gateway starting up...")
    settings = get_settings()

    # Log configuration (no secrets!)
    logger.info(f"Device: {settings.device_serial or 'auto-detect'}")
    logger.info(f"TCP Mode: {settings.use_tcp}")
    logger.info(f"Vapi configured: {bool(settings.vapi_api_key)}")
    logger.info(f"Telegram configured: {bool(settings.telegram_bot_token)}")
    if not (os.getenv("IRONCLAW_API_TOKEN") or settings.api_token):
        logger.warning("IRONCLAW_API_TOKEN is unset. API routes accept local clients.")

    yield

    logger.info("🦾 Iron Claw Gateway shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Iron Claw Gateway",
        description="Mobile-First Autonomous Agent Architecture",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # CORS stays on an explicit origin list. Debug mode does not open it to every site.
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    extra_origins = os.getenv("IRONCLAW_CORS_ORIGINS", "")
    if extra_origins.strip():
        origins.extend(origin.strip() for origin in extra_origins.split(",") if origin.strip())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_api_token(request, call_next):
        decision = access_decision(
            request.url.path,
            request.method,
            request.headers.get("authorization"),
            os.getenv("IRONCLAW_API_TOKEN", settings.api_token),
            request.query_params.get("token"),
        )
        if decision is not None:
            status_code, detail = decision
            return JSONResponse(status_code=status_code, content={"detail": detail})
        return await call_next(request)

    # Register routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Job Hunter"])
    app.include_router(alarms.router, prefix="/api/v1/alarms", tags=["Temporal Guardian"])
    app.include_router(tabs.router, prefix="/api/v1/tabs", tags=["Tab Manager"])
    app.include_router(wake.router, prefix="/api/v1/wake", tags=["Active Interrupter"])
    app.include_router(hitl.router, prefix="/api/v1/hitl", tags=["Human-in-the-Loop"])
    app.include_router(chat.router, prefix="/api", tags=["Chat & Web"])
    app.include_router(chat_cloud.router, prefix="/api", tags=["Cloud Chat"])
    app.include_router(speech.router, prefix="/api/v1/speech", tags=["Speech-to-Text"])
    app.include_router(mobilerun.router, prefix="/api/v1/mobilerun", tags=["MobileRun Cloud"])
    app.include_router(mobilerun_ws.router, prefix="/api/v1/mobilerun", tags=["MobileRun WebSocket"])
    app.include_router(openclaw.router, prefix="/openclaw", tags=["OpenClaw Integration"])
    app.include_router(google_sheets.router, prefix="/api/v1/sheets", tags=["Google Sheets"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "ironclaw.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
