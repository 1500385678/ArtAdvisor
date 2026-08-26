"""/create 路由 · 创作辅助 (Phase 1 桩接口,实际接入 Phase 3 LLM + 视觉模型)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="创作辅助(桩)")
def create_assist() -> dict:
    return {
        "status": "stub",
        "message": "Phase 1 桩接口:风格/主题/媒介关键词 → 同类作品 + 技法拆解",
        "next": "提交 keywords 列表后返回参考作品清单 + 风格图谱匹配",
    }
