# Notion API 常见问题与解决方案

## 🔍 API错误代码

### 401 Unauthorized - API密钥无效
**错误信息**: `{"object":"error","status":401,"code":"unauthorized","message":"API key token is invalid."}`

**解决方案**:
```bash
# 1. 检查API密钥格式
cat ~/.hermes/.notion_api_key

# 2. 确认密钥完整性（应该是50个字符）
# 格式: ntn_开头，后面跟随一长串字符

# 3. 重新获取API密钥
# 访问 https://www.notion.so/my-integrations
# 创建新的Integration，复制新密钥

# 4. 更新密钥文件
echo "ntn_new_api_key_here" > ~/.hermes/.notion_api_key

# 5. 测试API连接
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"
```

### 403 Forbidden - 权限不足
**错误信息**: `{"object":"error","status":403,"code":"forbidden","message":"Notion API key cannot access the requested resource."}`

**解决方案**:
```bash
# 1. 检查Integration是否添加到工作区
# 访问 https://www.notion.so/my-integrations
# 确保你的Integration在"Integrations"列表中

# 2. 检查页面共享权限
# 打开Notion页面 → 点击"Share" → 确保你的Integration在"Invite a person"列表中

# 3. 重新共享页面
# 点击页面右上角"Share" → 添加你的Integration

# 4. 验证权限
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/databases"
```

### 404 Not Found - 资源不存在
**错误信息**: `{"object":"error","status":404,"code":"object_not_found","message":"Could not find the requested resource."}`

**解决方案**:
```bash
# 1. 检查数据库ID是否正确
cat ~/.hermes/hermes_sync_config.json | grep sync_database_id

# 2. 如果数据库不存在，重新创建
python ~/.hermes/scripts/hermes-sync/create_sync_database.py

# 3. 更新配置文件中的数据库ID
# 编辑 ~/.hermes/hermes_sync_config.json
# 替换 sync_database_id 为新创建的数据库ID

# 4. 验证数据库存在
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/databases/{sync_database_id}"
```

## ⚡ 速率限制问题

### API限流 (429 Too Many Requests)
**错误信息**: `{"object":"error","status":429,"code":"rate_limited","message":"API rate limit exceeded."}`

**解决方案**:
```bash
# 1. 检查API调用频率
# Hermes同步系统默认设置了延迟：
# - Dashboard写入: 0.4秒延迟 (~2.5 req/s)
# - Fixer操作: 0.6秒延迟 (~1.7 req/s)

# 2. 如果需要手动操作，添加延迟
sleep 1

# 3. 批量操作时使用分页
# 例如：dashboard.py --limit 100 --offset 0
# 然后 --offset 100, --offset 200 等

# 4. 监控API使用情况
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/limits"
```

## 🔄 同步脚本常见问题

### 脚本执行失败 (Python错误)
**错误**: `ModuleNotFoundError: No module named 'requests'`

**解决方案**:
```bash
# 1. 安装依赖
pip install requests

# 2. 或者使用系统Python
which python3
python3 --version

# 3. 确保Python环境正确
# 如果使用虚拟环境，激活它
source venv/bin/activate  # 或 .\venv\Scripts\activate
```

### 文件路径错误 (Windows路径问题)
**错误**: `FileNotFoundError: [Errno 2] No such file or directory`

**解决方案**:
```bash
# 1. 使用绝对路径
# 确保所有路径都是绝对路径，特别是在Windows上

# 2. 检查路径格式
# Windows: C:\Users\win10\.hermes\sync_backups
# Linux/macOS: /c/Users/win10/.hermes/sync_backups

# 3. 使用os.path.expanduser处理~路径
import os
path = os.path.expanduser("~/.hermes/sync_backups")
```

### 同步报告显示0个文件
**问题**: 同步报告显示备份了0个文件

**解决方案**:
```bash
# 1. 检查需要备份的文件列表
cat ~/.hermes/scripts/hermes-sync/sync_to_notion.py | grep "config_files"

# 2. 验证文件是否存在
ls -la ~/.hermes/.env
ls -la ~/.hermes/config.yaml

# 3. 添加缺失的文件到备份列表
# 编辑 sync_to_notion.py 文件
# 在 config_files 列表中添加缺失的文件

# 4. 重新运行同步
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py
```

## 📊 Notion数据库操作问题

### 创建数据库失败
**错误**: 数据库创建脚本执行失败

**解决方案**:
```bash
# 1. 检查父页面ID是否正确
cat ~/.hermes/hermes_sync_config.json | grep parent_page_id

# 2. 确保父页面存在
# 父页面应该是你的Notion工作区中的一个页面

# 3. 重新创建数据库
python ~/.hermes/scripts/hermes-sync/create_sync_database.py

# 4. 手动创建数据库
# 如果脚本失败，可以在Notion中手动创建数据库
# 然后将ID填入配置文件
```

### 数据库属性更新失败
**问题**: 更新数据库属性时出现错误

**解决方案**:
```bash
# 1. 检查属性名称是否正确
# Notion API对属性名称非常严格

# 2. 使用正确的属性类型
# select, multi_select, title, rich_text, number, date, checkbox

# 3. 更新属性时包含所有选项
# 当更新select/multi_select时，必须包含所有现有选项
# 不能只包含新选项，否则会删除旧选项

# 4. 示例：正确的PATCH请求
curl -X PATCH "https://api.notion.com/v1/databases/{database_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "properties": {
      "状态": {
        "select": {
          "options": [
            {"name": "✅ 已完成", "color": "green"},
            {"name": "🔄 进行中", "color": "yellow"},
            {"name": "⏳ 待处理", "color": "gray"}
          ]
        }
      }
    }
  }'
```

## 🔧 网络与代理问题

### 公司网络阻止Notion API访问
**问题**: 在公司网络中Notion API无法访问

**解决方案**:
```bash
# 1. 检查网络连接
ping api.notion.com

# 2. 使用VPN
# 确保VPN连接正常

# 3. 检查代理设置
# 如果需要代理，设置环境变量
# export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 4. 测试API连接
curl -v -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"
```

### DNS解析失败
**问题**: DNS无法解析api.notion.com

**解决方案**:
```bash
# 1. 更改DNS服务器
# 使用Google DNS或Cloudflare DNS

# Windows:
netsh interface ip set dns "以太网" static 8.8.8.8

# macOS/Linux:
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4

# 2. 清除DNS缓存
# Windows:
ipconfig /flushdns

# macOS:
sudo dscacheutil -flushcache

# Linux:
sudo systemd-resolve --flush-caches

# 3. 测试DNS解析
dig api.notion.com
nslookup api.notion.com
```

## 📝 配置文件问题

### 配置文件格式错误
**错误**: JSON解析失败

**解决方案**:
```bash
# 1. 验证JSON格式
python -m json.tool ~/.hermes/hermes_sync_config.json

# 2. 修复格式错误
# 使用在线JSON验证工具
# 或者手动编辑文件

# 3. 示例正确格式
{
  "sync_database_id": "...",
  "parent_page_id": "...",
  "created_at": "2026-07-13T20:00:00Z",
  "notion_api_key": "...",
  "sync_scope": "company_environment_all_conversations"
}
```

### 环境变量未设置
**问题**: NOTION_API_KEY环境变量未设置

**解决方案**:
```bash
# 1. 设置环境变量
# 临时设置
export NOTION_API_KEY="$(cat ~/.hermes/.notion_api_key)"

# 持久设置（添加到shell配置文件）
echo "export NOTION_API_KEY=\"$(cat ~/.hermes/.notion_api_key)\"" >> ~/.bashrc
echo "export NOTION_API_KEY=\"$(cat ~/.hermes/.notion_api_key)\"" >> ~/.zshrc

# 2. 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc

# 3. 验证环境变量
printenv | grep NOTION_API_KEY
```

## 🔄 同步状态问题

### 同步状态显示失败
**问题**: sync_status.json显示同步失败

**解决方案**:
```bash
# 1. 检查详细错误信息
cat ~/.hermes/sync_backups/sync_report_*.json | python -m json.tool

# 2. 查看最新的同步报告
ls -lt ~/.hermes/sync_backups/*.json | head -1 | xargs cat

# 3. 手动重试同步
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 4. 检查Notion数据库中的记录
# 打开Notion中的同步管理数据库
# 查看是否有错误记录
```

### 快照丢失
**问题**: 创建了快照但找不到了

**解决方案**:
```bash
# 1. 检查快照目录
ls -la ~/.hermes/sync_backups/

# 2. 查找最新快照
ls -d ~/.hermes/sync_backups/company_sync_snapshot_* | sort -r | head -1

# 3. 如果快照不存在，检查脚本执行日志
# 脚本应该在 ~/.hermes/sync_backups/ 目录中创建快照

# 4. 重新创建快照
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --snapshot-only
```

---

**📌 总结**:
- 401错误 → 检查API密钥
- 403错误 → 检查权限和页面共享
- 404错误 → 检查数据库ID
- 429错误 → 添加延迟或分页
- 路径错误 → 使用绝对路径
- 网络问题 → 检查VPN和代理

当遇到问题时，首先检查错误代码和错误信息，然后按照对应的解决方案逐步排查。