"""/gallery 路由 · 作品库 (Phase 1 第一接口,已联通数据层).

端点:
- GET /gallery:列表 (支持 period / artist / region 过滤,limit/offset 分页)
- GET /gallery/{artwork_id}:详情
- GET /gallery/stats:统计 (总数/按 period / artist / region 分布)
"""
from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from app.data.loader import artwork_count, filter_by_movement, get_by_id, load_artworks

router = APIRouter()


@router.get("", summary="列出作品")
def list_artworks(
    movement: Optional[str] = Query(None, description="按 period 过滤,如 印象派 / 文艺复兴 · 盛期"),
    artist: Optional[str] = Query(None, description="按艺术家过滤,如 莫奈"),
    region: Optional[str] = Query(None, description="按地域过滤,如 西方 / 东方"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    items = load_artworks()
    if movement:
        items = filter_by_movement(movement)
    if artist:
        items = [it for it in items if it.get("artist") == artist]
    if region:
        items = [it for it in items if it.get("region") == region]
    total = len(items)
    items = items[offset : offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/stats", summary="作品库统计")
def stats() -> dict:
    items = load_artworks()
    by_period: Dict[str, int] = {}
    by_artist: Dict[str, int] = {}
    by_region: Dict[str, int] = {}
    for it in items:
        p = it.get("period", "Unknown")
        a = it.get("artist", "Unknown")
        r = it.get("region", "Unknown")
        by_period[p] = by_period.get(p, 0) + 1
        by_artist[a] = by_artist.get(a, 0) + 1
        by_region[r] = by_region.get(r, 0) + 1
    return {
        "total": artwork_count(),
        "by_period": by_period,
        "by_artist": by_artist,
        "by_region": by_region,
        "artists_count": len(by_artist),
    }


@router.get("/{artwork_id}", summary="作品详情")
def get_artwork(artwork_id: str) -> dict:
    item = get_by_id(artwork_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Artwork {artwork_id} not found")
    return item
