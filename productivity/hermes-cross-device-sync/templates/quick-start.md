# 🚀 快速启动模板

## 📋 使用前检查清单

### ✅ 环境准备
- [ ] Notion API密钥已获取
- [ ] API密钥已保存到 `~/.hermes/.notion_api_key`
- [ ] Python 3.11+ 已安装
- [ ] Hermes Agent 已安装

### ✅ 配置文件
- [ ] `~/.hermes/.notion_api_key` 存在且格式正确
- [ ] `~/.hermes/hermes_sync_config.json` 已创建
- [ ] 同步数据库已创建

### ✅ Cron任务
- [ ] 公司电脑同步任务已创建（17:45 周一至周六）
- [ ] 家里电脑恢复任务已创建（18:30 每天）

---

## 🔧 快速配置命令

### 1. 保存Notion API密钥
```bash
# 将你的Notion API密钥保存到文件
# 格式: ntn_开头，50个字符

echo "ntn_your_api_key_here" > ~/.hermes/.notion_api_key

# 设置环境变量（可选）
echo "export NOTION_API_KEY=\"$(cat ~/.hermes/.notion_api_key)\"" >> ~/.bashrc
source ~/.bashrc
```

### 2. 创建同步配置文件
```bash
# 创建同步配置文件
cat > ~/.hermes/hermes_sync_config.json << 'EOF'
{
  "sync_database_id": "company_sync_db_placeholder",
  "parent_page_id": "97eba701709c4d1c8c8a4f7a0e8a1b2c",
  "created_at": "2026-07-13T20:00:00Z",
  "notion_api_key": "$(cat ~/.hermes/.notion_api_key)",
  "sync_scope": "company_environment_all_conversations"
}
EOF
```

### 3. 创建同步数据库
```bash
# 运行数据库创建脚本
python ~/.hermes/scripts/hermes-sync/create_sync_database.py

# 更新数据库ID到配置文件
# 编辑 ~/.hermes/hermes_sync_config.json
# 将 sync_database_id 替换为实际创建的数据库ID
```

### 4. 验证配置
```bash
# 检查API密钥
echo "✅ API密钥: $(cat ~/.hermes/.notion_api_key | head -c 10)..."

# 检查配置文件
cat ~/.hermes/hermes_sync_config.json | python -m json.tool

# 测试API连接
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"
```

### 5. 手动测试同步
```bash
# 测试公司电脑同步
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 测试家里电脑恢复
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py

# 查看同步报告
ls -lt ~/.hermes/sync_backups/*.json | head -3
```

---

## 📝 手动同步命令

### 公司电脑同步
```bash
# 基础同步（备份所有内容）
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 只备份Hermes状态
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --state-only

# 只备份对话记录
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --conversations-only

# 只创建快照
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --snapshot-only

# 查看帮助
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --help
```

### 家里电脑恢复
```bash
# 基础恢复（恢复所有内容）
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py

# 只恢复Hermes状态
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py --state-only

# 只恢复对话记录
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py --conversations-only

# 查看帮助
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py --help
```

---

## 🔍 故障排除快速检查

### API密钥问题
```bash
# 检查密钥格式
cat ~/.hermes/.notion_api_key | wc -c
# 应该是51个字符（包括换行符）

# 测试API连接
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"
# 应该返回 200
```

### 文件备份问题
```bash
# 检查需要备份的文件
ls -la ~/.hermes/.env ~/.hermes/config.yaml ~/.hermes/hermes_sync_config.json

# 如果文件不存在，创建它们
# 或者编辑 sync_to_notion.py 添加缺失的文件
```

### Cron任务问题
```bash
# 查看cron任务
hermes cron list

# 手动运行测试
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 检查日志
ls -la ~/.hermes/sync_backups/*.json | tail -1
```

---

## 📊 监控命令

### 查看同步状态
```bash
# 查看本地同步状态
cat ~/.hermes/sync_status.json

# 查看最新同步报告
ls -lt ~/.hermes/sync_backups/*.json | head -1 | xargs cat | python -m json.tool

# 查看快照
ls -d ~/.hermes/sync_backups/company_sync_snapshot_* | sort -r | head -1

# 查看同步目录大小
# Windows
dir /s "%USERPROFILE%\.hermes\sync_backups"

# Linux/macOS
du -sh ~/.hermes/sync_backups
```

### 检查同步历史
```bash
# 列出所有同步报告
echo "=== 同步报告列表 ==="
ls -lh ~/.hermes/sync_backups/company_sync_report_*.json

# 列出所有快照
echo "=== 快照列表 ==="
ls -d ~/.hermes/sync_backups/company_sync_snapshot_*/

# 查看特定报告内容
echo "=== 报告详情 ==="
python -c "
import json
import sys
with open(sys.argv[1]) as f:
    data = json.load(f)
print(f'同步时间: {data[\"timestamp\"]}')
print(f'同步步骤: {len(data[\"steps\"])}')
for step in data['steps']:
    print(f'  - {step[\"step\"]}: {step[\"status\"]}')
" ~/.hermes/sync_backups/company_sync_report_20260713_*.json
```

---

## 🎯 常用操作

### 更新同步脚本
```bash
# 从Git仓库更新脚本
cd ~/.hermes/scripts/hermes-sync
git pull origin main

# 或者手动下载最新版本
```

### 清理旧数据
```bash
# 删除7天前的快照和报告
find ~/.hermes/sync_backups -name "company_sync_snapshot_*" -mtime +7 -exec rm -rf {} \;
find ~/.hermes/sync_backups -name "company_sync_report_*" -mtime +7 -exec rm -f {} \;
find ~/.hermes/sync_backups -name "sync_from_notion_report_*" -mtime +7 -exec rm -f {} \;
```

### 重置同步状态
```bash
# 删除同步状态文件
rm -f ~/.hermes/sync_status.json

# 重新运行同步
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py
```

---

## 📞 技术支持

### 遇到问题？
1. **检查故障排除文档** → `references/troubleshooting.md`
2. **查看同步工作流** → `references/sync-workflow.md`
3. **检查API连接** → 测试API密钥
4. **查看日志** → 检查同步报告

### 需要帮助？
```bash
# 查看技能文档
skill_view name=hermes-cross-device-sync

# 查看支持文件
ls ~/.hermes/skills/productivity/hermes-cross-device-sync/references/
```

---

## 🚀 下一步操作

### ✅ 已完成
- [x] Notion API密钥配置
- [x] 同步配置文件创建
- [x] 同步数据库创建
- [x] Cron任务设置
- [x] 手动测试通过

### 📅 等待自动同步
- [ ] 等待今天17:45的公司电脑同步
- [ ] 等待今天18:30的家里电脑恢复

### 🔧 可选优化
- [ ] 将同步数据库集成到Notion工作区
- [ ] 添加同步状态监控页面
- [ ] 配置同步状态通知
- [ ] 设置定期清理 cron 任务

---

**🎉 系统已配置完成！**

现在你可以：
1. 等待自动同步执行
2. 手动运行测试命令
3. 查看详细文档了解更多功能
4. 开始使用跨设备同步系统

**技能文档**: `skill_view name=hermes-cross-device-sync`

**支持文件**: `references/` 目录中的详细文档