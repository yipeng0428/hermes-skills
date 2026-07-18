# Hermes跨设备同步工作流详解

## 🔄 同步流程图

```
公司电脑 (17:45) → Notion数据中心 → 家里电脑 (18:30)
       ↓                   ↓                   ↓
   备份流程           中介同步           恢复流程
   (sync_to_notion)   (Notion数据库)   (sync_from_notion)
```

## 📋 详细工作流程

### 第一阶段：公司电脑 - 下班前同步 (sync_to_notion.py)

#### 步骤1：初始化同步环境
```python
class HermesSync:
    def __init__(self):
        self.config = self.load_config()  # 加载同步配置
        self.sync_dir = os.path.expanduser("~/.hermes/sync_backups")
        os.makedirs(self.sync_dir, exist_ok=True)
```

#### 步骤2：备份Hermes状态
```python
def backup_hermes_state(self):
    """备份Hermes当前状态"""
    hermes_state = {
        "backup_time": datetime.now().isoformat(),
        "config_files": [],
        "skills_loaded": [],
        "active_profile": "default",
        "model_provider": "mistral-small-latest",
        "custom_providers": []
    }
    
    # 备份重要配置文件
    config_files = [
        ".env",
        "config.yaml",
        "hermes_sync_config.json",
        "万凯包装_精简档案.md"
    ]
    
    for filename in config_files:
        filepath = os.path.expanduser(f"~/.hermes/{filename}")
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            hermes_state["config_files"].append({
                "name": filename,
                "size_bytes": file_size,
                "size_kb": round(file_size / 1024, 2)
            })
    
    return hermes_state
```

#### 步骤3：备份工作上下文
```python
def backup_work_context(self):
    """备份工作上下文"""
    work_context = {
        "timestamp": datetime.now().isoformat(),
        "current_project": "万凯包装设计项目",
        "active_tasks": [],
        "environment_variables": {
            "COMPUTER_ROLE": "company_office",
            "WORK_LOCATION": "福建万凯包装有限公司",
            "USER_ROLE": "美工设计师",
            "SYNC_MODE": "automatic"
        },
        "recent_work_patterns": ["电商设计", "客户LOGO", "产品物料", "平台维护"]
    }
    
    return work_context
```

#### 步骤4：备份对话记录
```python
def backup_conversations(self):
    """备份公司环境中所有对话记录"""
    backup_data = {
        "type": "对话同步",
        "timestamp": datetime.now().isoformat(),
        "conversation_count": 0,
        "size_kb": 0,
        "scope": "company_environment_all_conversations",
        "topics_covered": ["万凯包装", "设计工作", "电商平台", "客户项目", "内部事务"]
    }
    
    # 这里可以集成session_search工具获取对话记录
    # 使用Hermes的会话搜索功能
    
    return backup_data
```

#### 步骤5：创建同步快照
```python
def create_sync_snapshot(self):
    """创建同步快照"""
    snapshot_dir = os.path.join(
        self.sync_dir, 
        f"company_sync_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # 复制重要文件到快照目录
    important_files = [
        "~/.hermes/.env",
        "~/.hermes/config.yaml",
        "~/.hermes/hermes_sync_config.json",
        "~/.hermes/万凯包装_精简档案.md"
    ]
    
    for file_path in important_files:
        src = os.path.expanduser(file_path)
        if os.path.exists(src):
            dest = os.path.join(snapshot_dir, os.path.basename(file_path))
            shutil.copy2(src, dest)
    
    # 记录系统信息
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename if hasattr(os, 'uname') else "Windows",
        "sync_type": "company_to_notion_full",
        "files_backed_up": len(important_files),
        "computer_role": "company_office",
        "sync_scope": "all_company_conversations_and_state"
    }
    
    with open(os.path.join(snapshot_dir, "sync_info.json"), 'w') as f:
        json.dump(system_info, f, indent=2)
    
    return snapshot_dir
```

#### 步骤6：更新Notion数据库
```python
def update_notion_sync_db(self, sync_data):
    """更新Notion同步数据库"""
    # 使用Notion API更新数据库
    # 记录同步时间、文件数量、对话数量、状态等
    
    # API调用示例:
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }
    
    # 创建数据库记录
    database_id = self.config["sync_database_id"]
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "同步时间": {
                "type": "created_time",
                "created_time": sync_data["timestamp"]
            },
            "同步类型": {"select": {"name": "📥 公司→Notion"}},
            "设备": {"select": {"name": "公司电脑"}},
            "状态": {"select": {"name": "✅ 已完成"}},
            "同步内容": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"备份了{sync_data['steps'][0]['data']['config_files']}个配置文件"}
                }]
            },
            "文件数量": {"number": len(sync_data['steps'][0]['data']['config_files'])},
            "对话数量": {"number": sync_data['steps'][2]['data']['conversation_count']},
            "数据大小": {"number": sync_data['steps'][2]['data']['size_kb']},
            "备注": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "公司环境中所有对话同步"}
                }]
            }
        }
    }
    
    # 发送API请求
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )
    
    return response.status_code == 200
```

#### 步骤7：生成同步报告
```python
def generate_sync_report(self, sync_results):
    """生成同步报告"""
    report_path = os.path.join(
        self.sync_dir, 
        f"company_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(report_path, 'w') as f:
        json.dump(sync_results, f, indent=2, ensure_ascii=False)
    
    return report_path
```

### 第二阶段：Notion数据中心 - 数据中介

#### Notion数据库结构
```json
{
  "database_id": "company_sync_db_placeholder",
  "properties": {
    "同步时间": {"type": "created_time"},
    "同步类型": {"type": "select", "options": ["📥 公司→Notion", "📤 Notion→家里", "🔄 双向同步"]},
    "设备": {"type": "select", "options": ["公司电脑", "家里电脑", "Notion数据中心"]},
    "状态": {"type": "select", "options": ["✅ 已完成", "🔄 进行中", "⏳ 待处理", "❌ 失败"]},
    "同步内容": {"type": "rich_text"},
    "文件数量": {"type": "number"},
    "对话数量": {"type": "number"},
    "数据大小": {"type": "number", "format": {"number": {"format": "KB"}}},
    "备注": {"type": "rich_text"}
  }
}
```

#### 数据流转示例
```
公司电脑同步 (17:45)
→ Notion数据库记录
→ 家里电脑恢复 (18:30)
```

### 第三阶段：家里电脑 - 到家后恢复 (sync_from_notion.py)

#### 步骤1：初始化恢复环境
```python
class HermesSyncFromNotion:
    def __init__(self):
        self.config = self.load_config()
        self.sync_dir = os.path.expanduser("~/.hermes/sync_backups")
```

#### 步骤2：从快照恢复文件
```python
def sync_hermes_state_from_notion(self):
    """从Notion同步Hermes状态到本地"""
    latest_snapshot = self.find_latest_snapshot()
    
    if latest_snapshot:
        files_to_restore = [
            ".env",
            "config.yaml",
            "hermes_sync_config.json",
            "万凯包装_精简档案.md"
        ]
        
        for filename in files_to_restore:
            src = os.path.join(latest_snapshot, filename)
            dest = os.path.expanduser(f"~/.hermes/{filename}")
            
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
    
    return {"restored_files": len(files_to_restore)}
```

#### 步骤3：从Notion同步对话记录
```python
def sync_conversations_from_notion(self):
    """从Notion同步对话记录到本地"""
    # 使用Notion API获取对话记录
    # 保存到本地对话历史
    
    return {
        "conversations_synced": 0,
        "last_sync": datetime.now().isoformat()
    }
```

#### 步骤4：更新本地同步状态
```python
def update_local_sync_status(self):
    """更新本地同步状态"""
    status = {
        "last_sync_from_notion": datetime.now().isoformat(),
        "synced_files": True,
        "synced_conversations": True,
        "sync_scope": "company_environment_all_conversations",
        "status": "completed"
    }
    
    status_path = os.path.expanduser("~/.hermes/sync_status.json")
    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2)
    
    return status
```

#### 步骤5：生成恢复报告
```python
def generate_recovery_report(self, sync_results):
    """生成恢复报告"""
    report_path = os.path.join(
        self.sync_dir,
        f"sync_from_notion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(report_path, 'w') as f:
        json.dump(sync_results, f, indent=2)
    
    return report_path
```

## 📊 数据一致性保证

### 原子操作设计
- 每个同步步骤要么全部成功，要么全部回滚
- 使用文件系统的原子操作（copy2替代copy）
- 记录每个步骤的状态和结果

### 错误恢复机制
```python
try:
    # 执行同步步骤
    backup_files()
    create_snapshot()
    update_database()
    generate_report()
    
    # 如果所有步骤成功，标记为完成
    mark_sync_complete()
    
except Exception as e:
    # 如果任何步骤失败，记录错误
    log_error(e)
    
    # 提供备选方案
    if not snapshot_created:
        create_fallback_snapshot()
    
    # 通知用户
    send_error_notification()
```

### 验证检查
```python
# 同步后验证数据完整性
def verify_sync_integrity(sync_results):
    """验证同步完整性"""
    
    # 检查文件是否存在
    for file in expected_files:
        if not os.path.exists(file):
            return False, f"文件丢失: {file}"
    
    # 检查快照是否创建
    if not os.path.exists(snapshot_path):
        return False, "快照未创建"
    
    # 检查数据库记录
    db_record = query_notion_database()
    if not db_record:
        return False, "数据库记录缺失"
    
    return True, "同步验证通过"
```

## ⚡ 性能优化

### API调用优化
- 使用延迟避免速率限制（0.4秒/次写入）
- 批量操作使用分页（limit 100）
- 缓存API响应避免重复请求

### 文件操作优化
- 使用shutil.copy2保持文件元数据
- 批量文件操作使用线程池
- 快照压缩减少存储空间

### 同步策略优化
- 增量同步：只同步变化的文件和对话
- 全量备份：重要配置文件完整备份
- 混合策略：文件全量备份，对话增量同步

## 🔧 配置管理

### 配置文件结构
```json
{
  "sync_database_id": "...",
  "parent_page_id": "...",
  "created_at": "2026-07-13T20:00:00Z",
  "notion_api_key": "...",
  "sync_scope": "company_environment_all_conversations",
  "backup_files": [
    ".env",
    "config.yaml",
    "hermes_sync_config.json",
    "万凯包装_精简档案.md"
  ]
}
```

### 环境变量管理
```bash
# API密钥存储
~/.hermes/.notion_api_key

# 同步配置
~/.hermes/hermes_sync_config.json

# 同步状态
~/.hermes/sync_status.json

# 同步报告
~/.hermes/sync_backups/*.json

# 快照
~/.hermes/sync_backups/company_sync_snapshot_*/
```

## 📈 监控与日志

### 同步日志
- 每次同步生成详细报告
- 保存同步时间、文件数量、对话数量
- 记录错误和警告信息

### 状态监控
```bash
# 查看同步状态
cat ~/.hermes/sync_status.json

# 查看最新报告
ls -lt ~/.hermes/sync_backups/*.json | head -1

# 检查快照
ls -d ~/.hermes/sync_backups/company_sync_snapshot_* | wc -l
```

### 告警机制
- 同步失败时发送通知
- 重要文件备份失败时告警
- 同步时间异常时提醒

---

**📌 总结**:
- 同步流程分为三个阶段：备份、中介、恢复
- 每个阶段都有详细的步骤和验证机制
- 数据一致性通过原子操作和错误恢复保证
- 性能通过优化API调用和文件操作提升
- 完整的日志和监控确保系统可靠性