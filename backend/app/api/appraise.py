"""/appraise 路由 · 鉴赏讲解 (Phase 1 MVP T2 联通,沿用 services/appraise_service.py).

端点:
- GET /appraise?artwork_id=aw-001      → 5 维 JSON(主端点,联通 evaluate())
- GET /appraise/known                  → 当前可产出 5 维的 artwork_id 清单(list_known_ids)
- GET /appraise/cached                 → 仅缓存命中(data/appraise/*.json)的 artwork_id 清单
- GET /appraise/cached/stats           → 缓存覆盖度指标(count / size / generators / mtime)
- GET /appraise/demo                   → 快速预览 aw-001 demo(无 query)

承接:
- T1 静态加载模板(2026-09-08 闭环 commit b0ec730) · 5 维 schema 在 services 层
- T2 接口联通(本文件,2026-09-09 闭环)
- T3 LLM 调用(待 Phase 2)
- T4 缓存到 data/appraise/{id}.json(2026-09-11 闭环 commit bfaaf46,save_cached + _load_cached)
- T4 缓存配套 list_cached_ids + /cached 端点(2026-09-12 闭环 commit 8eb9ece)
- T4 缓存配套 stats 端点(2026-09-14 闭环,本文件 /cached/stats,代码层第 6 阶段,无新决策)
- T5 前端 5 维分 Tab(待 React 工程)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.appraise_service import (
    TEMPLATE_VERSION,
    cache_stats,
    evaluate,
    list_cached_ids,
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


@router.get("/cached", summary="data/appraise/ 已落盘缓存的 artwork_id 清单")
def cached() -> dict:
    """仅列出 data/appraise/*.json 已落盘的 artwork_id(不含内置 demo).

    用途:
    - T5 前端"已鉴赏"Tab 数据来源(与 /known 区分:only LLM/cache 产物)
    - Phase 2 接入 LLM 后,作为覆盖度指标端点
    - 空目录(未启动 LLM)返回空集合而非 404
    """
    ids = list_cached_ids()
    return {
        "template_version": TEMPLATE_VERSION,
        "cached_ids": ids,
        "count": len(ids),
    }


@router.get("/cached/stats", summary="data/appraise/ 缓存覆盖度指标")
def cached_stats() -> dict:
    """data/appraise/ 缓存目录的覆盖度指标(代码层第 6 阶段 · 2026-09-14 闭环).

    返回字段:
    - count:缓存命中数(不含内置 demo)
    - total_size_bytes:全部 .json 文件字节数累计
    - distinct_generators:出现的不同 generator 字符串(去重,最多 10 个)
    - newest_mtime / oldest_mtime:最新 / 最早文件 mtime(ISO 格式,UTC)

    用途:
    - Phase 2 接入 LLM 后,作为 LLM 覆盖度观测端点(进度条 / 仪表盘)
    - T5 前端"已鉴赏"Tab 可选展示 统计 角标
    - 运维自检:确认 LLM 任务跑成功后落盘正常
    - 空目录 / 未启动 LLM → 全 0 / 空集合 / mtime=None,不抛异常
    """
    return cache_stats()


@router.get("/demo", summary="快速预览 aw-001 5 维 demo")
def demo() -> dict:
    """返回内置蒙娜丽莎 demo,用于前端接入前的快速预览."""
    return {
        "template_version": TEMPLATE_VERSION,
        "result": evaluate("aw-001"),
    }
