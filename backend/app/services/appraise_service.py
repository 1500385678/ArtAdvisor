"""ArtAdvisor · 鉴赏讲解服务 · Phase 1 MVP T1+T2 雏形.

关联文档:
- 模板:docs/鉴赏讲解模板.md (v1.0, 2026-09-04)
- 接口:backend/app/api/appraise.py (Phase 1 桩,T2 联通)
- 数据:data/artworks.json + data/artists.json

5 维结构 (5 维 × 平均 4 子字段 = 20 核心字段 + 3 元字段 = 23 字段):
- context    · 背景    · 4 字段 (artist_bio / commission / historical_event / period_position)
- composition· 构图    · 5 字段 (format / focal_point / lines_and_shape / color_palette / space_depth)
- technique  · 技法    · 4 字段 (medium / process / innovation / restoration)
- influence  · 影响    · 4 字段 (direct_heirs / paradigm_shift / cultural_footprint / current_location)
- controversy· 争议    · 4 字段 (attribution / iconography / value_judgment / open_questions)

Phase 1 MVP 集成路径 (docs/鉴赏讲解模板.md 第五节):
- [x] T1 静态加载模板 (本文件) —— 2026-09-08 闭环
- [x] T2 /appraise?artwork_id=aw-001 接口联通(返回 5 维 JSON)—— 2026-09-09 闭环 commit 50e71db
- [ ] T3 LLM 调用 (Claude / GPT-4o) 按 prompt 骨架填充 —— 待张勇决策
- [x] T4 缓存到 data/appraise/{id}.json —— 2026-09-11 闭环 save_cached() + _load_cached() 自检读回通过
- [ ] T5 前端 5 维分 Tab 展示 —— 待 React 工程
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# 模板元数据
# ----------------------------------------------------------------------------

TEMPLATE_VERSION: str = "appraise-5dim-v1.0"

# 5 维字段 schema,顺序固定,用于生成/校验/文档
TEMPLATE_SCHEMA: dict[str, list[str]] = {
    "context": [
        "artist_bio",
        "commission",
        "historical_event",
        "period_position",
    ],
    "composition": [
        "format",
        "focal_point",
        "lines_and_shape",
        "color_palette",
        "space_depth",
    ],
    "technique": [
        "medium",
        "process",
        "innovation",
        "restoration",
    ],
    "influence": [
        "direct_heirs",
        "paradigm_shift",
        "cultural_footprint",
        "current_location",
    ],
    "controversy": [
        "attribution",
        "iconography",
        "value_judgment",
        "open_questions",
    ],
}

# 路径常量 (Phase 1 MVP 部署位置)
# _ArtLib/ArtWeb/backend/app/services/appraise_service.py
#   ^  3       2         1         0     parents() 数 = 3
_PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
_ARTWORKS_PATH: Path = _PROJECT_ROOT / "data" / "artworks.json"
_CACHE_DIR: Path = _PROJECT_ROOT / "data" / "appraise"

# ----------------------------------------------------------------------------
# 内置示例:aw-001《蒙娜丽莎》5 维
# ----------------------------------------------------------------------------
# 来源:docs/鉴赏讲解模板.md §二 各字段"示例"列 + 公开艺术史资料
# 用途:T1 验收 / 单元测试 / 离线 demo(无 LLM / 无网络)
# Phase 2 接入 LLM 后,本示例保留为"人工校对基线",用于回归比对

_AW001_DEMO: dict[str, Any] = {
    "artwork_id": "aw-001",
    "artist_id": "ar-001",
    "title_cn": "蒙娜丽莎",
    "title_en": "Mona Lisa",
    "template_version": TEMPLATE_VERSION,
    "generated_at": "2026-09-08T03:00:00+08:00",
    "generator": "service:appraise + template:5dim (no LLM,manual baseline)",
    "context": {
        "artist_bio": (
            "达·芬奇 1503 年受佛罗伦萨商人 Francesco del Giocondo 委托,"
            "为其妻丽莎·盖拉尔迪尼绘制肖像,达·芬奇 1503-1517 年间多次重绘,终身未交付"
        ),
        "commission": "私人订件 · 佛罗伦萨 · 后转售法国王室",
        "historical_event": "文艺复兴盛期,佛罗伦萨共和国的商业与艺术巅峰",
        "period_position": "High Renaissance (1490s-1527),与米开朗基罗《创世纪》天顶画同期",
    },
    "composition": {
        "format": "77×53 cm 竖幅半身像,金字塔式构图",
        "focal_point": "面部三角区 → 双手 → 远景,视线沿手臂下移",
        "lines_and_shape": "稳定的金字塔轮廓,双手交叠成底部支撑",
        "color_palette": "暖棕调主导,空气透视处理远景,无明显对比色",
        "space_depth": "空气透视(sfumato)模糊远景,人物与背景无明显分界",
    },
    "technique": {
        "medium": "木板油画 (Poplar panel + oil)",
        "process": (
            "底层单色厚涂 (verdaccio) → 多层透明釉染 (glaze),"
            "单色底层决定明暗,釉染决定色彩过渡"
        ),
        "innovation": "首创 sfumato 烟雾法:无明确轮廓线,色层渐变消融边界",
        "restoration": "1956-1962 大规模修复 + 2004 卢浮宫 micro-cracking 3D 扫描",
    },
    "influence": {
        "direct_heirs": [
            "拉斐尔《弗娜芮娜》",
            "安格尔《里维耶夫人》",
            "达利《蒙娜丽莎·达利》",
        ],
        "paradigm_shift": "将肖像画从'符号性'提升到'心理性'层,定下西方肖像画 500 年基调",
        "cultural_footprint": (
            "杜尚《L.H.O.O.Q.》戏仿 / 沃霍尔丝网复刻 / "
            "小说《达·芬奇密码》/ 流行文化高频 icon"
        ),
        "current_location": "巴黎卢浮宫 6 号厅,玻璃柜恒温恒湿展示",
    },
    "controversy": {
        "attribution": (
            "1970s 部分学者认为背景山水非达·芬奇手笔;"
            "2005 卢浮宫红外扫描确认全幅同一人"
        ),
        "iconography": (
            "早期解读为'母性' / 19 世纪浪漫主义解读为'神秘微笑' / "
            "20 世纪女性主义解读为'凝视'权力"
        ),
        "value_judgment": (
            "20 世纪前被视为'达·芬奇次要作品',"
            "1911 卢浮宫失窃事件后全球知名度跃升为'世界第一画'"
        ),
        "open_questions": [
            "为何终身未交付给委托方?",
            "真实模特是谁?",
            "双重性别气质是巧合还是达·芬奇刻意?",
        ],
    },
}

# 内置 demo 索引
_DEMO_INDEX: dict[str, dict[str, Any]] = {
    "aw-001": _AW001_DEMO,
}


# ----------------------------------------------------------------------------
# 数据访问
# ----------------------------------------------------------------------------

def _load_artwork_meta(artwork_id: str) -> dict[str, Any]:
    """从 data/artworks.json 拉取单部作品的最小元数据.

    Phase 1 MVP 暂不常驻全表(70 部可承受,但保留按需读);Phase 2 改 SQLite 索引。
    注:artworks.json 主键字段为 "id" (非 "artwork_id"),取 id 后重命名为 artwork_id
    以便与 5 维模板 JSON schema 对齐。
    """
    if not _ARTWORKS_PATH.exists():
        raise FileNotFoundError(
            f"artworks.json not found at {_ARTWORKS_PATH} (run from project root)"
        )
    with _ARTWORKS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    for art in data.get("artworks", []):
        if art.get("id") == artwork_id:
            return art
    raise KeyError(f"artwork_id={artwork_id!r} not found in artworks.json")


def _load_cached(artwork_id: str) -> dict[str, Any] | None:
    """从 data/appraise/{id}.json 读缓存 (T4 阶段启用)."""
    cache_path = _CACHE_DIR / f"{artwork_id}.json"
    if not cache_path.exists():
        return None
    with cache_path.open(encoding="utf-8") as f:
        return json.load(f)


def save_cached(artwork_id: str, result: dict[str, Any]) -> Path:
    """将 5 维鉴赏结果落盘到 data/appraise/{id}.json (T4 缓存层).

    Args:
        artwork_id: 形如 "aw-001" 的作品编号
        result: 符合 TEMPLATE_SCHEMA 的 5 维 JSON dict (含 3 元字段)

    Returns:
        落盘后的 Path (data/appraise/{artwork_id}.json)

    行为契约:
    - 自动 mkdir -p _CACHE_DIR(空目录自然产生,git 不跟踪)
    - ensure_ascii=False 保留中文字段
    - indent=2 便于人读 + git diff
    - 覆盖写:Phase 2 接入 LLM 后,同一 id 会被新版 generator 覆盖
    - 落盘不入库:`.gitignore` 已设 `data/appraise/*.json`(LLM 产物不污染 repo)

    关联:
    - T3 LLM 调用层生成 result 后,显式调用 save_cached(id, result) 持久化
    - T5 前端分 Tab 触发时,evaluate() 走 _load_cached() 命中,跳过 LLM
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _CACHE_DIR / f"{artwork_id}.json"
    cache_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return cache_path


# ----------------------------------------------------------------------------
# 公开 API
# ----------------------------------------------------------------------------

def list_known_ids() -> list[str]:
    """列出当前已具备 5 维内容的 artwork_id (内置 demo + 缓存命中)."""
    known = set(_DEMO_INDEX.keys())
    if _CACHE_DIR.exists():
        for p in _CACHE_DIR.glob("*.json"):
            known.add(p.stem)
    return sorted(known)


def list_cached_ids() -> list[str]:
    """列出 data/appraise/ 下已落盘的 artwork_id (仅缓存命中,不含内置 demo).

    Phase 1 MVP 用途:
    - /appraise/cached 端点数据源
    - T5 前端"已鉴赏"Tab 数据来源
    - Phase 2 接入 LLM 后,可按此列表估算 LLM 覆盖度
    """
    if not _CACHE_DIR.exists():
        return []
    return sorted(p.stem for p in _CACHE_DIR.glob("*.json"))


def is_known(artwork_id: str) -> bool:
    """快速判断 artwork_id 是否能产出 5 维内容 (demo 或缓存命中)."""
    return artwork_id in _DEMO_INDEX or (_CACHE_DIR / f"{artwork_id}.json").exists()


def evaluate(artwork_id: str, *, use_cache: bool = True) -> dict[str, Any]:
    """生成 / 返回 5 维鉴赏结构.

    优先级:
    1. 内置 demo (人工校对基线,Phase 1 验收用)
    2. data/appraise/{id}.json 缓存 (T4 阶段)
    3. 骨架 + artworks.json 元数据,5 维填 "无明确记载" (Phase 2 接入 LLM 前的 fallback)

    Args:
        artwork_id: 形如 "aw-001" 的作品编号
        use_cache: 是否优先读内置 demo + 缓存 (默认 True)

    Returns:
        符合 TEMPLATE_SCHEMA 的 5 维 JSON dict (含 3 元字段)
    """
    if use_cache and artwork_id in _DEMO_INDEX:
        return _DEMO_INDEX[artwork_id]

    if use_cache:
        cached = _load_cached(artwork_id)
        if cached is not None:
            return cached

    # Fallback: 骨架 + 元数据
    art = _load_artwork_meta(artwork_id)
    return {
        "artwork_id": artwork_id,
        "artist_id": art.get("artist_id"),
        "title_cn": art.get("title_cn"),
        "title_en": art.get("title_en"),
        "year_range": art.get("year_range"),
        "style": art.get("style"),
        "template_version": TEMPLATE_VERSION,
        "generated_at": _dt.datetime.now(_dt.timezone.utc)
        .isoformat(timespec="seconds"),
        "generator": "service:appraise + template:5dim (skeleton,awaiting LLM)",
        **{dim: {k: "无明确记载" for k in fields}
           for dim, fields in TEMPLATE_SCHEMA.items()},
    }


# ----------------------------------------------------------------------------
# 自检 (python -m app.services.appraise_service)
# ----------------------------------------------------------------------------

def _self_check() -> None:
    """开发期自检:验证 evaluate() 产出符合 TEMPLATE_SCHEMA + T4 落盘读回闭环."""
    # 1. aw-001 命中内置 demo,aw-070 走 fallback 骨架路径
    for aw_id in ["aw-001", "aw-070"]:
        result = evaluate(aw_id)
        assert result["template_version"] == TEMPLATE_VERSION
        for dim, fields in TEMPLATE_SCHEMA.items():
            assert dim in result, f"missing dim={dim} in {aw_id}"
            for f in fields:
                assert f in result[dim], f"missing field={dim}.{f} in {aw_id}"
        print(f"[ok] {aw_id} -> {result['generator']}")

    # 2. T4 落盘读回闭环:aw-002 走 skeleton → 显式 save_cached → 重读 cache
    #    验证 save_cached() + _load_cached() 双向打通,无副作用(自检结束 unlink)
    aw_id = "aw-002"
    skeleton = evaluate(aw_id, use_cache=False)
    cache_path = save_cached(aw_id, skeleton)
    reloaded = _load_cached(aw_id)
    assert reloaded is not None, f"{aw_id} cache 落盘后读回为 None"
    assert reloaded["artwork_id"] == aw_id
    assert reloaded["generator"] == skeleton["generator"]
    for dim, fields in TEMPLATE_SCHEMA.items():
        for f in fields:
            assert reloaded[dim][f] == "无明确记载", (
                f"{aw_id} cache 读回 {dim}.{f} != skeleton"
            )
    cache_path.unlink()
    print(f"[ok] {aw_id} -> cache 落盘 → 读回校验通过 (T4 闭环,已清理)")

    # 3. list_cached_ids() 在 cache 存在 / 缺失两态下行为正确
    assert "aw-002" not in list_cached_ids(), "aw-002 unlink 后不应仍在 list_cached_ids"
    print(f"[ok] list_cached_ids() -> {list_cached_ids()} (unlink 后空集合,T4 配套)")


if __name__ == "__main__":
    _self_check()


__all__ = [
    "TEMPLATE_VERSION",
    "TEMPLATE_SCHEMA",
    "evaluate",
    "list_known_ids",
    "list_cached_ids",
    "is_known",
    "save_cached",
]
