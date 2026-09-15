"""ArtAdvisor · T3 LLM Prompt 骨架 · Phase 1 MVP 代码层第 8 阶段 (2026-09-16).

承接:
- T1 静态加载模板 → backend/app/services/appraise_service.py (5 维 schema)
- T2 /appraise 接口联通 → backend/app/api/appraise.py (5 维 JSON)
- T4 缓存层 → data/appraise/{id}.json (save_cached + _load_cached)
- T3 prompt 骨架(本文件,2026-09-16 闭环)
    - 不调任何 LLM:仅写 prompt 字符串模板 + 构建器 + 解析器
    - 阻塞链 T3 决策依赖项(模型选型)由张勇显化
    - Phase 2 接入 LLM 时,本文件作为 llm_call() 的"prompt 入参 + response 解析"层

5 维结构复用 (TEMPLATE_SCHEMA from appraise_service):
- context · composition · technique · influence · controversy

行为契约:
- APPRAISE_PROMPT_TEMPLATE:可被 str.format(**ctx) 直接填充的 prompt 模板
- build_appraise_prompt(meta, *, focus_dim=None):基于 artworks.json 单部元数据
  生成完整 prompt,focus_dim 非 None 时聚焦单维(用于补全某维的二次调用)
- parse_llm_output(raw):解析 LLM 文本输出为 5 维 JSON dict
  合法输入 → 直接 json.loads
  含 ```json fence → 提取 fence 内文本后再解析
  非法输入 / 解析失败 → raise ValueError(由调用方决定降级策略)
"""
from __future__ import annotations

import json
import re
from typing import Any

from app.services.appraise_service import TEMPLATE_SCHEMA, TEMPLATE_VERSION

# ----------------------------------------------------------------------------
# Prompt 模板 (Phase 1 MVP 阶段可被任意 LLM 直接调用)
# ----------------------------------------------------------------------------
# 设计原则:
# 1. 把 5 维 schema 显式列出,LLM 不必猜测字段
# 2. 元数据注入(作品/艺术家/年代)以便 LLM 给出有依据的回答
# 3. 输出格式明确要求"严格 JSON",减少解析失败
# 4. 留一处可选 focus_dim 占位符 {focus_dim_hint},默认隐藏,聚焦时显化

APPRAISE_PROMPT_TEMPLATE: str = """你是一位艺术史家 + 策展人。请基于以下作品元数据,按 5 维结构给出结构化鉴赏讲解。

# 作品元数据
- 作品编号:{artwork_id}
- 中文名:{title_cn}
- 英文名:{title_en}
- 艺术家:{artist}
- 年代:{year_range}
- 流派:{style}
- 时期:{period}
- 地域:{region}
- 媒介:{medium}
- 馆藏:{museum}

{focus_dim_hint}
# 5 维输出 schema (严格 JSON,key 顺序固定,缺字段填"无明确记载")
{{
  "artwork_id": "{artwork_id}",
  "template_version": "{template_version}",
  "context": {{
    "artist_bio": "...",
    "commission": "...",
    "historical_event": "...",
    "period_position": "..."
  }},
  "composition": {{
    "format": "...",
    "focal_point": "...",
    "lines_and_shape": "...",
    "color_palette": "...",
    "space_depth": "..."
  }},
  "technique": {{
    "medium": "...",
    "process": "...",
    "innovation": "...",
    "restoration": "..."
  }},
  "influence": {{
    "direct_heirs": "...",
    "paradigm_shift": "...",
    "cultural_footprint": "...",
    "current_location": "..."
  }},
  "controversy": {{
    "attribution": "...",
    "iconography": "...",
    "value_judgment": "...",
    "open_questions": "..."
  }}
}}

# 行为约束
1. 仅输出合法 JSON,不要 ```json fence,不要前后缀文字
2. 不确定字段填"无明确记载",不臆造
3. 每字段 ≤ 200 字,简洁有力
4. 跨语言:中文为主,关键术语附英文(如 sfumato / chiaroscuro)
"""


# 单维聚焦时插入的额外提示(供 LLM 二次调用补全某维)
_FOCUS_DIM_TEMPLATE: str = """
# 本次仅需补全维度
{focus_dim}:
{focus_dim_fields}

其余 4 维请填"无明确记载"。
"""


# ----------------------------------------------------------------------------
# 构建器
# ----------------------------------------------------------------------------

def build_appraise_prompt(
    artwork_meta: dict[str, Any],
    *,
    focus_dim: str | None = None,
) -> str:
    """基于单部作品元数据,生成完整 prompt 字符串.

    Args:
        artwork_meta: 从 data/artworks.json 拉取的单部作品 dict
            (含 id / title_cn / title_en / artist / year_range / style / period /
            region / medium / museum 等 22 字段)
        focus_dim: None → 5 维全生成;否则聚焦单维(用于二次补全)
            取值限定为 TEMPLATE_SCHEMA 的 key(context / composition / technique /
            influence / controversy),非法值 raise ValueError

    Returns:
        可直接传给 LLM 的 prompt 字符串(已填充元数据 + schema 指引)

    Raises:
        ValueError: focus_dim 不在 TEMPLATE_SCHEMA 中
    """
    if focus_dim is not None and focus_dim not in TEMPLATE_SCHEMA:
        raise ValueError(
            f"focus_dim={focus_dim!r} not in TEMPLATE_SCHEMA "
            f"(allowed: {sorted(TEMPLATE_SCHEMA.keys())})"
        )

    # 元数据兜底:缺字段填"(无)"
    def _safe(key: str) -> str:
        v = artwork_meta.get(key)
        return str(v) if v not in (None, "") else "(无)"

    focus_hint = ""
    if focus_dim is not None:
        fields = TEMPLATE_SCHEMA[focus_dim]
        focus_hint = _FOCUS_DIM_TEMPLATE.format(
            focus_dim=focus_dim,
            focus_dim_fields="\n".join(f"  - {f}: ..." for f in fields),
        )

    return APPRAISE_PROMPT_TEMPLATE.format(
        artwork_id=_safe("id"),
        title_cn=_safe("title_cn"),
        title_en=_safe("title_en"),
        artist=_safe("artist"),
        year_range=_safe("year_range"),
        style=_safe("style"),
        period=_safe("period"),
        region=_safe("region"),
        medium=_safe("medium"),
        museum=_safe("museum"),
        template_version=TEMPLATE_VERSION,
        focus_dim_hint=focus_hint,
    )


# ----------------------------------------------------------------------------
# 解析器
# ----------------------------------------------------------------------------

# 兼容 LLM 在 JSON 外层加 ```json ... ``` markdown fence 的情况
_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?```",
    re.DOTALL | re.IGNORECASE,
)


def parse_llm_output(raw: str) -> dict[str, Any]:
    """解析 LLM 文本输出为 5 维 JSON dict.

    Args:
        raw: LLM 返回的原始文本(可能含 ```json fence 或前后缀说明)

    Returns:
        符合 TEMPLATE_SCHEMA 的 5 维 JSON dict(含 3 元字段)

    Raises:
        ValueError: 输入为空 / 非字符串 / 解析后缺核心 5 维
        json.JSONDecodeError: 文本不是合法 JSON

    行为契约:
    1. 空字符串 / 非字符串 → raise ValueError(不静默降级)
    2. 含 ```json fence → 提取 fence 内文本后再解析(LLM 常见输出格式)
    3. 解析后必须包含 context / composition / technique / influence / controversy
       5 维;缺维 → raise ValueError(便于上层降级到 skeleton 路径)
    """
    if not isinstance(raw, str):
        raise ValueError(f"raw must be str, got {type(raw).__name__}")
    if not raw.strip():
        raise ValueError("raw is empty")

    text = raw.strip()
    # 优先尝试 markdown fence 提取
    fence = _FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()

    # 直接 JSON 解析
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 二次尝试:LLM 有时在 JSON 前后加散落说明(如 "以下是结果:" + JSON)
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start >= 0 and brace_end > brace_start:
            text = text[brace_start : brace_end + 1]
            data = json.loads(text)
        else:
            raise

    # 5 维 schema 校验(强制)
    missing = [dim for dim in TEMPLATE_SCHEMA if dim not in data]
    if missing:
        raise ValueError(
            f"LLM output missing 5-dim keys: {missing} "
            f"(required: {sorted(TEMPLATE_SCHEMA.keys())})"
        )
    return data


# ----------------------------------------------------------------------------
# 自检 (python -m app.services.prompts)
# ----------------------------------------------------------------------------

_AW001_META: dict[str, Any] = {
    "id": "aw-001",
    "title_cn": "蒙娜丽莎",
    "title_en": "Mona Lisa",
    "artist": "达·芬奇",
    "year_range": "1503-1519",
    "style": "文艺复兴 · 盛期",
    "period": "High Renaissance",
    "region": "西方",
    "medium": "木板油画",
    "museum": "巴黎卢浮宫",
}


def _self_check() -> None:
    """开发期自检:3 路径验证 prompt 构建 + 解析闭环."""
    # 1. build_appraise_prompt 全量 5 维 prompt 构造
    prompt = build_appraise_prompt(_AW001_META)
    assert "aw-001" in prompt, "artwork_id 未注入 prompt"
    assert "蒙娜丽莎" in prompt, "title_cn 未注入 prompt"
    assert "达·芬奇" in prompt, "artist 未注入 prompt"
    assert TEMPLATE_VERSION in prompt, "template_version 未注入 prompt"
    assert "context" in prompt and "controversy" in prompt, "5 维未在 prompt 列出"
    assert "(无)" not in prompt, "应填字段不应含(无)兜底"
    print(f"[ok] build_appraise_prompt -> {len(prompt)} chars (5 维全量,元数据齐全)")

    # 2. focus_dim 聚焦单维 prompt 构造
    prompt_focus = build_appraise_prompt(_AW001_META, focus_dim="technique")
    assert "technique" in prompt_focus, "focus_dim=technique 未生效"
    assert "medium" in prompt_focus, "focus_dim 字段清单未列出"
    # 非法 focus_dim 应 raise
    try:
        build_appraise_prompt(_AW001_META, focus_dim="bogus")
    except ValueError:
        print("[ok] focus_dim=bogus -> ValueError (校验生效)")
    else:
        raise AssertionError("focus_dim=bogus 应抛 ValueError")

    # 3. parse_llm_output 三路径
    # 3a. 合法 JSON 直接解析
    valid_json = json.dumps({
        "context": {"artist_bio": "x"},
        "composition": {"format": "y"},
        "technique": {"medium": "z"},
        "influence": {"direct_heirs": "a"},
        "controversy": {"attribution": "b"},
    }, ensure_ascii=False)
    parsed = parse_llm_output(valid_json)
    assert parsed["context"]["artist_bio"] == "x"
    print("[ok] parse_llm_output(合法 JSON) -> 5 维 dict")

    # 3b. 含 ```json fence 的 markdown 输出
    fenced = f"以下是结果:\n```json\n{valid_json}\n```\n祝好"
    parsed_fenced = parse_llm_output(fenced)
    assert parsed_fenced["context"]["artist_bio"] == "x"
    print("[ok] parse_llm_output(```json fence) -> 提取后解析")

    # 3c. 缺核心 5 维 → ValueError(便于上层降级)
    try:
        parse_llm_output('{"context": {}}')
    except ValueError:
        print("[ok] parse_llm_output(缺 5 维) -> ValueError (便于降级到 skeleton)")
    else:
        raise AssertionError("缺 5 维应抛 ValueError")


if __name__ == "__main__":
    _self_check()


__all__ = [
    "APPRAISE_PROMPT_TEMPLATE",
    "build_appraise_prompt",
    "parse_llm_output",
]