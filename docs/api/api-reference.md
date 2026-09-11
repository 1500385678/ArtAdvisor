# ArtAdvisor API 参考 · Phase 1 MVP 现状

> ArtAdvisor REST API 接口文档 · v1.0.1 · 2026-09-12
> 适用阶段:**Phase 1 MVP 骨架**(`/gallery` 联通数据层 + `/appraise` 联通 services + T4 缓存配套 `/cached`,其余 3 桩)
> 维护:07-艺术-Art 行业顾问

---

## 一、概述

### 1.1 服务入口

| 维度 | 值 |
|------|-----|
| Base URL(本地开发) | `http://127.0.0.1:8000` |
| Base URL(生产) | 规划中 |
| OpenAPI / Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| 启动命令 | `cd backend && uvicorn app.main:app --reload --port 8000` |
| 当前版本 | `0.1.0` (Phase 1 MVP 骨架) |

### 1.2 接口总览

| 模块 | 路由 | 状态 | 数据层 | 阻塞链阶段 |
|------|------|------|--------|----------|
| Meta | `GET /health` | ✅ 已闭环 | 静态 | T1 |
| Gallery · 作品库 | `GET /gallery` | ✅ 已联通 | `data/artworks.json` | T2 |
| Gallery · 统计 | `GET /gallery/stats` | ✅ 已联通 | `data/artworks.json` | T2 |
| Gallery · 详情 | `GET /gallery/{artwork_id}` | ✅ 已联通 | `data/artworks.json` | T2 |
| Vision · 作品识别 | `GET /vision` | 🟡 桩 | — | Phase 3 |
| Appraise · 5 维讲解 | `GET /appraise?artwork_id=...` | ✅ 已联通 | `services/appraise_service.py` | T2 (T3-T5 待 Phase 2) |
| Appraise · 清单 | `GET /appraise/known` | ✅ 已联通 | 同上 | T2 |
| Appraise · 缓存清单 | `GET /appraise/cached` | ✅ 已联通 (2026-09-12) | `data/appraise/*.json` | T4 配套 |
| Appraise · Demo | `GET /appraise/demo` | ✅ 已联通 | 同上 | T2 |
| Create · 创作辅助 | `GET /create` | 🟡 桩 | — | Phase 3 |
| Cure · 虚拟策展 | `GET /cure` | 🟡 桩 | — | Phase 3 |

**图例**:✅ 已联通 · 🟡 桩接口(返回状态标记) · ❌ 缺失

### 1.3 通用约定

- **协议**:HTTP/1.1,JSON 入参 + JSON 出参
- **字符集**:UTF-8
- **CORS**:开发环境全开(`*`);生产环境按域名收紧
- **错误格式**:`{"detail": "<message>"}` (FastAPI 标准)
- **分页**:`limit` (1-100,默认 20) + `offset` (≥0,默认 0)
- **ID 格式**:artwork_id 形如 `aw-001` ~ `aw-070`(当前 70 部)

---

## 二、Meta · `/health`

### `GET /health`

探活端点 · 用于打破 0 代码 + 验证容器/进程。

**响应** · `200 OK`

```json
{
  "status": "ok",
  "service": "artadvisor-api",
  "version": "0.1.0",
  "phase": "1-MVP-skeleton"
}
```

**示例**

```bash
curl http://127.0.0.1:8000/health
```

---

## 三、Gallery · `/gallery/*`

> 数据层:`data/artworks.json` v1.6.0 / 70 部 / 14%(2026-09-02 触底)
> 加载器:`backend/app/data/loader.py`

### `GET /gallery`

列出作品(支持 period / artist / region 过滤,limit/offset 分页)。

**Query 参数**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `movement` | str | 否 | — | 按 period 过滤,如 `印象派` / `文艺复兴 · 盛期` |
| `artist` | str | 否 | — | 按艺术家过滤,如 `莫奈` |
| `region` | str | 否 | — | 按地域过滤,如 `西方` / `东方` |
| `limit` | int | 否 | 20 | 1-100 |
| `offset` | int | 否 | 0 | ≥0 |

**响应** · `200 OK`

```json
{
  "total": 70,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "aw-001",
      "title_zh": "蒙娜丽莎",
      "artist": "达·芬奇",
      "year": "1503-1519",
      "period": "文艺复兴 · 盛期",
      "region": "西方",
      "...": "...(共 22 字段,见 artworks.json schema)"
    }
  ]
}
```

### `GET /gallery/stats`

作品库统计(总数 + 按 period / artist / region 分布)。

**响应** · `200 OK`

```json
{
  "total": 70,
  "by_period": {"印象派": 8, "...": "..."},
  "by_artist": {"莫奈": 3, "...": "..."},
  "by_region": {"西方": 42, "东方": 14, "...": "..."},
  "artists_count": 30
}
```

### `GET /gallery/{artwork_id}`

作品详情(单条 22 字段全量)。

**Path 参数** · `artwork_id` 必填,形如 `aw-001`

**响应** · `200 OK`(找到)· `404 Not Found`(未找到)

```json
{
  "id": "aw-001",
  "title_zh": "蒙娜丽莎",
  "...": "..."
}
```

---

## 四、Appraise · `/appraise/*`

> 服务层:`backend/app/services/appraise_service.py` 275 行
> 模板版本:`appraise-5dim-v1.0`(5 维 × 4 子字段 = 20 核心字段)
> 模板文档:[../鉴赏讲解模板.md](../鉴赏讲解模板.md)

### 4.1 五维 schema 速览

| 维度 | 子字段数 | 字段清单 |
|------|---------|---------|
| `context`(背景) | 4 | artist_bio / commission / historical_event / period_position |
| `composition`(构图) | 5 | format / focal_point / lines_and_shape / color_palette / space_depth |
| `technique`(技法) | 4 | medium / process / innovation / restoration |
| `influence`(影响) | 4 | direct_heirs / paradigm_shift / cultural_footprint / current_location |
| `controversy`(争议) | 4 | attribution / iconography / value_judgment / open_questions |

### `GET /appraise?artwork_id=aw-001`

主端点:返回 5 维结构化鉴赏(JSON)。

**Query 参数** · `artwork_id` 必填,形如 `aw-001` / `aw-070`

**响应** · `200 OK`

```json
{
  "template_version": "appraise-5dim-v1.0",
  "schema": "5dim (context / composition / technique / influence / controversy)",
  "result": {
    "context": {"artist_bio": "...", "...": "..."},
    "composition": {"format": "...", "...": "..."},
    "technique": {"medium": "...", "...": "..."},
    "influence": {"direct_heirs": "...", "...": "..."},
    "controversy": {"attribution": "...", "...": "..."}
  }
}
```

**错误码**

| 状态码 | 含义 | 触发条件 |
|--------|------|----------|
| `404 Not Found` | 作品不在 `artworks.json` | `artwork_id` 拼写错误 / 超出 aw-001~aw-070 范围 |
| `503 Service Unavailable` | 数据层缺失 | `data/artworks.json` 不存在 |

### `GET /appraise/known`

当前可产出 5 维内容的 `artwork_id` 清单(内置 demo + 缓存命中)。

**响应** · `200 OK`

```json
{
  "template_version": "appraise-5dim-v1.0",
  "known_ids": ["aw-001"],
  "count": 1
}
```

> 当前 count=1(仅 aw-001 内置蒙娜丽莎 demo);其余 69 部走 skeleton 路径(T3 LLM 调用后扩展)

### `GET /appraise/cached`

仅 `data/appraise/*.json` 已落盘缓存的 `artwork_id` 清单(**不含**内置 demo)。

**响应** · `200 OK`

```json
{
  "template_version": "appraise-5dim-v1.0",
  "cached_ids": [],
  "count": 0
}
```

> Phase 1 MVP 阶段空目录(T3 LLM 未启动)→ `cached_ids: []`,`count: 0`;空集合返回 `200` 而非 `404`,便于前端"已鉴赏"Tab 渲染。
> T3 接入 LLM 后,本端点返回 LLM 已落盘的 artwork_id 集合,可用于覆盖度指标。

### `GET /appraise/demo`

快速预览 aw-001 demo(无 query)。

**响应** · `200 OK`(同 `/appraise?artwork_id=aw-001`,但去掉 wrapper)

```json
{
  "template_version": "appraise-5dim-v1.0",
  "result": {"context": {"...": "..."}, "...": "..."}
}
```

---

## 五、Vision · `/vision`

### `GET /vision`

作品识别(Phase 1 桩接口,实际接入 Phase 3 CLIP/DINOv2)。

**响应** · `200 OK`

```json
{
  "status": "stub",
  "message": "Phase 1 桩接口:实际接入 CLIP/DINOv2 计划在 Phase 3",
  "next": "提交 image_url 后返回 流派/时期/艺术家 候选 top-3"
}
```

---

## 六、Create · `/create`

### `GET /create`

创作辅助(Phase 1 桩接口,实际接入 Phase 3 LLM + 视觉模型)。

**响应** · `200 OK`

```json
{
  "status": "stub",
  "message": "Phase 1 桩接口:风格/主题/媒介关键词 → 同类作品 + 技法拆解",
  "next": "提交 keywords 列表后返回参考作品清单 + 风格图谱匹配"
}
```

---

## 七、Cure · `/cure`

### `GET /cure`

虚拟策展(Phase 1 桩接口,实际接入 Phase 3 LLM 主题生成)。

**响应** · `200 OK`

```json
{
  "status": "stub",
  "message": "Phase 1 桩接口:主题/风格/年代 → 虚拟展览作品组合",
  "next": "提交 theme + period + style 后返回 8-12 件作品推荐 + 展览叙事大纲"
}
```

---

## 八、Phase 1 MVP 阻塞链

按 [../鉴赏讲解模板.md §五 Phase 1 MVP 集成路径](../鉴赏讲解模板.md) 5 步框架:

| 阶段 | 任务 | 状态 | 闭环 commit |
|------|------|------|----------|
| T1 | services 静态加载模板 | ✅ 已闭环 | `b0ec730` (2026-09-08) |
| T2 | `/appraise` 接口联通(返回 5 维 JSON) | ✅ 已闭环 | `50e71db` (2026-09-09) |
| T3 | LLM 调用(Claude / GPT-4o)按 prompt 骨架填充 | ⏳ 待启动 | — |
| T4 | 缓存到 `data/appraise/{id}.json` | ⏳ 待启动 | services 层已预留 `_load_cached()` |
| T5 | 前端 5 维分 Tab 展示 | ⏳ 待启动 | — |

**当前阻塞链**:T1+T2 已闭环 → T3 LLM 调用是下一可独立启动子任务(不涉及新决策)。

---

## 九、不做什么

- **不**实现 CLIP/DINOv2 接入(`/vision` 留 Phase 3)
- **不**实现 LLM 真实调用(`/appraise` 当前走内置 demo + skeleton 路径,真实 LLM 留 T3)
- **不**实现鉴权 + 限流(Phase 1 MVP 假设本地可信环境)
- **不**实现 WebSocket / SSE(本阶段全 REST,后续 `/vision` 流式识别再考虑)
- **不**实现 OpenAPI 自动生成(本文件手动维护,代码注释里有 docstring 可对照)
- **不**写 SDK / Client(等前端 React 工程启动时再考虑类型定义生成)

---

## 十、变更记录

- **2026-09-10 v1.0**:首版落盘,梳理 5 大接口(11 端点) + Phase 1 MVP 阻塞链;`docs/api/` 首份文档
- 后续随 `/appraise` T3 LLM 接入 + `/gallery` 续推到 500 部 + `/vision` 桩变实,逐项更新

---

## 关联文档

- [../architecture-overview.md](../architecture-overview.md) — 整体架构 + 产品立项
- [../鉴赏讲解模板.md](../鉴赏讲解模板.md) — 5 维 schema 字段定义 + LLM prompt 骨架
- [../../backend/app/main.py](../../backend/app/main.py) — FastAPI 入口
- [../../backend/app/api/appraise.py](../../backend/app/api/appraise.py) — T2 联通参考实现
- [../../backend/app/api/gallery.py](../../backend/app/api/gallery.py) — T2 联通参考实现
- [../../backend/app/services/appraise_service.py](../../backend/app/services/appraise_service.py) — 5 维模板加载 + evaluate() API
- [../../data/artworks.json](../../data/artworks.json) — 70 部作品主表
- [../../data/artists.json](../../data/artists.json) — 73 位艺术家档案
- [../项目开发计划.md §五 Phase 0](../项目开发计划.md) — 任务闭环追踪
