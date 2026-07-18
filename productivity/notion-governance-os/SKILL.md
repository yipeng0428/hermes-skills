---
name: notion-governance-os
description: "Notion 持续治理系统：自动巡检、分类、纠错、去重、建立关联并提醒异常的 Notion 知识库运维系统"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_API_KEY]
  commands: [python3, pip]
  files: [notion_gov_config.json, notion_scan_cache.json]
metadata:
  hermes:
    tags: [Notion, Governance, Productivity, Automation, CI/CD, Knowledge-Management]
    homepage: https://developers.notion.com
---

# 🛡️ Notion 持续治理系统 (Notion Governance OS)

**像维护代码仓库一样维护你的 Notion 知识库**

一套自动化的 Notion 治理、监控和维护系统，确保你的知识库始终保持整洁、结构化、可检索和高质量。

## 🎯 核心理念

```
Notion 知识库  =  代码仓库
治理系统       =  CI/CD 管线
巡检报告       =  测试报告
问题追踪       =  Issue Tracker
自动修复       =  自动化脚本
```

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                 Notion 持续治理系统 (Governance OS)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ 🔍 巡检层 │  │ 🛠️ 修复层 │  │ 📊 监控面板    │  │ 📋 文档 │ │
│  │          │  │          │  │              │  │         │ │
│  │ • 完整性  │→│ • 自动命名│→│ • 治理数据库  │→│ • 运维手册│ │
│  │ • 编码    │  │ • 去重    │  │ • 问题追踪    │  │         │ │
│  │ • 分类    │  │ • 归档    │  │ • 健康评分    │  │         │ │
│  │ • 关联    │  │ • 关联    │  │ • 定期报告    │  └─────────┘ │
│  └──────────┘  └──────────┘  └──────────────┘              │
│                                                             │
│  ⏰ 定时任务：每日快检 + 每周深度巡检 + 每月报告              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 核心组件

### 1. 🔍 scanner.py — 巡检引擎
**功能：** 全量/增量扫描 Notion 工作区，检测所有问题

**检测维度：**
- ✅ **完整性检查** - 无标题页面、空数据库、未归档内容
- ✅ **编码问题** - 乱码标题修复（UTF-8 编码损坏）
- ✅ **命名规范** - 模糊命名、数字编号、临时标记
- ✅ **结构化程度** - 页面散落检测、数据库利用率
- ✅ **重复内容** - 相似标题、内容重复
- ✅ **关联性** - 孤立页面、断开的引用

**输出：** JSON 报告 + 缓存机制

**使用：**
```bash
# 全量扫描
python scanner.py --full

# 增量扫描 (快速)
python scanner.py --incremental

# 限制扫描数量
python scanner.py --limit 100

# 保存报告
python scanner.py --output /path/to/report.json
```

**配置：** `notion_gov_config.json`

### 2. 📊 dashboard.py — 治理数据库写入器
**功能：** 将巡检结果写入 Notion 治理数据库，实现可视化追踪

**重要参数：**
- `--offset N`: 从第 N 条问题开始写入（配合 --limit 实现分批滑动窗口写入）
- `--limit N`: 最多写入 N 条
- `--only-critical`: 仅写入 🔴严重问题
- 内置去重逻辑：通过 `type:page_id` 指纹避免重复写入

> **Pitfall:** `--limit` 总是取前 N 条，不加 `--offset` 无法实现滑动窗口分批。第一次写入后剩余条目需要配合 `--offset` 才能跳过已写入的问题。

**治理数据库结构：**
```
📋 治理面板 (Governance Panel)
├── Name (标题) - 问题页面标题
├── 问题类型 (Select) - 完整性/编码/命名/结构/重复/关联
├── 严重级别 (Select) - 🔴严重 / 🟡警告 / 🟢信息
├── 状态 (Select) - 待处理/进行中/已解决/已忽略
├── 关联页面ID (Rich Text) - 问题页面的 ID
├── 发现日期 (Date) - 问题发现时间
├── 修复日期 (Date) - 问题修复时间
├── 自动化 (Checkbox) - 是否可自动修复
└── 备注 (Rich Text) - 详细说明和处理建议
```

**写入策略：**
- 🔴严重问题立即写入
- 🟡警告问题批量写入
- 自动标记可自动修复项

**使用：**
```bash
# 写入巡检报告
python dashboard.py /path/to/scan_report.json

# 仅写入严重问题
python dashboard.py /path/to/scan_report.json --severity critical
```

### 3. 🛠️ fixer.py — 自动修复引擎
**功能：** 自动修复可自动化修复的问题

**支持的自动修复：**
- ✅ **乱码标题修复** — 从页面 H1 标题推断正确标题
- ✅ **无标题页面命名** — 基于内容生成描述性标题
- ✅ **空数据库归档** — 将空数据库移动到归档区域

**修复策略（按优先级）：**
1. 提取页面内容中的 H1 标题（`# 标题` 或 `## 标题`）
2. 如果没有 H1，取首行非空内容（截断至 60 字）
3. 如果是空页面 → 标记为「空页面（待清理）」

**使用：**
```bash
# 按类型修复
python fixer.py report.json --type 编码损坏
python fixer.py report.json --type 无标题

# Dry-run 预览（不实际修改）
python fixer.py report.json --type 编码损坏 --dry-run --limit 3
```

**已验证的端到端修复流程：**
```
scanner.py 检测 → fixer.py 自动修复 → curl PATCH 写回 Notion → 验证修复后标题
```
成功修复示例：`"?? ��Ŀ�浵"` → `"🤖 AI API 自动监控系统 — 项目总结"`

**集成到 Cron 管线：**
每周深度巡检先跑 fixer 再跑 dashboard，确保写入治理DB前问题已修复：
```
scanner.py → fixer.py --type 编码损坏 → fixer.py --type 无标题 → dashboard.py
```

### 4. ⏰ Cron 定时任务
**双级调度系统（已验证部署）：**

| 任务级别 | Cron ID | 频率 | 执行时间 | 模式 | 输出 |
|---------|---------|------|----------|------|------|
| 🔍 每日快检 | `3dbb3c951f5c` | 每天 | 09:00 | 增量扫描 → 自动修复 → 简报 | 🔴严重问题中文报告 |
| 🔬 每周深度 | `6fa3f7afb10f` | 每周一 | 09:00 | 全量扫描 → fixer → dashboard | 写入治理DB + 更新状态 |
| 📊 一次性批量 | （已删） | 手动 | — | 分批滑动窗口(50-100条) | 1062条问题全量入库 |

**实际 Cron 管线（以每周深度为例）：**
```
scanner.py --incremental (或 --full)
  → fixer.py --type 编码损坏    ← 自动修复乱码
  → fixer.py --type 无标题      ← 自动修复无标题
  → dashboard.py                 ← 写入治理DB（去重）
```

**已验证的部署数据：**
- 治理数据库: `02d80532-c500-486c-92e1-ec374f51b06c` (Hermes 数据中心)
- 首次扫描: 5,937 条目 → 1,062 问题 (306🔴 + 756🟡)
- 批量写入: 822 新增 + 194 跳过，0 错误
- 自动修复: 11/11 乱码 + 8/8 无标题 全部修复

**创建 Cron 的通用模板：**
```bash
hermes cronjob create \
  --name "描述" \
  --schedule "cron_表达式" \
  --prompt "自包含的完整任务描述（所有路径用绝对路径）" \
  --skills ["notion"] \
  --enabled_toolsets '["terminal","file"]'
```

> ⚠️ Cron prompt 必须自包含（无当前会话上下文）。不要在 prompt 里引用 `C:\Users\win10\.hermes\` 的相对路径。

## 🚀 快速开始

### 第一步：环境准备

```bash
# 1. 确保 Notion API Key 已配置
# 文件: ~/.hermes/.env
NOTION_API_KEY=ntn_your_integration_token_here

# 2. 克隆治理系统脚本
mkdir -p ~/.hermes/scripts/notion-governance
cd ~/.hermes/scripts/notion-governance

# 3. 复制脚本文件 (从本技能的 references/scripts/ 目录)
# 脚本已包含在技能安装中
```

### 第二步：初始化治理数据库

```bash
# 运行初始化脚本创建治理数据库
python dashboard.py --init

# 或者手动创建：
# 1. 在 Notion 中创建一个页面 "🛡️ 治理面板"
# 2. 使用 Notion API 创建数据库
# 3. 配置数据库 ID 到 notion_gov_config.json
```

### 第三步：首次全量扫描

```bash
# 运行全量扫描
python scanner.py --full --output ~/.hermes/reports/scan_initial.json

# 查看扫描结果
cat ~/.hermes/reports/scan_initial.json | jq '.summary'

# 写入治理数据库
python dashboard.py ~/.hermes/reports/scan_initial.json
```

### 第四步：自动修复

```bash
# 查看可修复问题
python fixer.py ~/.hermes/reports/scan_initial.json --dry-run

# 执行修复
python fixer.py ~/.hermes/reports/scan_initial.json
```

### 第五步：设置定时任务

```bash
# 创建每日快检 Cron
hermes cronjob create \
  --name "Notion-每日快检" \
  --schedule "0 9 * * *" \
  --prompt "使用 scanner.py 增量扫描 Notion 工作区，检测 🔴严重问题并写入治理数据库" \
  --skills ["notion"]

# 创建每周深度 Cron
hermes cronjob create \
  --name "Notion-每周深度" \
  --schedule "0 9 * * 1" \
  --prompt "使用 scanner.py 全量扫描 Notion 工作区，检测所有问题并写入治理数据库，生成健康评分" \
  --skills ["notion"]
```

## 📋 问题分类与处理流程

### 🔴 严重问题 (Critical)
**定义：** 影响知识库可用性和搜索效果的问题

| 问题类型 | 检测条件 | 自动修复 | 优先级 |
|----------|----------|----------|--------|
| 无标题页面 | 页面标题为空 | ❌ 手动 | 高 |
| 编码损坏标题 | 标题包含乱码字符 | ✅ 自动 | 高 |
| 空数据库 | 数据库内无条目 | ✅ 自动 | 中 |
| 未授权页面 | 页面无法访问 | ❌ 手动 | 高 |

**处理流程：**
```
检测 → 写入治理数据库 → 通知用户 → 自动修复(如支持) → 验证 → 关闭
```

### 🟡 警告问题 (Warning)
**定义：** 不影响核心功能但影响用户体验的问题

| 问题类型 | 检测条件 | 自动修复 | 优先级 |
|----------|----------|----------|--------|
| 模糊命名 | 标题为"1""2""临时"等 | ✅ 自动 | 中 |
| 页面散落 | 页面不在任何数据库中 | ❌ 建议 | 低 |
| 重复标题 | 相似标题的页面 | ✅ 建议 | 中 |
| 低利用率数据库 | 数据库条目 < 5 | ✅ 建议 | 低 |
```

### 🟢 信息问题 (Info)
**定义：** 优化建议和最佳实践提醒

| 问题类型 | 检测条件 | 自动修复 | 优先级 |
|----------|----------|----------|--------|
| 命名建议 | 标题不够描述性 | ✅ 建议 | 低 |
| 分类建议 | 页面缺少标签 | ✅ 建议 | 低 |
| 结构建议 | 建议使用数据库而非页面 | ❌ 建议 | 低 |
```

## 📊 健康评分系统

系统会为每次扫描生成健康评分：

```json
{
  "scan_id": "2026-07-12-001",
  "timestamp": "2026-07-12T09:00:00Z",
  "summary": {
    "total_pages": 5937,
    "total_databases": 270,
    "problems_found": 1062,
    "critical": 306,
    "warning": 756,
    "info": 0,
    "health_score": 78.5,
    "trend": "improving"
  },
  "details": {
    "critical_breakdown": {
      "untitled_pages": 25,
      "encoding_issues": 11,
      "empty_databases": 42
    },
    "warning_breakdown": {
      "vague_titles": 173,
      "orphaned_pages": 116,
      "low_utilization": 145
    }
  }
}
```

**评分标准：**
- 100分：完美状态
- 80-99分：良好，轻微问题
- 60-79分：需要关注，多个问题
- <60分：需要立即处理

## 🔧 配置管理

### 配置文件：`notion_gov_config.json`

```json
{
  "gov_database_id": "02d80532-c500-486c-92e1-ec374f51b06c",
  "gov_data_source_id": "9005166f-b0f6-40e2-9336-2f1d00755840",
  "url": "https://app.notion.com/p/02d80532c500486c92e1ec374f51b06c",
  "parent_page": "Hermes 数据中心",
  "parent_page_id": "39b86cdd-9a32-81bd-a252-c45cf86c4924",
  "created_at": "2026-07-13",
  "properties": {
    "Name": "title",
    "问题类型": "select",
    "严重级别": "select",
    "状态": "select",
    "关联页面ID": "rich_text",
    "发现日期": "date",
    "修复日期": "date",
    "自动化": "checkbox",
    "备注": "rich_text"
  },
  "test_entry": "39c86cdd-9a32-81b3-bf74-c41019267d16"
}
```

### 缓存文件：`notion_scan_cache.json`

用于增量扫描，存储上次扫描的状态，避免重复检查。

## 📈 监控与报告

### 实时监控面板
治理数据库同时作为监控面板，实时显示：
- 📊 问题统计（按类型、严重级别、状态分组）
- 📈 健康评分趋势图
- ⏰ 问题处理进度
- 🔔 待处理问题提醒

### 定期报告
| 报告类型 | 频率 | 内容 | 发送对象 |
|----------|------|------|----------|
| 每日快报 | 每天 | 🔴严重问题列表 | 用户邮件 |
| 每周报告 | 每周 | 🔴🟡所有问题 + 健康评分 | 用户 + 治理频道 |
| 每月报告 | 每月 | 趋势分析 + 改进建议 | 用户 + 团队 |

## 🛠️ 故障排除

### 常见问题

**Q: API Token 过期怎么办？**
A: 在 https://www.notion.so/my-integrations 创建新的 Integration Token，更新到 `~/.hermes/.env`，然后重启 Hermes。

**Q: 扫描速度太慢怎么办？**
A: 使用 `--limit` 参数限制扫描数量，或者使用 `--incremental` 增量扫描模式。

**Q: 治理数据库写入失败怎么办？**
A: 检查数据库 ID 是否正确，确保 Integration 有对数据库的写入权限。

**Q: 自动修复没有效果怎么办？**
A: 使用 `--dry-run` 模式预览修复效果，确认问题类型支持自动修复。

### 日志查看

```bash
# 查看扫描日志
cat ~/.hermes/logs/scanner_*.log

# 查看修复日志
cat ~/.hermes/logs/fixer_*.log

# 查看治理数据库写入日志
cat ~/.hermes/logs/dashboard_*.log
```

## 📚 最佳实践

### 1. 治理系统部署建议

```bash
# 推荐部署结构
~/.hermes/
├── scripts/
│   └── notion-governance/
│       ├── scanner.py        # 巡检引擎
│       ├── dashboard.py      # 写入器
│       ├── fixer.py          # 修复引擎
│       └── utils.py          # 工具函数
├── reports/
│   ├── scan_latest.json      # 最新扫描报告
│   ├── scan_initial.json     # 初始扫描报告
│   └── scan_YYYY-MM-DD.json  # 历史报告
├── logs/
│   ├── scanner_*.log
│   ├── dashboard_*.log
│   └── fixer_*.log
├── notion_gov_config.json     # 配置文件
└── notion_scan_cache.json     # 缓存文件
```

### 2. 命名规范建议

```
✅ 推荐格式：
- "📝 2026-Q3 产品路线图"
- "🤖 AI 音乐生成器 - 技术文档"
- "📊 用户增长分析 - 2026年6月"
- "🔧 系统架构设计 - v2.1"

❌ 避免格式：
- "1" "2" "3" (数字编号)
- "临时" "草稿" "测试" (临时标记)
- "Untitled" (无标题)
- "New Page 1" (默认命名)
```

### 3. 结构化组织建议

```
📁 知识库根目录
├── 📊 数据仓库 (数据库集中管理)
│   ├── 📈 产品指标
│   ├── 👥 用户画像
│   └── 💰 财务数据
├── 📝 文档库 (页面集中管理)
│   ├── 🎯 项目文档
│   ├── 🛠️ 技术文档
│   └── 📚 学习笔记
├── 🔄 归档区 (历史内容)
└── 🛡️ 治理面板 (问题追踪)
```

### 4. 定期维护建议

```bash
# 每月任务
1. 运行全量扫描
2. 生成健康评分报告
3. 处理所有 🟡 警告问题
4. 更新治理系统配置

# 每季度任务
1. 重新评估知识库结构
2. 清理归档区域
3. 更新命名规范
4. 优化治理系统
```

## 🔗 相关技能

- **[notion](productivity/notion)** - Notion API 基础使用
- **[plan](software-development/plan)** - 项目计划和执行
- **[github-pr-workflow](github/github-pr-workflow)** - PR 工作流最佳实践

## 📖 参考资料

### 📖 技能文档与模板
- **[report-format.md](references/report-format.md)** - 巡检报告格式规范
- **[notion-api-v2025-quirks.md](references/notion-api-v2025-quirks.md)** - Notion API v2025-09-03 关键行为与踩坑记录
- **[wankai-weekly-system.md](references/wankai-weekly-system.md)** - 万凯工作台周报系统（基于同一 API 模式的 Worker 延伸案例）
- **[quick-start.sh](templates/quick-start.sh)** - 快速启动脚本
- **[health_score.py](scripts/health_score.py)** - 健康评分计算器

### 🔗 外部链接
- [Notion API 文档](https://developers.notion.com)
- [Notion 数据库 vs 数据源](https://developers.notion.com/docs/working-with-databases)
- [Notion Workers 文档](https://developers.notion.com/workers)
- [Hermes Cron 任务调度](https://hermes-agent.nousresearch.com/docs/cronjob)

## 🎯 总结

Notion 持续治理系统为你提供了一套完整的 Notion 知识库运维解决方案，让你的知识库从"一次性整理"变成"持续运维"。

**核心价值：**
- ✅ **自动化** - 减少人工维护成本
- ✅ **实时监控** - 及时发现问题
- ✅ **智能修复** - 自动处理可修复问题
- ✅ **可视化追踪** - 问题一目了然
- ✅ **持续改进** - 定期健康评估

**适用场景：**
- 🏢 企业知识库维护
- 👥 团队文档管理
- 📚 个人笔记整理
- 🎓 学习资料管理
- 🔧 任何需要长期维护的 Notion 知识库

---

**💡 提示：** 将这个技能标记为收藏，下次需要维护 Notion 时直接加载即可！