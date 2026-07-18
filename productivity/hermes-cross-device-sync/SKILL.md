---
name: hermes-cross-device-sync
description: Configure and operate Hermes Agent's cross-device synchronization system for seamless work environment transitions between office and home computers using Notion as the data intermediary.
description_zh: 配置和操作Hermes Agent的跨设备同步系统，使用Notion作为数据中介，实现办公电脑和家里电脑之间的无缝工作环境切换
platforms: [windows, macos, linux]
prerequisites:
  env_vars: [NOTION_API_KEY]
  commands: [python3]
  files: [~/.hermes/.notion_api_key, ~/.hermes/hermes_sync_config.json]
related_skills:
  - notion-governance
  - hermes-config-providers
  - notion
---

# Hermes 跨设备同步系统

配置和操作Hermes Agent的跨设备同步系统，使用Notion作为数据中介，实现办公电脑和家里电脑之间的无缝工作环境切换。

## 🎯 核心能力

### 🔄 自动同步
- **公司电脑 → Notion**: 每天17:45自动备份所有对话、文件、状态
- **Notion → 家里电脑**: 每天18:30自动恢复所有数据
- **同步范围**: 公司环境中所有与Hermes的对话（而不仅仅是特定业务内容）

### 📁 备份策略
- **文件备份**: 配置文件、万凯档案、Hermes状态
- **对话同步**: 所有公司环境对话记录
- **状态备份**: Hermes当前状态、技能加载情况
- **快照创建**: 系统状态快照（用于恢复）
- **数据库记录**: 完整的同步历史记录

### 🔧 恢复策略
- **自动恢复**: 到家后自动从Notion获取最新数据
- **文件恢复**: 配置文件、工作文档
- **对话恢复**: 所有公司环境对话记录
- **状态恢复**: Hermes环境状态

## 🚀 快速开始

### 第一步：配置Notion API密钥

```bash
# 1. 获取Notion API密钥
# 访问 https://www.notion.so/my-integrations
# 创建新的Integration，复制API密钥

# 2. 保存API密钥
mkdir -p ~/.hermes
echo "ntn_your_api_key_here" > ~/.hermes/.notion_api_key

# 3. 设置环境变量
# 可选：在 ~/.bashrc 或 ~/.zshrc 中添加
# export NOTION_API_KEY="$(cat ~/.hermes/.notion_api_key)"
```

### 第二步：创建同步数据库

```bash
# 运行数据库创建脚本
python ~/.hermes/scripts/hermes-sync/create_sync_database.py

# 验证数据库创建
# 脚本会创建"🔄 Hermes 跨设备同步管理"数据库
# 并保存数据库ID到配置文件
```

### 第三步：验证配置

```bash
# 检查配置文件
cat ~/.hermes/hermes_sync_config.json

# 检查cron任务
hermes cron list

# 预期看到两个cron任务已创建
```

## 📋 使用场景

### 场景1：公司电脑下班前自动同步

**触发条件**: 每天17:45（周一至周六）

**执行步骤**:
1. ✅ 备份Hermes当前状态（配置、技能、提供商）
2. ✅ 备份工作上下文（环境变量、项目、任务）
3. ✅ 备份对话记录（所有公司环境对话）
4. ✅ 创建同步快照（系统状态备份）
5. ✅ 更新Notion数据库（记录同步历史）
6. ✅ 生成同步报告（保存到本地）

**输出示例**:
```
🚀 Hermes 跨设备同步 - 公司电脑下班前任务
📍 同步范围：公司环境中所有与Hermes的对话
📅 执行时间: 2026-07-13 17:45:00

🛠️ [步骤1/4] 备份Hermes当前状态
✅ Hermes状态备份完成: 4个配置文件

📋 [步骤2/4] 备份工作上下文
✅ 工作上下文备份完成

💬 [步骤3/4] 备份公司环境中所有对话记录
✅ 对话记录备份完成: 支持所有公司环境对话

📸 [步骤4/4] 创建同步快照
✅ 快照创建完成: company_sync_snapshot_20260713_174500

📊 [步骤5/5] 更新Notion同步数据库
✅ 同步记录已更新到Notion
  🎯 记录了所有公司环境对话的同步状态

📋 同步任务完成报告
📅 执行时间: 2026-07-13T17:45:00
🛠️ 状态备份: 4个配置文件
📋 工作上下文: 已备份当前工作环境
💬 对话备份: 支持所有公司环境对话
📊 数据库更新: ✅ 成功
💡 总计: 5个步骤完成
🎯 同步范围: 公司环境中所有对话

📝 详细报告已保存: ~/.hermes/sync_backups/company_sync_report_20260713_174500.json

🎉 同步任务执行成功！
```

### 场景2：家里电脑到家后自动恢复

**触发条件**: 每天18:30

**执行步骤**:
1. ✅ 从Notion同步Hermes状态（恢复配置、技能、提供商）
2. ✅ 从Notion同步工作上下文（恢复环境变量）
3. ✅ 从Notion同步对话记录（恢复所有对话）
4. ✅ 更新本地同步状态（记录恢复时间）
5. ✅ 生成恢复报告（保存到本地）

**输出示例**:
```
🏠 Hermes 跨设备同步 - 家里电脑同步任务
📍 同步范围：公司环境中所有与Hermes的对话
📅 执行时间: 2026-07-13 18:30:00

🛠️ [步骤1/3] 从Notion同步Hermes状态
✅ Hermes状态同步完成: 恢复了4个文件
   🎯 同步范围：公司环境中所有对话和配置

📋 [步骤2/3] 从Notion同步工作上下文
✅ 工作上下文同步完成

💬 [步骤3/3] 从Notion同步公司环境中所有对话记录
✅ 对话记录同步完成: 支持所有公司环境对话

📊 [步骤4/4] 更新本地同步状态
✅ 同步状态已更新

📋 同步任务完成报告
📅 执行时间: 2026-07-13T18:30:00
🛠️ Hermes状态: 恢复了4个文件
📋 工作上下文: 已同步当前工作环境
💬 对话记录: 支持所有公司环境对话
📊 同步状态: ✅ 完成
🎯 同步范围: 公司环境中所有对话

📝 详细报告已保存: ~/.hermes/sync_backups/sync_from_notion_report_20260713_183000.json

🎉 从Notion同步完成！

📝 现在你可以继续使用Hermes，所有公司电脑的对话内容都已同步到家里。
```

🛠️ [步骤1/3] 从Notion同步Hermes状态
✅ Hermes状态同步完成: 恢复了4个文件
   🎯 同步范围：公司环境中所有对话和配置

📋 [步骤2/3] 从Notion同步工作上下文
✅ 工作上下文同步完成

💬 [步骤3/3] 从Notion同步公司环境中所有对话记录
✅ 对话记录同步完成: 支持所有公司环境对话

📊 [步骤4/4] 更新本地同步状态
✅ 同步状态已更新

📋 同步任务完成报告
📅 执行时间: 2026-07-13T18:30:00
🛠️ Hermes状态: 恢复了4个文件
📋 工作上下文: 已同步当前工作环境
💬 对话记录: 支持所有公司环境对话
📊 同步状态: ✅ 完成
🎯 同步范围: 公司环境中所有对话

📝 详细报告已保存: ~/.hermes/sync_backups/sync_from_notion_report_20260713_183000.json

🎉 从Notion同步完成！

📝 现在你可以继续使用Hermes，所有公司电脑的对话内容都已同步到家里。
```

### 场景3：手动同步测试

```bash
# 测试公司电脑同步
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 测试家里电脑恢复
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py

# 只备份Hermes状态
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py --state-only

# 只同步对话记录
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py --conversations-only
```

## 📁 文件结构

```
~/.hermes/
├── .notion_api_key                    # Notion API密钥 (50字符格式)
├── hermes_sync_config.json            # 同步配置文件
├── scripts/
│   └── hermes-sync/
│       ├── sync_to_notion.py          # 公司电脑同步脚本 (15KB)
│       ├── sync_from_notion.py        # 家里电脑恢复脚本 (9.7KB)
│       ├── create_sync_database.py    # 数据库创建脚本
│       └── README.md                  # 完整用户手册
└── sync_backups/
    ├── company_sync_snapshot_20260713_174500/
    │   ├── .env
    │   ├── config.yaml
    │   ├── hermes_sync_config.json
    │   ├── 万凯包装_精简档案.md
    │   └── sync_info.json
    ├── company_sync_report_20260713_174500.json
    └── sync_from_notion_report_20260713_183000.json
```

## 🛠️ 配置文件格式

### hermes_sync_config.json
```json
{
  "sync_database_id": "company_sync_db_placeholder",
  "parent_page_id": "97eba701709c4d1c8c8a4f7a0e8a1b2c",
  "created_at": "2026-07-13T20:00:00Z",
  "notion_api_key": "ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "sync_scope": "company_environment_all_conversations"
}
```

## ⚙️ Cron任务配置

### 已创建的cron任务

```bash
# 公司电脑下班前同步 (周一至周六 17:45)
job_id: 0a54b41faab0
schedule: "45 17 * * 1-6"
deliver: "origin"

# 家里电脑到家后同步 (每天 18:30)
job_id: 7e961a09c8b1
schedule: "30 18 * * *"
deliver: "origin"
```

### 查看cron任务
```bash
# 列出所有cron任务
hermes cron list

# 查看特定任务详情
hermes cron list --job-id 0a54b41faab0
```

### 🔍 故障排除

### Discovering the Right Database ID

The canonical approach to find the live `data_source_id`:

1. `POST /v1/search` with `{"query": "兄弟消息板"}` — returns all databases with matching name
2. From results, pick the one with the full 8-property schema (发送者/消息类型/状态/优先级/发送时间/内容/关联页面/Name)
3. **Use the `data_source_id` (not `database_id`)** for `/data_sources/{id}/query`

### When Query Returns 404 on a Known Database ID

This happens when multiple duplicate databases exist. Check CANVAS page children:

```bash
# List all child databases under Hermes 数据中心
curl -s "https://api.notion.com/v1/blocks/39b86cdd-9a32-81bd-a252-c45cf86c4924/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2025-09-03"
# Then filter for blocks with "type": "child_database"
```

You'll likely find 4-5 databases all named "📬 兄弟消息板" — only one has the full schema. Archive the rest.

### 常见问题

**Q1: 同步任务没有执行？**
```bash
# 检查cron服务状态
systemctl status cron  # Linux
# 或确保Hermes桌面应用在运行

# Windows特殊情况：确保Hermes Agent在后台运行
# 检查任务管理器中的Hermes进程
```

**Q2: Notion API报错？**
```bash
# 测试API密钥
curl -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"
```

**Q3: 文件恢复失败？**
```bash
# 检查快照是否存在
ls -la ~/.hermes/sync_backups/company_sync_snapshot_*

# 检查恢复报告
cat ~/.hermes/sync_backups/restore_report_*.json
```

**Q4: Python脚本执行失败？**
```bash
# Windows特殊情况：使用绝对路径执行脚本
python "C:\Users\win10\.hermes\scripts\hermes-sync\sync_from_notion.py"

# 或者使用特定的Python版本
/c/Users/win10/.local/bin/python3.11.exe ~/.hermes/scripts/hermes-sync/sync_from_notion.py
```

**Q5: 同步报告显示0个文件？**
```bash
# 编辑脚本检查文件路径
nano ~/.hermes/scripts/hermes-sync/sync_to_notion.py

# 检查配置文件中的文件列表
cat ~/.hermes/hermes_sync_config.json

# 检查快照是否包含预期文件
ls -la ~/.hermes/sync_backups/company_sync_snapshot_*/
```

**Q6: Windows下Python脚本执行路径问题？**
```bash
# 使用绝对路径执行脚本
python "C:\Users\win10\.hermes\scripts\hermes-sync\sync_from_notion.py"

# 或者使用特定的Python解释器
/c/Users/win10/.local/bin/python3.11.exe ~/.hermes/scripts/hermes-sync/sync_from_notion.py

# 确保使用正确的路径格式（Windows风格）
python "C:\\Users\\win10\\.hermes\\scripts\\hermes-sync\\sync_from_notion.py"
```

## 📊 同步状态查看

### 查看同步历史
```bash
# 查看所有同步报告
ls -la ~/.hermes/sync_backups/company_sync_report_*.json
ls -la ~/.hermes/sync_backups/sync_from_notion_report_*.json

# 查看最新的同步报告内容
python -c "
import json
with open('~/.hermes/sync_backups/company_sync_report_latest.json') as f:
    data = json.load(f)
print(json.dumps(data, indent=2, ensure_ascii=False))
"

# 查看最新的快照
ls -la ~/.hermes/sync_backups/company_sync_snapshot_*/

# 查看同步状态
cat ~/.hermes/sync_status.json
```

### 检查同步状态
```bash
# 查看本地同步状态
cat ~/.hermes/sync_status.json

# 查看Notion同步数据库
# 使用Notion网页版或API查看
```

## 💡 最佳实践

### 1. 配置文件管理
- 将所有重要配置文件添加到备份列表
- 定期检查备份的文件是否完整
- 使用版本控制管理配置变更

### 2. 同步时间优化
- 公司电脑：17:45（下班前15分钟）
- 家里电脑：18:30（到家后30分钟）
- 避免在工作时间执行同步任务

### 3. 存储管理
- 定期清理旧的快照和报告
- 保留最近7天的同步数据
- 重要文件保留更长时间

### 4. 网络环境
- 确保网络连接稳定
- 公司网络：使用VPN确保访问
- 家里网络：确保Notion API可达

### 5. 权限管理
- 确保Integration有正确的权限
- 定期检查API密钥有效性
- 及时更新过期的密钥

## 🎯 技术细节

### 🎯 技术细节

### 同步策略
- **增量同步**: 只同步变化的文件和对话
- **全量备份**: 重要配置文件完整备份
- **混合策略**: 文件全量备份，对话增量同步

### 数据一致性
- **原子操作**: 每个同步步骤要么全部成功，要么全部回滚
- **状态跟踪**: 记录每个步骤的状态和结果
- **错误恢复**: 失败时提供备选方案
- **验证检查**: 同步后验证数据完整性

### 同步范围
- **公司电脑同步**: 所有对话、文件、状态
- **家里电脑恢复**: 所有对话、文件、状态
- **Notion数据库**: 完整的同步历史记录

## 📊 同步状态查看

### 查看同步历史
```bash
# 查看所有同步报告
ls -la ~/.hermes/sync_backups/company_sync_report_*.json
ls -la ~/.hermes/sync_backups/sync_from_notion_report_*.json

# 查看最新的同步报告内容
python -c "
import json
with open('~/.hermes/sync_backups/company_sync_report_latest.json') as f:
    data = json.load(f)
print(json.dumps(data, indent=2, ensure_ascii=False))
"

# 查看最新的快照
ls -la ~/.hermes/sync_backups/company_sync_snapshot_*/

# 查看同步状态
cat ~/.hermes/sync_status.json
```

### 检查同步状态
```bash
# 查看本地同步状态
cat ~/.hermes/sync_status.json

# 查看Notion同步数据库
# 使用Notion网页版或API查看
```

- **[notion-governance](notion-governance)**: Notion知识库治理系统
- **[hermes-config-providers](hermes-config-providers)**: Hermes配置管理
- **[notion](notion)**: Notion API操作

## 🤝 Hermes 兄弟协作系统 (v1.0)

在跨设备同步的基础上，进一步实现两个 Hermes 实例之间的**身份感知**和**消息互通**。两个 Hermes（🏢公司 + 🏠家里）通过共享的 Notion 消息板互相通报状态、留言、指派任务。与数据同步互补：同步系统传输文件/对话，兄弟系统传输意图/状态/任务。

详见: [references/hermes-brothers-collaboration.md](references/hermes-brothers-collaboration.md)

核心组件：
- 身份标识：`~/.hermes/hermes_identity.json`（每台电脑不同，包含自己和兄弟的身份信息）
- 消息板：Notion「📬 兄弟消息板」数据库（8 属性：发送者/类型/状态/优先级/时间/内容等）
- 脚本：`hermes_brothers_post.py`(发) / `hermes_brothers_check.py`(查)
- 签名约定：写入 Notion 末尾加 `📝 由 [🏢/🏠 Hermes·X] 记录 · 时间戳 CST`
- **每日签到**: 每天首次互动运行 check.py 检查兄弟消息，可选发送签到
- **身份启动验证（⚠️ 关键 protocol）**: 每次会话启动时必须执行以下 check，**不要盲信用户对身份的声明**：
  1. 读取 `~/.hermes/hermes_identity.json` 获取 `identity` 字段
  2. 执行 `hostname` + `pwd` 获取物理位置
  3. 比对两者是否一致
  4. **一致** → 继续，如用户说"你是另一台电脑的 Hermes"，告知用户实际配置是正确的
  5. **不一致** → 立即修正，感谢用户指出
  6. **绝不能**仅因用户声明就修改 `hermes_identity.json` — 必须客观验证（详见下方陷阱 2、5）
- 7 种消息类型 (👋📢💬📋🔄⚠️📝) + 4 级优先级 (🔥⚡📌💤)
- **工作上下文联动**: 聊工作时主动查 Notion「📋 每周事务」+ 桌面日期文件夹（如 717）
- **滞留判别**: LOGO 效果图 📝未定稿 = 正常等待客户，不标记为滞留
- **Watchdog 巡检**: `scripts/hermes_watchdog.py` 每 30 分钟 cron 静默巡检，有异常才通知。详见 [references/hermes-brothers-collaboration.md#watchdog-巡检模式](references/hermes-brothers-collaboration.md)
- **钉钉打卡自动化**: Win32 API 托盘恢复 + keybd_event 模拟按键，详见 [references/dingtalk-automation.md](references/dingtalk-automation.md)
- **重复数据库检测**: 启动时使用 `scripts/find_duplicate_databases.sh` 扫描 Hermes 数据中心页面下是否存在同名数据库，发现重复立即归档废弃副本

## ⚠️ 首次部署常见陷阱（2026-07-18 总结）

| # | 陷阱 | 症状 | 根因 | 修复 |
|---|------|------|------|------|
| 1 | 重复数据库 | `/data_sources/{id}/query` 返回 404 | 多次创建同名 DB + database_id ≠ data_source_id | 用 search 拿 data_source_id；归档废弃 DB |
| 2 | 身份文件配置错误 | 家里 Hermes 以 🏢 身份写入 Notion | 模板复制后未修改 `hermes_identity.json` | 立即验证 `identity=home` |
| 3 | database_id vs data_source_id | 404 `object_not_found` | 用了错误类型的 ID | 查/写数据 → data_source_id；创建页面 → database_id |
| 4 | Notion 集成未共享 | API 返回 404 或 403 | 数据库未与 Integration 共享 | Notion 页面 `... → Connect to → 选择 Integration` |
| 5 | **身份误认（本 session 教训）** | Hermes 以错误身份在 Notion 发消息、写入错误签名、覆盖完整版 SOUL.md | 用户说"你是家里的 Hermes"后未验证物理位置，直接信以为真 | **客观验证优先：先 `hostname` + 目录结构确认物理位置，再决定身份。绝不因用户声明而盲信** |
| 6 | **破坏性覆盖 SOUL.md** | 公司版 SOUL.md（含设计规范、产品知识、Cron 配置等 7600+ 字）被家里版（1800 字）完全覆盖，原始档案永久丢失 | 直接 `write_file` 整体覆盖而非使用 `patch` 增量编辑 | **永远不要整体覆盖 SOUL.md**。只能用 `patch` 修改特定段落，保留其他内容。如需重大变更，先备份：`cp ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak.YYYYMMDD` |
| 8 | **gh CLI 路径错误** | `gh: command not found` 但 gh 已安装 | Windows 上 gh 在 `C:\Program Files\GitHub CLI\gh.exe`，不在 PATH 里 | 用绝对路径 `& 'C:\Program Files\GitHub CLI\gh.exe'` 或先 `winget install GitHub.cli` |
| 9 | **PAT 权限不足** | `GitHub token lacks permission to fork repos` | PAT 缺少 `repo` scope 或 `workflow` scope | 重新生成 PAT 时勾选 `repo` 全部 + `workflow`，或改用 git clone + copy + push 方案 |
| 10 | **PowerShell 管道解析失败** | `An empty pipe element is not allowed` | `$token | & $gh` 在 PS 中解析异常 | 先写 token 到文件：`echo token > /tmp/txt`, 然后 `cat /tmp/txt | & $gh auth login --with-token` |

### 陷阱 5 详细过程（2026-07-18 真实事件）

**场景**: 用户在 company 电脑上，上一 turn 被告知"你是家里的 Hermes"后，直接执行了：
1. 把 `hermes_identity.json` 的 `identity` 从 `company` 改成 `home`
2. 用 `write_file` 整体覆盖 `SOUL.md`（公司版 7600 字 → 家里版 1800 字），原始档案永久丢失
3. 以🏢 select 身份在 Notion 发了"我是🏠 Hermes·家里"消息
4. 把公司 Hermes 之前的 3 条未读消息误标为已读

**用户纠正**: "等一下，不对。当下我是在公司的，所以，你才是公司电脑。现在请立刻全部盘查一下"

**正确 protocol**（新增）:
1. 收到身份声明时 → **不要立即修改文件**
2. 先执行 `hostname` + `whoami` + `pwd` 确认物理位置
3. 检查当前 `hermes_identity.json` 的 `identity` 是否与物理位置一致
4. 如一致 → 告知用户他的声明与实际不符，不修改
5. 如不一致 → 这才是真正的配置错误，立即修正并感谢用户指出

### 陷阱 6 详细过程（SOUL.md 破坏性覆盖）

SOUL.md 是 Hermes 的"灵魂档案"，包含大量不可再生的上下文：
- 工作联动规则（桌面日期文件夹协议）
- 设计规范（压盖机、淘宝主图尺寸）
- 产品知识（PET 瓶系列、认证列表）
- Cron 任务配置（15 个活跃任务）
- Watchdog 巡检配置

**恢复方法**: 如果 SOUL.md 被覆盖：
1. 从 Notion `🧬 SOUL.md` 页面恢复（公司 Hermes 上传过完整版本）
2. 用 `GET /v1/pages/{id}/markdown` 读取
3. 用 `write_file` 整体写回（这是少数可以用 write_file 的场景——从可信源恢复）
4. **绝不能用 `patch` 来恢复**——你不知道哪些段落被修改了，增量编辑无法修复整体覆盖

### 陷阱 7 详细过程（兄弟消息板冒名发帖）

**修复冒名消息**: 无法删除已发出的 Notion 页面（除非 archive），只能：
1. 发 ⚠️ 警告消息声明前一条作废
2. 在消息内容中明确指出：那条消息的身份标注是错误的
3. 确保后续所有消息使用正确身份 |

### 🔗 Skills 跨设备共享

当用户有多台 Hermes 实例（如公司 + 家里），需要在设备间同步 local skills 时，参考 **[references/github-skills-share.md](references/github-skills-share.md)** 中的方案。支持三种方式：GitHub 仓库同步（推荐，永久可用）、tar 打包拷贝（最快）、Skills Hub 发布（官方方式）。

关键注意：
- Windows 上 gh CLI 路径：`C:\Program Files\GitHub CLI\gh.exe`（不在 PATH）
- PAT 可能需要 `repo` + `workflow` scope 才能 publish
- 公司网络可能需要 VPN/代理才能访问 GitHub

## 🔗 支持文件

见 `references/` 目录中的详细文档：
- **[references/github-skills-share.md](references/github-skills-share.md)**: Skills 跨设备共享 — GitHub 仓库方案（解决公司/家里两台 Hermes 的 skill 同步问题）
- **[references/conversation-sync-technical.md](references/conversation-sync-technical.md)**: 会话历史同步技术实现 — state.db schema、export/import 脚本详解、FTS 索引维护、验证方法
- **[references/sync-workflow.md](references/sync-workflow.md)**: 同步工作流详解，包含三阶段流程图、详细步骤、数据一致性保证、性能优化等
- **[references/troubleshooting.md](references/troubleshooting.md)**: 故障排除指南，包含Notion API常见问题、速率限制处理、权限问题解决等
- **[references/hermes-brothers-collaboration.md](references/hermes-brothers-collaboration.md)**: 兄弟协作系统 — 身份验证、消息板、Watchdog 巡检
- **[references/dingtalk-automation.md](references/dingtalk-automation.md)**: 钉钉打卡自动化 — Win32 API 托盘恢复 + keybd_event 模拟按键
- **[templates/quick-start.md](templates/quick-start.md)**: 快速启动模板，包含使用前检查清单、快速配置命令、故障排除快速检查、常用操作等

### 🗄️ 会话历史同步脚本（v1.1 新增）

| 脚本 | 功能 |
|------|------|
| `scripts/hermes-sync/export_sessions.py` | 从 state.db 提取所有会话为 JSON（仅 user/assistant 消息，跳过工具调用） |
| `scripts/hermes-sync/import_sessions.py` | 将 JSON 导入到本地 state.db（跳过已存在会话，同步更新 FTS 索引） |
| `scripts/hermes-sync/sync_to_notion.py` | 更新版：下班前自动导出对话到快照（步骤3） |
| `scripts/hermes-sync/sync_from_notion.py` | 更新版：到家后自动从快照恢复对话（步骤2） |

**典型工作流**：
```bash
# 公司电脑 - 导出所有会话
python ~/.hermes/scripts/hermes-sync/export_sessions.py

# 将导出的 JSON 带回家（U盘/云盘/Notion附件）
# 文件位置：~/.hermes/sync_backups/sessions/sessions_export_YYYYMMDD_HHMMSS.json

# 家里电脑 - 导入会话
python ~/.hermes/scripts/hermes-sync/import_sessions.py \
  ~/.hermes/sync_backups/sessions/sessions_export_YYYYMMDD_HHMMSS.json
```

这些支持文件提供了详细的技术文档、故障排除指南和快速启动模板，帮助你更好地使用Hermes跨设备同步系统。

---

**🎉 系统已准备就绪！**

当前版本：v1.2.1
最后更新：2026-07-18

### 更新日志

- v1.2.3 (2026-07-18): 新增 Skills 跨设备共享方案 — GitHub 仓库同步（解决公司/家里两台 Hermes 的 skill 同步问题），含 gh CLI 在 Windows 的路径问题、PAT 权限配置、PowerShell 管道解析修复
- v1.2.2 (2026-07-18): 新增陷阱 5-7 — 身份误认客观验证 protocol、SOUL.md 破坏性覆盖防护、兄弟消息板冒名发帖修复
- v1.2.1 (2026-07-18): 首次部署陷阱总结（4 条常见错误）、身份文件配置错误修复指南、重复数据库清理记录
- v1.2.0 (2026-07-16): 兄弟协作系统完整部署 + SOUL.md 创建方法论 + 工作上下文联动规则 + Watchdog 巡检 + 钉钉打卡自动化 + 通知渠道（Windows Toast + 钉钉）
- v1.1.0 (2026-07-12): 会话历史同步（export_sessions.py / import_sessions.py）
- v1.0.0 (2026-07-10): 跨设备文件/对话/状态同步