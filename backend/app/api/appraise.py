"""/appraise 路由 · 鉴赏讲解 (Phase 1 桩接口,实际接入 Phase 2 LLM 模板)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="鉴赏讲解(桩)")
def appraise() -> dict:
    return {
        "status": "stub",
        "message": "Phase 1 桩接口:5 维模板(背景/构图/技法/影响/争议)计划在 Phase 2",
        "next": "提交 artwork_id 后返回 5 维度结构化讲解 + LLM 润色",
    }
