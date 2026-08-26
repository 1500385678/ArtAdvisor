"""/cure 路由 · 虚拟策展 (Phase 1 桩接口,实际接入 Phase 3 LLM 主题生成)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="虚拟策展(桩)")
def cure() -> dict:
    return {
        "status": "stub",
        "message": "Phase 1 桩接口:主题/风格/年代 → 虚拟展览作品组合",
        "next": "提交 theme + period + style 后返回 8-12 件作品推荐 + 展览叙事大纲",
    }
