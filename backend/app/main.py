"""ArtAdvisor FastAPI 入口 · Phase 1 MVP 骨架.

启动:
    cd backend
    uvicorn app.main:app --reload --port 8000

验证:
    curl http://127.0.0.1:8000/health
    curl http://127.0.0.1:8000/gallery | jq
    open http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.gallery import router as gallery_router
from app.api.vision import router as vision_router
from app.api.appraise import router as appraise_router
from app.api.create import router as create_router
from app.api.cure import router as cure_router

app = FastAPI(
    title="ArtAdvisor API",
    version="0.1.0",
    description=(
        "07-艺术-Art 行业 Web 项目 · 让每个人身边都有一位'央美教授 + 策展人 + 艺术评论家'。"
        "Phase 1 MVP:5 大接口 /gallery /vision /appraise /create /cure。"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS · 本地开发开全,生产环境收紧
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    """探活端点 · Phase 1 第一个接口,用于打破 0 代码 + 验证容器/进程。"""
    return {
        "status": "ok",
        "service": "artadvisor-api",
        "version": app.version,
        "phase": "1-MVP-skeleton",
    }


# Phase 1 五大接口路由注册
app.include_router(gallery_router, prefix="/gallery", tags=["gallery"])
app.include_router(vision_router, prefix="/vision", tags=["vision"])
app.include_router(appraise_router, prefix="/appraise", tags=["appraise"])
app.include_router(create_router, prefix="/create", tags=["create"])
app.include_router(cure_router, prefix="/cure", tags=["cure"])
