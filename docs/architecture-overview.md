# 艺术顾问 · 产品立项与技术方案

> 项目代号：ArtAdvisor（内部代号 07-艺术-Art）
> 版本：v1.0 · 2026-08-24
> 维护：张勇

---

## 一、项目概述

### 1.1 愿景

> **让每个人身边都有一位"央美教授 + 一位策展人 + 一位艺术评论家"。**

把张勇已经整理的"艺术史 → 艺术理论 → 视觉构成 → 创作方法 → 艺术鉴赏 → 艺术市场"完整知识图谱，做成一个**会思考的艺术顾问**——能讲作品、能评创作、能解流派、能给审美训练，也能针对一件作品给出"背景 + 形式 + 意义"三件套。

### 1.2 形态

| 形态 | 场景 | 状态 |
|------|------|------|
| **飞书 Agent（当前）** | 工作中随问随答 | ✅ 已上线 |
| **Web App（核心）** | 自学/爱好者/创作者 | ⏳ 规划中 |
| **桌面端（Electron/Tauri）** | 创作场景 | 📋 远期 |
| **微信小程序** | 每日一画 | 📋 远期 |
| **REST API** | 嵌入创作工具 | 📋 远期 |
| **AR 美术馆** | 摄像头识别画作 | 📋 远期 |

### 1.3 已有资产盘点

| 资产 | 位置 | 价值 |
|------|------|------|
| 西方艺术史图谱 | `western_art_knowledge.md` | 古典 → 现代 → 当代 |
| 中国艺术史图谱 | `chinese_art_knowledge.md` | 古代 → 近代 → 当代 |
| 艺术理论图谱 | `art_theory_knowledge.md` | 形式主义/图像学/符号学 |
| 视觉构成图谱 | `visual_composition_knowledge.md` | 色彩/构图/光影/质感 |
| 创作方法图谱 | `creation_knowledge.md` | 油画/国画/雕塑/摄影/数字 |
| 艺术鉴赏图谱 | `appreciation_knowledge.md` | 流派/风格/赏析方法 |
| 艺术市场图谱 | `art_market_knowledge.md` | 拍卖/画廊/收藏/版权 |
| 经典作品库 | `masterpieces.json` | 1000+ 名作 |
| 艺术家档案 | `artists.json` | 500+ 艺术家 |
| 流派标签库 | `movements.json` | 100+ 流派 |
| SQLite DB | `data.db` | 已有表结构 |
| Persona / Skill | `persona.md` / `SKILL.md` | 触发配置 |

---

## 二、产品定位

### 2.1 目标用户

| 用户群 | 痛点 | 价值 |
|--------|------|------|
| **艺术爱好者** | 看不懂、缺背景 | 作品讲解 + 背景故事 |
| **艺术专业学生** | 抽象、缺案例 | 经典库 + 流派网络 |
| **创作者（绘画/设计/摄影）** | 缺理论、缺反馈 | 视觉构成 + AI 评图 |
| **艺术教师** | 备课难、案例散 | 经典库 + 课件生成 |
| **收藏者 / 投资人** | 缺知识、缺市场 | 艺术家 + 市场 + 拍卖数据 |
| **策展人** | 缺主题、缺叙事 | 主题推荐 + 叙事设计 |

### 2.2 核心价值主张

1. **艺术三件套讲解**：选作品 → 同时输出"背景 + 形式 + 意义"
2. **AI 评图**：上传作品 → 视觉构成诊断 + 改进建议
3. **经典作品库**：1000+ 名作高清图 + 深度讲解
4. **艺术家档案**：500+ 艺术家生平 / 风格 / 作品 / 影响
5. **流派网络**：100+ 流派 + 时间线 + 关系图
6. **跨文化桥接**：中西艺术对比 + 互鉴

### 2.3 差异化（vs 现有产品）

- **Google Arts & Culture**：作品库强，缺理论、缺中文课纲
- **WikiArt**：艺术家档案好，缺理论深度
- **Coursera 艺术课**：英文为主，互动弱
- **小红书 / 抖音**：碎片化，缺系统
- **各家美术馆 APP**：分散，缺统一入口

**我们的差异**：以张勇的**结构化知识图谱 + 经典库 + 艺术家档案**为骨架，AI 提供"背景 + 形式 + 意义"三件套，覆盖中西艺术 + 创作 + 市场。

---

## 三、功能架构

### 3.1 五大核心模块

```
┌─────────────────────────────────────────────────┐
│             艺术顾问 ArtAdvisor                  │
├──────────┬──────────┬──────────┬────────┬───────┤
│ 知识图谱 │ 作品库   │ 艺术家   │ 智能讲解│ 多端  │
│ (Graph)  │ (Work)   │ (Artist) │ (AI)   │ (UI)  │
├──────────┴──────────┴──────────┴────────┴───────┤
│              数据层 (SQLite / PG)               │
├─────────────────────────────────────────────────┤
│              内容层 (Markdown + JSON + 图像)     │
└─────────────────────────────────────────────────┘
```

### 3.2 模块拆分

#### 模块 1：知识图谱（Knowledge Graph）
- **数据结构**：节点（知识点）+ 边（前置 / 衍生 / 作品关联）
- **覆盖**：西方艺术 → 中国艺术 → 艺术理论 → 视觉构成 → 创作 → 鉴赏 → 市场
- **节点属性**：
  - name, period, level, difficulty, tags, prerequisites
  - works[]（关联作品）
  - artists[]（关联艺术家）
  - movements[]（关联流派）
  - cross_refs[]（跨文化桥接）
  - applications[]（应用场景：创作/鉴赏/收藏/教学）
  - explanation[]（三件套讲解：背景/形式/意义）

#### 模块 2：经典作品库（Masterpieces Library）
- **1000+ 名作**：
  - 西方：达芬奇/米开朗基罗/伦勃朗/莫奈/梵高/毕加索/康定斯基
  - 中国：顾恺之/吴道子/王希孟/黄公望/八大山人/齐白石/徐悲鸿
  - 摄影：布列松/亚当斯/森山大道
  - 当代：草间弥生/班克斯/蔡国强
- **每条作品**：高清图 / 作者 / 创作背景 / 形式分析 / 主题意义 / 影响
- **多维检索**：按流派/时期/地域/媒介/主题
- **对比模式**：并排对比多幅作品

#### 模块 3：艺术家档案（Artist Profiles）
- **500+ 艺术家**：
  - 西方古典 → 现代 → 当代
  - 中国古代 → 近代 → 当代
  - 摄影 / 雕塑 / 装置 / 数字艺术
- **每条档案**：生平 / 师承 / 风格演变 / 代表作 / 影响 / 拍卖纪录

#### 模块 4：智能讲解（AI Tutor）
- **三件套讲解**：选作品 → 同时输出"背景 + 形式 + 意义"
- **AI 评图**：上传作品 → 视觉构成诊断 + 改进建议（构图/色彩/光影/质感）
- **流派问答**："印象派和后印象派的区别？" → 风格演变 + 代表作
- **创作建议**："我想画夜景，怎么构图？" → 构图方法 + 参考
- **跨文化对比**："中国山水画和西方风景画有什么不同？"

#### 模块 5：多端 UI
- Web App（核心）：响应式设计，PC / 平板 / 手机
- 飞书机器人：消息形态（当前）
- 小程序：每日一画 + 简评
- 桌面端：创作场景 + AI 评图
- AR 美术馆（远期）：摄像头识别画作

---

## 四、技术架构

### 4.1 整体架构

```
┌─────────────────────────────────────────────┐
│  表现层 (Presentation)                       │
│  Web (React/Vue) · 小程序 · 飞书 Bot · CLI  │
└──────────────────┬──────────────────────────┘
                   │ HTTPS / WebSocket
┌──────────────────┴──────────────────────────┐
│  API 层 (FastAPI · Python)                  │
│  /graph /work /artist /ai /user            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│  服务层 (Services)                          │
│  图谱引擎 · 作品库 · 艺术家库 · AI 引擎     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│  数据层 (Data)                              │
│  PostgreSQL · Redis · 向量库 · 文件存储     │
└─────────────────────────────────────────────┘
```

### 4.2 技术栈选型

| 层 | 选型 | 理由 |
|----|------|------|
| **后端框架** | FastAPI（Python） | 异步、自动文档 |
| **前端** | React + TypeScript | 组件丰富 |
| **UI 库** | Ant Design / shadcn/ui | 中文友好 / 现代 |
| **图像识别** | CLIP / ResNet | 作品分类、风格识别 |
| **图像生成** | ComfyUI（已装） / SD | 创作辅助 |
| **CDN** | 对象存储 + CDN | 高清作品分发 |
| **数据库** | PostgreSQL（主） + SQLite（离线） | 张勇已有 SQLite 经验 |
| **缓存** | Redis | 作品缓存、AI 响应缓存 |
| **向量库** | pgvector / Chroma | 作品检索、相似风格 |
| **LLM** | Claude / GPT / 本地 Ollama | 讲解 / 评图 / 跨文化 |
| **部署** | Docker Compose → K8s | 单机起步，平滑扩容 |
| **CI/CD** | GitHub Actions | 自动化 |
| **监控** | Sentry + Prometheus | 错误 + 性能 |
| **认证** | JWT + 飞书 OAuth | 飞书用户无缝 |

### 4.3 数据架构

#### 核心表

```sql
-- 知识点表
CREATE TABLE knowledge_points (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  period TEXT,                   -- 时期
  level TEXT,                   -- 入门/进阶/专业
  difficulty INT,               -- 1-5
  description TEXT,
  works JSONB,
  artists JSONB,
  movements JSONB,
  cross_refs JSONB,             -- 跨文化桥接
  applications JSONB,
  explanation JSONB,            -- 三件套讲解
  prerequisites INT[],
  tags TEXT[]
);

-- 作品
CREATE TABLE artworks (
  id SERIAL PRIMARY KEY,
  title TEXT,
  artist_id INT,
  year INT,
  medium TEXT,                  -- 油画/水墨/摄影/雕塑/装置
  style TEXT,                   -- 流派
  size TEXT,
  location TEXT,                -- 收藏地
  image_url TEXT,
  image_high_res_url TEXT,
  background TEXT,
  formal_analysis JSONB,        -- 构图/色彩/光影/质感
  meaning TEXT,
  influence TEXT,
  knowledge_ids INT[],
  movement_ids JSONB,
  tags TEXT[]
);

-- 艺术家
CREATE TABLE artists (
  id SERIAL PRIMARY KEY,
  name TEXT,
  name_en TEXT,
  born INT,
  died INT,
  nationality TEXT,
  school TEXT,
  bio TEXT,
  teachers JSONB,
  students JSONB,
  style_evolution JSONB,
  representative_works JSONB,
  influence TEXT,
  auction_records JSONB,
  knowledge_ids INT[]
);

-- 流派
CREATE TABLE movements (
  id SERIAL PRIMARY KEY,
  name TEXT,
  name_en TEXT,
  period TEXT,                  -- 起止年
  region TEXT,
  core_ideas JSONB,
  characteristics JSONB,
  representative_works JSONB,
  representative_artists JSONB,
  predecessor_id INT,           -- 前驱流派
  successor_ids JSONB,          -- 后继流派
  knowledge_ids INT[]
);

-- AI 评图
CREATE TABLE art_reviews (
  id SERIAL PRIMARY KEY,
  user_id INT,
  image_url TEXT,
  composition_score REAL,
  color_score REAL,
  light_score REAL,
  texture_score REAL,
  issues JSONB,
  suggestions JSONB,
  created_at TIMESTAMP
);

-- 用户档案
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  open_id TEXT UNIQUE,
  name TEXT,
  role TEXT,                    -- 爱好者/创作者/教师/收藏者
  favorite_movements JSONB,
  favorite_artists JSONB,
  level TEXT,
  created_at TIMESTAMP
);

-- 收藏
CREATE TABLE user_collections (
  id SERIAL PRIMARY KEY,
  user_id INT,
  artwork_id INT,
  notes TEXT,
  created_at TIMESTAMP
);
```

#### 已有 SQLite 表（迁移）

- 保留 `data.db` 已有数据
- 写迁移脚本 → PostgreSQL
- 作品高清图上传对象存储 + CDN
- 艺术家档案从公开数据灌入

### 4.4 模块拆分（代码组织）

```
art-advisor/
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── api/                # 路由层
│   │   │   ├── graph.py        # /graph
│   │   │   ├── work.py         # /work
│   │   │   ├── artist.py       # /artist
│   │   │   ├── ai.py           # /ai
│   │   │   └── user.py
│   │   ├── services/           # 业务层
│   │   │   ├── graph_engine.py
│   │   │   ├── work_search.py
│   │   │   ├── artist_search.py
│   │   │   ├── art_reviewer.py
│   │   │   └── ai_tutor.py
│   │   ├── models/             # ORM
│   │   ├── db/                 # 数据库
│   │   ├── vision/             # 视觉模型
│   │   ├── llm/                # LLM 抽象
│   │   └── utils/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/                   # React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Graph.tsx
│   │   │   ├── Work.tsx
│   │   │   ├── Artist.tsx
│   │   │   ├── Movement.tsx
│   │   │   ├── Review.tsx
│   │   │   ├── Tutor.tsx
│   │   │   └── Profile.tsx
│   │   ├── components/
│   │   ├── api/
│   │   ├── store/              # Zustand
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
│
├── content/                    # 内容数据
│   ├── knowledge/              # 知识点 JSON
│   ├── works/                  # 作品库
│   ├── artists/                # 艺术家
│   ├── movements/              # 流派
│   └── md/                     # Markdown 原文
│
├── deploy/
│   ├── docker-compose.yml
│   └── k8s/
│
├── scripts/                    # 工具脚本
│   ├── md_to_json.py
│   ├── works_seed.py
│   ├── artists_seed.py
│   └── migrate_sqlite.py
│
└── README.md
```

---

## 五、迭代计划

### Phase 0 - 资产盘点（1-2 周）

> 把已有的 md 文件转成结构化数据

- [ ] 写 `md_to_json.py`：解析 7 份知识点 md → JSON
- [ ] 建立知识图谱初始数据（西方艺术/中国艺术/理论/构成/创作/鉴赏/市场）
- [ ] 作品库整理（1000+，含高清图）
- [ ] 艺术家档案入库（500+）
- [ ] 流派库入库（100+）
- [ ] SQLite → PostgreSQL 迁移脚本
- [ ] 建表 + 灌库

**交付**：可查询的知识图谱 + 作品库 + 艺术家档案（CLI/JSON）

### Phase 1 - MVP（4-6 周）

> 让用户能"看 + 学 + 评"

- [ ] FastAPI 骨架 + `/graph` `/work` `/artist` 接口
- [ ] React 前端：知识图谱浏览 + 作品浏览 + 艺术家档案 + 简单 AI 评图
- [ ] 200 个核心作品
- [ ] 100 个核心艺术家
- [ ] 飞书 OAuth 登录
- [ ] Docker Compose 一键启动

**交付**：Web App 可用，PC 端能查图谱、看作品、查艺术家

### Phase 2 - 完整功能（8-12 周）

> 学习闭环：进度 / 推荐 / 创作

- [ ] 学习进度追踪（流派 / 艺术家掌握）
- [ ] 智能推荐（基于兴趣）
- [ ] AI 深度评图（构图/色彩/光影/质感）
- [ ] 创作辅助（草图 → 建议）
- [ ] 个人美术馆
- [ ] 作品库扩展到 5000+
- [ ] 移动端适配

**交付**：完整艺术学习闭环

### Phase 3 - AI 智能化（4-8 周）

> 让 AI 真正"懂艺术"

- [ ] AI 三件套讲解（背景/形式/意义）
- [ ] AI 深度评图（多维度）
- [ ] AI 创作辅助
- [ ] AI 流派演变讲解
- [ ] AI 跨文化对比
- [ ] 学习数据分析（审美能力报告）

**交付**：AI 艺术助手可用

### Phase 4 - 多端 + 商业化（远期）

- [ ] 微信小程序（每日一画）
- [ ] 桌面端（创作场景）
- [ ] AR 美术馆（摄像头识别）
- [ ] 艺术市场数据接入
- [ ] 付费内容 / 会员体系
- [ ] 画廊 / 拍卖行合作（B2B）

---

## 六、里程碑

| 阶段 | 时间 | 关键产物 | 验证标准 |
|------|------|---------|---------|
| Phase 0 | W02 | 知识图谱 + 作品库 + 艺术家档案 JSON | 7 份 md 全部入库，1000+ 作品可查 |
| Phase 1 | W06 | Web MVP | 100 用户内测，反馈 ≥ 4.0/5.0 |
| Phase 2 | W14 | 完整学习闭环 | 日活 1000+ · 留存 ≥ 30% |
| Phase 3 | W20 | AI 艺术助手 | 评图准确率 ≥ 85% |
| Phase 4 | W32+ | 商业化版本 | DAU 1万+ / 付费转化 ≥ 5% |

---

## 七、风险与挑战

| 风险 | 影响 | 应对 |
|------|------|------|
| 作品高清图版权 | 法律风险 | 公共领域 + 已授权 + 用户贡献 |
| 艺术家数据准确性 | 教学 | 维基 + 美术馆数据交叉验证 |
| 流派分类争议 | 用户接受度 | 主流分类 + 多视角 |
| AI 评图主观性 | 创作者接受度 | 多维度评分 + 建议非定论 |
| 艺术市场数据敏感 | 合规 | 公开数据 + 免责声明 |
| 风格识别准确率 | 用户体验 | 多模型融合 + 人工审核 |
| 中西艺术对比简化 | 误导 | 专家审核 + 谨慎类比 |
| LLM 艺术知识 | 错误风险 | 知识图谱约束 + 答案回查 |
| 飞书生态依赖 | 渠道单一 | Web / 小程序多端铺开 |
| 艺术爱好者付费意愿 | 商业化 | 先免费验证 → 增值服务 |

---

## 八、成本估算（参考）

| 项 | 阶段 | 估算（月） |
|----|------|----------|
| 云服务器 | 起步 | ¥500 / 月（4C8G，图像处理） |
| 对象存储 | 作品高清图 | ¥500 / 月（图像大） |
| CDN | 图像分发 | ¥500 / 月 |
| LLM API（Claude/GPT） | 1000 用户 | ¥2500-6000 / 月 |
| 视觉模型 API | 评图 | ¥500-1500 / 月 |
| 域名 + SSL | - | ¥200 / 年 |
| 监控 / 日志 | - | ¥0（免费额度） |

**总成本**：MVP 阶段 ¥1500-3000 / 月，规模化后 ¥2万-5万 / 月（图像成本是大头）。

---

## 九、团队建议

- **MVP 阶段（1-2 人）**：张勇 + 1 全栈（要熟悉图像处理 + CDN）
- **完整阶段（3-5 人）**：+ 1 前端 + 1 艺术编辑（艺术史背景）
- **AI 阶段（5-8 人）**：+ 1 AI 工程师 + 1 视觉模型工程师
- **机构服务阶段（8-12 人）**：+ 1 策展人 + 1 拍卖行数据专家

---

## 十、版本说明

- **覆盖范围**：产品定位 + 功能 + 技术 + 迭代 + 风险
- **配套文档**：
  - 知识图谱：7 份 `*_knowledge.md`
  - 作品：`masterpieces.json`
  - 艺术家：`artists.json`
  - 流派：`movements.json`
- **下一步**：Phase 0 启动——把 md 转 JSON，建库 + 灌作品/艺术家/流派
- **维护**：张勇

---

> 哲学：**艺术不是装饰，是看世界的方式。** Phase 0-1 把"图谱 + 作品 + 艺术家"打通，AI 和商业化都是后面的事。地基是让爱好者看见作品、感受形式、形成自己的审美，让创作者看见自己、找到语言。
