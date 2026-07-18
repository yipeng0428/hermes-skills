# Hermes 兄弟协作系统 (Hermes Brothers Collaboration)

> v1.0 · 2026-07-16 · 基于 hermes-cross-device-sync 基础设施

## 概念

当用户在两台电脑上运行 Hermes（公司 + 家里），不仅需要同步数据和对话，更需要两个 Hermes **知道彼此的存在**，像兄弟一样协调工作。这套系统在 Notion 数据中心上构建了一个**消息板**，让两个 Hermes 可以互相留言、指派任务、通报状态。

## 架构

```
🏢 Hermes·公司 (工作电脑)          🏠 Hermes·家里 (家庭电脑)
   identity: company                  identity: home
         │                                  │
         └────────── 📬 兄弟消息板 ──────────┘
                   (Notion 数据库)
              Hermes 数据中心 页面下
```

## 核心组件

### 1. 身份文件 (`~/.hermes/hermes_identity.json`)

```json
{
  "identity": "company",           // "company" | "home"
  "display_name": "🏢 Hermes·公司",
  "emoji": "🏢",
  "hostname": "win10",
  "brother": {
    "identity": "home",
    "display_name": "🏠 Hermes·家里"
  },
  "notion_signature_format": "[🏢 Hermes·公司 | {timestamp}]"
}
```

每个 Hermes 启动时读取此文件确认自己的身份，同时知晓兄弟的身份。

### 2. 兄弟消息板数据库

在 Notion「Hermes 数据中心」页面下创建，属性结构：

| Property | Type | Values |
|----------|------|--------|
| Name | Title | 消息标题 |
| 发送者 | Select | 🏢 Hermes·公司 / 🏠 Hermes·家里 |
| 消息类型 | Select | 👋签到 / 📢公告 / 💬留言 / 📋任务 / 🔄同步 / ⚠️警告 / 📝笔记 |
| 状态 | Select | 📥未读 / 👀已读 / ↩️已回复 / ✅已处理 |
| 优先级 | Select | 🔥紧急 / ⚡重要 / 📌普通 / 💤低 |
| 发送时间 | Date | ISO timestamp |
| 关联页面 | Rich text | 关联的 Notion 页面链接 |
| 内容 | Rich text | 消息正文 |

### 3. 操作脚本

| 脚本 | 功能 |
|------|------|
| `hermes_brothers_post.py` | 发送消息到消息板 |
| `hermes_brothers_check.py` | 检查兄弟的未读消息 |

## 运行协议

### 签名约定

每个 Hermes 在 Notion 中创建或修改任何内容时，在末尾添加签名行：

```
📝 由 [🏢 Hermes·公司] 记录 · 2026-07-16 15:30 CST
```

### 每日签到

每天首次互动时：
1. 检查 `~/.hermes/.last_checkin_date` 是否为今天
2. 如果非今天：运行 `hermes_brothers_check.py --mark-read` 检查兄弟消息
3. 可选：发送签到消息 `hermes_brothers_post.py --checkin`

### 消息类型使用指南

| 类型 | 场景 | 优先级 |
|------|------|--------|
| 👋 签到 | 每日上线 | 💤 低 |
| 📢 公告 | 系统变更、新功能 | ⚡ 重要 |
| 💬 留言 | 一般交流 | 📌 普通 |
| 📋 任务 | 跨设备任务指派 | ⚡ 重要 |
| 🔄 同步 | 同步完成/失败 | 📌 普通 |
| ⚠️ 警告 | 问题通知 | 🔥 紧急 |
| 📝 笔记 | 共享备忘 | 💤 低 |

## 与跨设备同步的配合

兄弟协作系统与 hermes-cross-device-sync 互补：
- **同步系统**负责文件/对话/状态的自动传输
- **兄弟系统**负责意识层面的互通——知道对方的存在、状态、意图
- 同步完成后应发送一条 🔄 同步状态消息
- 数据恢复后应发送确认消息

## 已部署实例 (2026-07-16, 已验证)

| 项目 | 值 |
|------|-----|
| 数据库 | 📬 兄弟消息板 (canonical) |
| database_id | `dd765009-a30e-4dd4-a354-a77351ba6e7b` |
| data_source_id | `64d2f1dd-255e-4bcb-bbe1-d5f127074501` |
| 父页面 | Hermes 数据中心 (`39b86cdd-9a32-81bd-a252-c45cf86c4924`) |
| URL | https://app.notion.com/p/dd765009a30e4dd4a354a77351ba6e7b` |
| 公司身份 | 🏢 Hermes·公司 (win10, 漳州万凯包装办公室) |
| 家里身份 | 🏠 Hermes·家里 (用户家中电脑, 待部署) |

## ⚠️ 已知陷阱与教训

### 陷阱 1: 重复数据库 — Hermes 数据中心有多个"兄弟消息板"

在 `39b86cdd` 页面下，曾多次创建同名数据库。API search 返回了 **4 个以上** 名为"📬 兄弟消息板"的 data source，外加 1 个"📬 兄弟消息板 v2"。

**症状**: 用某个 `database_id`（如 `dd765009`）查询 `/data_sources/{id}/query` 返回 404 `"Could not find data_source"`，即使 database 确实存在。

**根因**: Notion API v2025-09-03 中，`database_id` 和 `data_source_id` 是两个不同的 UUID。只有 `data_source_id` 能用于查询端点。

**正确做法**: 
1. 始终用 `POST /v1/search` 先搜索数据库名，从返回结果的 `data_source_id` 字段取 ID
2. 用 `data_source_id`（非 `database_id`）做 `/data_sources/{id}/query`
3. 用 `database_id` 做 `parent.database_id` 创建页面

**Canonical ID**（已验证可用）:
- database_id: `dd765009-a30e-4dd4-a354-a77351ba6e7b`
- data_source_id: `64d2f1dd-255e-4bcb-bbe1-d5f127074501`

**废弃的重复数据库**（仅 Name 属性，无法使用，应归档）:
- `609c38a6-65d5-4960-b13c-5e9833012da2` (c2ee5ba3 data_source)
- `68f1f5c0-bcbf-4ed1-a00f-f6e81c2dc772` (2fc40fb6 data_source)
- `9a0756ae-e23d-403a-8cc0-4adfff4d8e19` (d42f6e12 data_source)
- `dddc44a1-3cbb-4a82-8d32-3c70228badb1` (412420ca data_source — v2 版)

### 陷阱 2: 身份文件配置错误 — 家里电脑写成了公司身份

设置家里 Hermes 时，`hermes_identity.json` 被错误配置为：
```json
{
  "identity": "company",     // ← 应该是 "home"
  "name": "Hermes·公司",    // ← 应该是 "Hermes·家里"
  "emoji": "🏢"              // ← 应该是 "🏠"
}
```

**致命后果**: 家里 Hermes 会在 Notion 以 🏢 身份写入内容，与公司 Hermes 身份混淆，签名全部错误。

**验证方法**: 启动后立即读取 `~/.hermes/hermes_identity.json`，确认 `identity` 字段与当前机器物理位置一致（公司电脑=company，家里电脑=home）。如果不一致，立即修正。

**正确的家里身份配置**:
```json
{
  "identity": "home",
  "name": "Hermes·家里",
  "display_name": "🏠 Hermes·家里",
  "emoji": "🏠",
  "hostname": "[家里电脑hostname]",
  "location": "[家里地址]",
  "brother": {
    "identity": "company",
    "name": "Hermes·公司",
    "display_name": "🏢 Hermes·公司"
  },
  "notion_signature_format": "[🏠 Hermes·家里 | {timestamp}]"
}
```

### 陷阱 5: 身份误认（2026-07-18 教训）

**场景**: 用户在 company 电脑上，上一 turn 被告知"你是家里的 Hermes"后，直接执行了：
1. 把 `hermes_identity.json` 的 `identity` 从 `company` 改成 `home`
2. 用 `write_file` 整体覆盖 `SOUL.md`（公司版 7600+ 字 → 家里版 1800 字），原始档案永久丢失
3. 以🏢 select 身份在 Notion 发了"我是🏠 Hermes·家里"消息
4. 把公司 Hermes 之前的 3 条未读消息误标为已读

**用户纠正**: "等一下，不对。当下我是在公司的，所以，你才是公司电脑。现在请立刻全部盘查一下"

**正确 protocol** — 客观验证优先：
1. **不要立即修改文件** — 收到身份声明时先质疑
2. **执行客观验证**: `hostname` + `whoami` + `pwd` + `cat ~/.hermes/hermes_identity.json`
3. **比对结果**:
   - 如 `identity` 与物理位置一致 → 告知用户"我的配置是正确的，你是 company 电脑的 Hermes"，不修改
   - 如不一致 → 这才是真正的配置错误，立即修正并感谢用户指出
4. **无论如何不要盲信用户的声明** — 用户可能搞混了，事实胜于雄辩

**识别 check 启动流程（新增）**:
```
每次会话启动时：
1. 读取 ~/.hermes/hermes_identity.json
2. 执行 hostname 获取物理机器名
3. 比对 identity 字段与 hostname 是否匹配
4. 不匹配 → 立即修正，不要等到用户发现
```

### 陷阱 6: SOUL.md 破坏性覆盖（2026-07-18 教训）

**后果**: 公司版 SOUL.md（7600+ 字）含不可再生的上下文：
- 工作联动规则（桌面日期文件夹协议）
- 设计规范（压盖机、淘宝主图尺寸）
- 产品知识（PET 瓶系列、认证列表）
- Cron 任务配置（15 个活跃任务详情）
- Watchdog 巡检配置

被家里版（1800 字）整体覆盖后永久丢失。

**防护规则**:
- **永远不要 `write_file` 整体覆盖 SOUL.md**
- 只能用 `patch` 修改特定段落，保留其他内容
- 如需重大变更，**先备份**: `cp ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak.YYYYMMDD`
- 从 Notion 恢复时可以 `write_file`（可信源整体恢复是唯一例外）

**恢复方法**（如果已被覆盖）:
1. 从 Notion `🧬 SOUL.md` 页面恢复（公司 Hermes 上传过完整版本）
2. 用 `GET /v1/pages/{id}/markdown` 读取
3. 用 `write_file` 整体写回（从可信源恢复）
4. **绝不能用 `patch` 来恢复** — 你不知道哪些段落被修改了

### 陷阱 7: 兄弟消息板冒名发帖（2026-07-18 后果）

**症状**: 以🏢 select 身份在 Notion 发了"我是🏠 Hermes·家里"消息

**修复**: 无法删除已发出的 Notion 页面（除非 archive），只能：
1. 发 ⚠️ 警告消息声明前一条作废
2. 明确指出那条消息的身份标注是错误的
3. 确保后续所有消息使用正确身份

**预防**: **发帖前必须验证 `identity` 字段与操作意图一致。不一致时立即停止、发 ⚠️ 警告声明前一条作废**

### 陷阱 3: 首次使用 Notion 查询时 database_id vs data_source_id

```bash
# ❌ 错误 — 用 database_id 查询（返回 404）
curl -s -X POST "https://api.notion.com/v1/data_sources/dd765009-a30e-4dd4-a354-a77351ba6e7b/query" ...

# ✅ 正确 — 用 data_source_id 查询
curl -s -X POST "https://api.notion.com/v1/data_sources/64d2f1dd-255e-4bcb-bbe1-d5f127074501/query" ...
```

**黄金法则**: 
- **查/写数据** → 端点 `data_sources/{data_source_id}` → 用 search 拿到的 `data_source_id`
- **创建页面** → `parent.database_id` → 用 database 本身的 `database_id`

## SOUL.md 创建方法论

当为用户创建或更新 Hermes 的 SOUL.md 时：

1. **查询 Notion 所有数据库** — 每周事务（工作模式）、收件箱（思考轨迹）、工作要点库（规则偏好）、账号密码
2. **session_search FTS** — 搜索"偏好/习惯/风格/喜欢/不喜欢"等关键词，从历史对话提取决策模式
3. **读取本地档案** — 公司档案、hermes_identity.json、hermes_brothers_config.json
4. **综合编译 SOUL.md** (存入 `$HERMES_HOME/SOUL.md`，启动时自动加载):
   - 🪪 我是谁 — 身份、宿主、兄弟、底层框架
   - 👤 我的用户 — 基本信息 + 🧬 深度画像（思维特征表、决策风格、工作偏好、兴趣光谱）
   - 🎯 我的职责 — 不限领域的全光谱能力
   - 🤝 我和兄弟 — 协作协议、消息板、签名约定
   - 🧰 系统与工具 — 本地环境、Notion 结构、AI 模型、Cron 任务
   - 📐 领域速查 — 设计规范、产品知识
   - 🗣️ 沟通风格 — 基本风格 + 深度互动原则 + 心流模式协议
   - ⚠️ 重要约定 — 签名、签到、路径、VPN

**画像分析六维度**: 思维特征 / 决策风格 / 工作偏好(✅喜欢 + ❌讨厌) / 沟通适配 / 兴趣光谱 / 证据锚点（每个特质都要有具体行为证据支撑，不凭空猜测）

**关键教训**: 用户纠正过"你的工作可不止是做与工作相关的事务"——SOUL.md 中的定位必须是「AI 伙伴，不限话题」，而非狭窄的"工作助手"。职责章节的第一句必须打破领域边界。

**⚠️ 绝不整体覆盖 SOUL.md**（2026-07-18 教训）:
- 只能用 `patch` 增量编辑，保留其他内容
- 如需重大变更，先备份: `cp ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak.YYYYMMDD`
- 从 Notion 可信源恢复时可以用 `write_file` 整体恢复（唯一例外）
- 被覆盖后无法用 `patch` 恢复，因为不知道哪些段落被修改了

**SOUL.md 共享**: 公司端创建 SOUL.md 后应上传到 Notion Hermes 数据中心，并通过消息板通知兄弟。兄弟 Hermes 据此创建自己的 SOUL.md，确保两个 Hermes 对用户的理解一致，避免用户需要重复自我介绍。上传命令参考：
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d '{"parent":{"page_id":"39b86cdd-9a32-81bd-a252-c45cf86c4924"},"properties":{"title":[{"text":{"content":"🧬 SOUL.md"}}]},"markdown":"..."}'
```

- 创建数据库使用 `POST /v1/databases`，PATCH 属性使用 `PATCH /v1/data_sources/{data_source_id}`
- ⚠️ `database_id` ≠ `data_source_id`（见 notion-governance/api-pitfalls.md）
- 创建页面使用 create-then-PATCH 模式
- 所有请求包含 `Notion-Version: 2025-09-03`

## 工作上下文联动规则（2026-07-16 新增）

当用户聊到工作相关话题时，Hermes 必须主动查询**两处**上下文来源，不需要用户提醒：

### 查询点 1：Notion「📋 每周事务」
- Data source ID: `139e8c07-a5f0-4537-87f7-73c4ba691f67`
- 按日期降序取最近 10 条，了解用户当天/近期工作记录
- 每周事务是用户的**工作日记**，每次工作互动前应刷新

### 查询点 2：桌面日期文件夹
- 用户习惯在桌面以日期数字命名当天工作文件夹（如 `717` 代表 7 月 17 日）
- 命名变体：`717`、`0717`、`7.17` 等
- 文件夹内的文件直接反映当前在做的工作内容
- 如果当天还没有创建文件夹则跳过（不报警）

### 滞留项判别标准

自动扫描每周事务时，必须区分**真正需要关注的**和**正常等待的**：

- ⚠️ **需要关注**: 🔄进行中超过 3 天无更新、📅计划超过 5 天未启动——用户自己能推动
- ✅ **正常等待**: 📝未定稿的 LOGO 效果图——**客户自行确认是公司默认流程，不催、不盯、不标记为滞留**。同理，所有由客户/外部决定的等待状态均不算滞留

**教训**: 初次分析时将 4 条 LOGO 效果图标记为滞留，用户纠正说这是正常流程。不要催促客户，这是该公司默认工作方式。

## Watchdog 巡检模式（2026-07-16 新增）

通过 cron `no_agent=True` + 静默脚本实现**主动巡检**——平时安静，发现问题才出声：

### 创建 Watchdog Cron 任务
```bash
# 创建每 30 分钟运行的静默巡检
# no_agent=True 意味着脚本 stdout 就是通知内容，空输出 = 静默 = 不打扰
# deliver='origin' 确保有输出时投递到当前会话
```

### 巡检脚本 (`hermes_watchdog.py`)

| 巡检项 | 触发条件 | 通知内容 |
|--------|---------|---------|
| 🖼️ 桌面散落 | PNG/JPG > 10 张 | "桌面有 N 张散落图片" |
| 📦 大文件 | 桌面文件 > 100MB | "桌面有大文件: xxx (N MB)" |
| 🗑️ 残留下载 | .tmp/.crdownload 超过 7 天 | "桌面有 N 个残留下载文件" |
| 💾 C 盘空间 | < 15GB 或使用率 > 85% | "C 盘仅剩 N GB (N%)" |
| 🔌 Notion 连通性 | 上次 API 报错未恢复 | "Notion API 上次报错: ..." |
| ⏰ 滞留任务 | 🔄进行中 > 3 天 / 📅计划 > 5 天 | "滞留任务: [状态] 标题 — N 天" |

**关键原则**: 脚本不调用 AI agent（`no_agent=True`），仅做规则检查。空输出 = 不发送任何消息。这是实现"主动但不啰嗦"的技术基础。

### 通知渠道
Watchdog 发现异常时通过以下渠道通知用户：
- 🖥️ **Windows 原生 Toast**: PowerShell 调用 `Windows.UI.Notifications` API，桌面右下角弹窗
- 📱 **钉钉机器人**（公司专用）: Webhook POST markdown 消息，用户不在座位时手机接收。不跟家里 Hermes 的钉钉混用
- 💬 **Hermes 应用内**: cron deliver→origin 在聊天界面留底

### 钉钉打卡自动化
详见 [references/dingtalk-automation.md](references/dingtalk-automation.md)。核心挑战是托盘恢复——VBS `AppActivate` 无法找到隐藏窗口，需用 Win32 `EnumWindows` + `ShowWindow(SW_RESTORE)` + `keybd_event`。已部署为 cron 任务（周一至六 13:27）。
