from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api import api_router
from app.core.config import settings
import app.db.models
import app.modules.service_reports.models
from app.db.base import Base
from app.db.session import AsyncSessionLocal
from app.modules.tracking.routes import router as tracking_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = AsyncSessionLocal.kw.get("bind")
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Startup table initialization note: {e}")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8081",
        "http://192.168.1.21:8081",
        "http://192.168.1.15:5173",
        "https://evio.staffroute.in",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)

app.include_router(tracking_router, prefix="/api")

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.get("/uploads/{file_path:path}")
async def serve_upload(file_path: str):
    full_path = (UPLOADS_DIR / file_path).resolve()
    if not str(full_path).startswith(str(UPLOADS_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)

@app.get("/")
async def root():
    return {
        "message": "Lift Service API is running",
    }
