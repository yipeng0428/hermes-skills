# 主动工作滞留监控 (Proactive Work Monitoring)

> 对 Notion「📋 每周事务」数据库的自动化巡检模式——无需用户提醒，主动发现积压工作并提出解决方案。

## 触发条件

当用户聊到工作相关话题时（或 Hermes 自行判断需要了解当前工作状态时），自动执行查询。

## 滞留判定标准（区分谁在等待）

⚠️ **关键区分：谁在等谁？** 只有用户需要行动但未行动才算滞留。客户端的等待是正常业务流程。

| 状态 | 场景 | 判定 |
|------|------|------|
| 📝 未定稿 + 🖌️客户LOGO | 客户自行确认中，公司默认流程 | ✅ **正常等待** — 不盯、不催、不标记为滞留 |
| 📝 未定稿 + 其他类别 | 用户自己的草稿未定稿 | 🟡 超过3天需关注 |
| 🔄 进行中 | 任何类别 | 🔴 ≥3天无更新需关注 |
| 📅 计划 | 任何类别 | 🟡 ≥5天未启动需关注 |
| ⏳ 待跟进 | 任何类别 | 🟡 被外部阻塞，跟进即可 |

## 桌面文件夹联动

用户习惯在桌面以日期数字命名当天工作文件夹（如"717"代表7月17日）。聊工作时同步检查桌面是否有当天或近期的日期文件夹。命名变体：717、0717、7.17。

## 查询命令

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/139e8c07-a5f0-4537-87f7-73c4ba691f67/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 50, "sorts": [{"property": "日期", "direction": "descending"}]}'
```

## 分析输出模板

扫描完成后，按以下格式呈现：

```
## 🚨 滞留项（需要关注）
🔴 未定稿 X天 | YYYY-MM-DD | [类别] 任务标题
   客户: xxx

## 🟡 进行中（正常范围内）
   YYYY-MM-DD [状态] [类别] 任务标题

## 🧠 分析
[模式识别：是否某类任务集中积压？是否有共性阻塞原因？]
[建议：基于模式的具体行动建议]
```

## 常见模式与应对

| 模式 | 症状 | 行动 |
|------|------|------|
| **LOGO 效果图等待** | 多个 📝未定稿 的 🖌️客户LOGO | ✅ **不做任何事** — 客户自己决定时间线，这是公司默认流程。不催、不盯、不建议主动联系 |
| **审核链卡住** | 🔄进行中 且客户指向同一审核人（如"给蔡总审核"）超过3天 | 建议用户主动 push 审核人，或先截图部分成果降低审核门槛 |
| **自己遗忘的草稿** | 非LOGO类 📝未定稿 超过3天 | 提醒用户有未完成的草稿，询问是否需要继续或取消 |
| **长期计划未启动** | 📅计划 超过5天 | 询问是否还需要做，或调整优先级

## 原则

- **主动，不被动** — 不等用户说"帮我看看"，自发扫描
- **区分谁在等** — 📝未定稿+客户LOGO=正常等待，不盯不催。只有用户需行动但未行动才算滞留
- **可行动，不只描述** — 不只说"有X条滞留"，要给出具体建议
- **连接工作要点库** — 发现的问题与规范相关时自动引用（如"客户效果图必须发印刷群"）

## 自动化实现

Watchdog 脚本 `~/.hermes/scripts/hermes_watchdog.py` 实现了每30分钟自动巡检：
- 桌面异常（散落图片、大文件、残留下载）
- C盘空间（<15GB或>85%使用率）
- Notion API 连通性
- 跨设备同步状态
- 每周事务滞留任务（遵循上述判定标准）

通过 `no_agent=True` cron job 运行，平时静默，发现问题时通过三重通道推送：
1. 🖥️ **Windows 原生 Toast** — PowerShell 调用 WinRT `Windows.UI.Notifications` API
2. 📱 **钉钉机器人 Webhook** — POST markdown 消息到公司专用群（不跟家里混）
3. 💬 **Hermes 应用内** — cron deliver→origin 消息留存

### Watchdog Cron 生命周期陷阱

**`resume` 对过期的 one-shot job 无效。** 如果 Watchdog 被禁用（`enabled=false`）且 one-shot 时间已过，`resume` 会返回错误：`"Cannot resume: one-shot time is in the past and will never fire"`。**必须 `remove` + `create` 重建。**

**正确创建命令：**
```
schedule: "every 30m"  ← 循环模式，不是 "once in 30m"
no_agent: true
script: "hermes_watchdog.py"
```

### 钉钉打卡自动化

用户需要周一至六 13:27 自动午休打卡。使用 VBScript/COM 模拟按键方案（不需要额外 pip 包）：

```python
# ~/.hermes/scripts/dingtalk_checkin.py
vbs_script = '''
Set WshShell = CreateObject("WScript.Shell")
WshShell.AppActivate "钉钉"
WScript.Sleep 800
WshShell.SendKeys "^k"        ' 打开搜索
WScript.Sleep 500
WshShell.SendKeys "打卡"      ' 搜索打卡
WScript.Sleep 600
WshShell.SendKeys "{ENTER}"   ' 触发
'''
subprocess.run(['cscript', '//Nologo', '//B'], input=vbs_script.encode())
```

⚠️ **前置条件**：电脑不休眠/不锁屏、钉钉保持登录。若公司要求锁屏则不适用，需改用手机端方案。

Cron: `schedule="27 13 * * 1-6"`, `no_agent=True`, `script="dingtalk_checkin.py"`

## 与治理系统的关系

- Notion Governance OS 关注**知识库质量**（标题乱码、重复页面等）
- 工作滞留监控关注**工作流健康度**（任务是否卡住、是否需要干预）
- 两者互补：前者是数据卫生，后者是业务节奏
