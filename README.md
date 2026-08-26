# ArtAdvisor

> 07-艺术-Art 行业 Web 项目 · 内部代号 ArtAdvisor · 让每个人身边都有一位"央美教授 + 策展人 + 艺术评论家"

## 项目说明

基于张勇的 36 行业架构,ArtAdvisor 是 **艺术-Art 行业** 的 Web 端顾问产品,把已有的艺术知识体系(西方/中国/理论/构成/创作/鉴赏/市场 7 大图谱)做成一个会看作品、会讲流派、会做策展的艺术顾问。

**项目代号**:ArtAdvisor · v0.1.0 · 2026-08-27

## 同步

- **GitHub**: <https://github.com/1500385678/ArtAdvisor>
- **Gitee**: <https://gitee.com/architectzy/ArtAdvisor>

## 自动化

- **T1** 每日 02:00 — 巡检项目状态
- **T4** 每日 02:00 — 写入次日开发计划到 `.plan/YYYYMMDD.md`
- **T5** 每日 03:00 — 按计划完成小步开发 + commit + push

## 快速开始(后端)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 验证
curl http://127.0.0.1:8000/health
open http://127.0.0.1:8000/docs
```

## 文档导航

- 主计划: [`项目开发计划.md`](项目开发计划.md) — Phase 0/1 任务 checkbox + 变更记录
- 架构总览: [`docs/architecture-overview.md`](docs/architecture-overview.md) — 产品定位/技术架构/数据表/迭代
- 巡检日志: [`.Log/巡检-艺术-YYYYMMDD.md`](.Log/)
- 当日计划: [`.plan/YYYYMMDD.md`](.plan/)
- 候选池: [`data/artworks-source-list.md`](data/artworks-source-list.md) / [`data/themes-index.md`](data/themes-index.md)
- 作品库: [`data/artworks.json`](data/artworks.json) — Phase 0 累计 20/500

## 阶段状态

| 阶段 | 状态 | 进度 |
|------|------|------|
| **Phase 0** 资产盘点 | 🟡 进行中 | 2/6 checkbox · artworks 20/500 (4%) |
| **Phase 1** MVP | 🟡 起步 | 0.x 骨架已落 (FastAPI 5 接口 + /health) |
| **Phase 2-4** | ⚪ 远期 | — |

## 关联文档

- 顶层控制: [`../ArtControl.md`](../ArtControl.md) · [`../ArtLibControl.md`](../ArtLibControl.md)
- 知识图谱: [`../_ArtLib/01-10/`](../_ArtLib/)
- 父项目 README: [`../README.md`](../README.md)
