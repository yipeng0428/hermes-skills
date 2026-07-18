# 会话历史同步技术实现

## 概述

Hermes 的会话历史存储在 `~/AppData/Local/hermes/state.db`（Windows）或 `~/.hermes/state.db`（macOS/Linux）中。数据库包含 `sessions`、`messages` 和 `messages_fts`（全文索引）表。

**关键发现**：state.db 文件可能很大（32MB+），但真正的用户/助手对话文本通常只有 ~50KB。绝大部分空间被 FTS 全文索引占用。因此导出时只提取 `role IN ('user', 'assistant')` 的消息，跳过工具调用。

## state.db Schema

### sessions 表
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    source TEXT,
    user_id TEXT,
    session_key TEXT,
    chat_id TEXT,
    chat_type TEXT,
    thread_id TEXT,
    display_name TEXT,
    origin_json TEXT,
    expiry_finalized INTEGER DEFAULT 0,
    model TEXT,
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    title TEXT,
    archived INTEGER NOT NULL DEFAULT 0,
    -- ... 其他列
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);
```

### messages 表
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'tool'
    content TEXT,
    timestamp REAL,
    active INTEGER DEFAULT 1,
    tool_call_id TEXT,
    tool_calls TEXT,
    tool_name TEXT,
    -- ... 其他列
);
```

### messages_fts 表（FTS5 虚拟表）
```sql
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content, 
    content='messages', 
    content_rowid='id'
);
```

## 导出脚本 (export_sessions.py)

### 核心逻辑
1. 连接 state.db
2. 查询所有会话（可排除已归档）
3. 对每个会话，查询 `role IN ('user', 'assistant')` 且 `content IS NOT NULL` 的消息
4. 跳过超长内容（>5000字符且以 `{` 开头，通常是工具输出残留）
5. 生成 JSON 文件

### 输出格式
```json
{
  "version": "1.0",
  "exported_at": "2026-07-12T23:39:16",
  "source_db": "C:\\Users\\win10/AppData\\Local\\hermes\\state.db",
  "total_sessions": 1,
  "total_messages": 11,
  "total_chars": 1170,
  "sessions": [
    {
      "session_id": "20260712_232536_d5a33e",
      "title": "我们共同的GitHub仓库",
      "started": "2026-07-12T23:25:58",
      "ended": null,
      "archived": false,
      "model": "LongCat-2.0",
      "message_count": 11,
      "total_chars": 1170,
      "messages": [
        {
          "role": "user",
          "content": "你还记得我们共同运营的那个github吗",
          "time": "2026-07-12T23:25:58"
        }
      ]
    }
  ]
}
```

### 使用方式
```bash
# 导出到默认位置（~/.hermes/sync_backups/sessions/）
python ~/.hermes/scripts/hermes-sync/export_sessions.py

# 导出到指定路径
python ~/.hermes/scripts/hermes-sync/export_sessions.py /path/to/output.json
```

## 导入脚本 (import_sessions.py)

### 核心逻辑
1. 读取 JSON 文件
2. 对每个会话：
   - 检查 `session_id` 是否已存在（跳过重复）
   - 插入 `sessions` 表（`source='sync_import'`）
   - 插入 `messages` 表
   - 同步插入 `messages_fts` 索引
3. 清理孤立 FTS 条目

### 关键注意事项
- **FTS 索引必须同步更新**：插入 messages 后必须立即插入 messages_fts，否则全文搜索无法找到导入的消息
- **跳过已存在会话**：通过 `session_id` 唯一性检查避免重复导入
- **时间戳转换**：ISO 格式时间需转换为 Unix timestamp
- **内容截断**：超过 10000 字符的内容会被截断（防止异常数据）

### 使用方式
```bash
# 预览导入（不实际写入）
python ~/.hermes/scripts/hermes-sync/import_sessions.py sessions.json --dry-run

# 实际导入
python ~/.hermes/scripts/hermes-sync/import_sessions.py sessions.json
```

## 同步脚本更新

### sync_to_notion.py（公司电脑）
在步骤3中调用 `export_sessions.py` 将对话导出到快照目录：
```python
def backup_conversations(self):
    from export_sessions import export_all_sessions
    session_dir = os.path.join(self.sync_dir, "sessions")
    os.makedirs(session_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_path = os.path.join(session_dir, f"sessions_export_{timestamp}.json")
    result = export_all_sessions(export_path)
    return {"export_path": result, "size_kb": ...}
```

### sync_from_notion.py（家里电脑）
在步骤2中调用 `import_sessions.py` 从快照恢复对话：
```python
def sync_conversations_from_snapshot(self):
    latest_snapshot = self.find_latest_snapshot()
    sessions_file = os.path.join(latest_snapshot, "sessions_export.json")
    if not os.path.exists(sessions_file):
        # 回退到 sessions 子目录
        sessions_files = glob.glob(os.path.join(self.sync_dir, "sessions", "*.json"))
        sessions_files.sort(reverse=True)
        sessions_file = sessions_files[0] if sessions_files else None
    if sessions_file:
        from import_sessions import import_sessions
        import_sessions(sessions_file)
```

## 验证方法

### 1. 导出验证
```bash
python -c "
import json
with open('sessions_export.json') as f:
    data = json.load(f)
print(f'会话数: {data[\"total_sessions\"]}')
print(f'消息数: {data[\"total_messages\"]}')
for s in data['sessions']:
    print(f'  {s[\"title\"]}: {s[\"message_count\"]} msgs')
"
```

### 2. 导入验证
```python
import sqlite3
conn = sqlite3.connect(r'C:/Users/win10/AppData/Local/hermes/state.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sessions")
print(f"会话数: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM messages")
print(f"消息数: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM messages_fts")
print(f"FTS索引: {cursor.fetchone()[0]}")
conn.close()
```

### 3. 内容完整性检查
```python
cursor.execute("SELECT id, title FROM sessions WHERE source = 'sync_import'")
for row in cursor.fetchall():
    print(f"已导入: {row[1]}")
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 导入后搜索不到消息 | FTS 索引未同步 | 检查 messages_fts 表是否有对应 rowid |
| 会话重复导入 | 未检查 session_id 唯一性 | 导入脚本已内置跳过逻辑 |
| 导出文件过大 | 包含了工具调用消息 | 检查 `role IN ('user', 'assistant')` 过滤 |
| state.db 被占用 | Hermes 正在运行 | 关闭 Hermes 后重试，或复制 state.db 到临时位置操作 |

## 跨平台路径

| 平台 | state.db 路径 |
|------|---------------|
| Windows | `~/AppData/Local/hermes/state.db` |
| macOS | `~/.hermes/state.db` |
| Linux | `~/.hermes/state.db` |

脚本使用 `os.path.expanduser` 自动适配。
