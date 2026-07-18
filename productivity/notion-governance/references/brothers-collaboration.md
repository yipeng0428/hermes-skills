# Hermes 兄弟协作系统 (Brothers Collaboration System)

> 两台 Hermes（公司 + 家里）通过 Notion 共享数据库互通消息，共同服务同一位用户。

## 架构

```
🏢 Hermes·公司 (工作电脑)          🏠 Hermes·家里 (家庭电脑)
       │                                  │
       └────── 📬 兄弟消息板 ──────────────┘
              (Notion 数据中心)
```

## 身份标识

每台 Hermes 通过 `~/.hermes/hermes_identity.json` 确认自己身份：

```json
{
  "identity": "company",
  "display_name": "🏢 Hermes·公司",
  "brother": {
    "name": "Hermes·家里",
    "identity": "home",
    "emoji": "🏠"
  },
  "notion_signature_format": "[🏢 Hermes·公司 | {timestamp}]"
}
```

## 兄弟消息板数据库

位于 Notion「Hermes 数据中心」页面下。

| Property | Type | Options |
|----------|------|---------|
| Name | Title | 消息标题 |
| 发送者 | Select | 🏢 Hermes·公司 / 🏠 Hermes·家里 |
| 消息类型 | Select | 👋签到 / 📢公告 / 💬留言 / 📋任务 / 🔄同步 / ⚠️警告 / 📝笔记 |
| 状态 | Select | 📥未读 / 👀已读 / ↩️已回复 / ✅已处理 |
| 优先级 | Select | 🔥紧急 / ⚡重要 / 📌普通 / 💤低 |
| 发送时间 | Date | ISO 8601 |
| 关联页面 | Rich text | 相关 Notion 页面链接 |
| 内容 | Rich text | 消息正文 |

## 核心协议

### 1. 签名约定

在 Notion 写入任何内容时，末尾加签名行：
```
📝 由 [🏢 Hermes·公司] 记录 · 2026-07-16 15:30 CST
```

### 2. 每日签到

每天第一次互动时：
1. 检查 `~/.hermes/.last_checkin_date` 是否今日
2. 若非今日，运行 `hermes_brothers_check.py --mark-read` 查询兄弟消息
3. 可选：发送签到消息 `hermes_brothers_post.py --checkin`

### 3. 消息类型使用

| 类型 | 场景 |
|------|------|
| 👋 每日签到 | 每日自动签到 |
| 📢 公告 | 系统变更、新功能部署 |
| 💬 留言 | 一般性留言 |
| 📋 任务 | 指派任务给兄弟 |
| 🔄 同步状态 | 同步完成/失败通知 |
| ⚠️ 警告 | 问题通知 |
| 📝 笔记 | 共享备忘/配置 |

### 4. 优先级响应

| 优先级 | 响应时间 |
|--------|---------|
| 🔥 紧急 | 下次互动时 |
| ⚡ 重要 | 24小时内 |
| 📌 普通 | 方便时 |
| 💤 低 | 无需回复 |

## 操作脚本

```bash
# 发送消息
python ~/.hermes/scripts/hermes_brothers_post.py \
  --type "💬 留言" --priority "📌 普通" \
  --title "标题" --content "内容"

# 检查消息（仅未读）
python ~/.hermes/scripts/hermes_brothers_check.py

# 检查全部 + 标记已读
python ~/.hermes/scripts/hermes_brothers_check.py --all --mark-read
```

## 数据库创建

使用 create-then-PATCH 模式。⚠️ 注意 data_source_id ≠ database_id（需通过 search API 获取真实 data_source_id 后再 PATCH 属性）。

## 与跨设备同步的关系

- **跨设备同步**（`hermes-cross-device-sync`）：文件备份、对话导出/导入，按时间表运行
- **兄弟协作**（本系统）：实时消息、签到、任务指派，事件驱动

两者互补：同步搬运数据，消息传递意图。
