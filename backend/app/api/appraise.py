"""/appraise 路由 · 鉴赏讲解 (Phase 1 MVP T2 联通,沿用 services/appraise_service.py).

端点:
- GET /appraise?artwork_id=aw-001  → 5 维 JSON(主端点,联通 evaluate())
- GET /appraise/known              → 当前可产出 5 维的 artwork_id 清单(list_known_ids)
- GET /appraise/demo               → 快速预览 aw-001 demo(无 query)

承接:
- T1 静态加载模板(2026-09-08 闭环 commit b0ec730) · 5 维 schema 在 services 层
- T2 接口联通(本文件,2026-09-09 闭环)
- T3 LLM 调用(待 Phase 2)
- T4 缓存到 data/appraise/{id}.json(已在 services 层预留,本端点不直接写)
- T5 前端 5 维分 Tab(待 React 工程)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.appraise_service import (
    TEMPLATE_VERSION,
    evaluate,
    list_known_ids,
)

router = APIRouter()


@router.get("", summary="鉴赏讲解 5 维讲解")
def appraise(
    artwork_id: str = Query(
        ...,
        description="作品编号,形如 aw-001 / aw-070",
        examples=["aw-001"],
    ),
) -> dict:
    """返回 5 维结构化鉴赏 (context / composition / technique / influence / controversy)."""
    try:
        result = evaluate(artwork_id)
    except KeyError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Artwork {artwork_id!r} not found in artworks.json",
        ) from e
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
    return {
        "template_version": TEMPLATE_VERSION,
        "schema": "5dim (context / composition / technique / influence / controversy)",
        "result": result,
    }


@router.get("/known", summary="已具备 5 维内容的 artwork_id 清单")
def known() -> dict:
    """当前可产出 5 维内容的 artwork_id 列表(内置 demo + 缓存命中)."""
    return {
        "template_version": TEMPLATE_VERSION,
        "known_ids": list_known_ids(),
        "count": len(list_known_ids()),
    }


@router.get("/demo", summary="快速预览 aw-001 5 维 demo")
def demo() -> dict:
    """返回内置蒙娜丽莎 demo,用于前端接入前的快速预览."""
    return {
        "template_version": TEMPLATE_VERSION,
        "result": evaluate("aw-001"),
    }
