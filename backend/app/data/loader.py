"""数据加载器 · 从 data/artworks.json 读取作品库.

Phase 0 资产:artworks.json v1.1.0 已落盘 20/500 部经典作品。
Phase 1 起步:先支持内存加载 + 简单查询。
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

# 数据文件位置:backend/app/data/loader.py -> ../../../../data/artworks.json
_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "artworks.json"


@lru_cache(maxsize=1)
def load_artworks() -> List[Dict[str, Any]]:
    """加载作品库 (内存缓存)。"""
    if not _DATA_FILE.exists():
        return []
    with _DATA_FILE.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    # 兼容两种结构:顶层 list,或 {"artworks": [...]}
    if isinstance(payload, list):
        return payload
    return payload.get("artworks", [])


def artwork_count() -> int:
    return len(load_artworks())


def get_by_id(artwork_id: str) -> Optional[Dict[str, Any]]:
    for item in load_artworks():
        if item.get("id") == artwork_id:
            return item
    return None


def filter_by_movement(movement: str) -> List[Dict[str, Any]]:
    """按 period 字段过滤 (artworks.json 实际用 period 表示流派/时期)."""
    return [
        item for item in load_artworks()
        if item.get("period") == movement
    ]
