from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .core.config import get_settings
from .db import get_engine, init_db
from .routers import admin, auth, did, external_auth, laws, mail, news, notifications, parliament, ratubles, referenda
from .services.bootstrap import seed_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with Session(get_engine()) as session:
        seed_demo_data(session)
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Государственный портал Ratcraftia.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in settings.cors_origins else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "rgov-backend"}


app.include_router(auth.router)
app.include_router(external_auth.router)
app.include_router(did.router)
app.include_router(mail.router)
app.include_router(news.router)
app.include_router(notifications.router)
app.include_router(laws.router)
app.include_router(ratubles.router)
app.include_router(parliament.router)
app.include_router(referenda.router)
app.include_router(admin.router)
