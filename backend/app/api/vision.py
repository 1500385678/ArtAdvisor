"""/vision 路由 · 作品识别 (Phase 1 桩接口,实际接入 Phase 3 AI)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="作品识别(桩)")
def identify() -> dict:
    return {
        "status": "stub",
        "message": "Phase 1 桩接口:实际接入 CLIP/DINOv2 计划在 Phase 3",
        "next": "提交 image_url 后返回 流派/时期/艺术家 候选 top-3",
    }
