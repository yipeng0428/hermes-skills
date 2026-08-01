# Auto-Heal 部署指南（家里电脑 🏠）

> 由 🏢 Hermes·公司 推送 · 2026-08-01
> 部署前请先阅读 skill: `hermes-system-diagnostics/auto-heal/SKILL.md`

## 背景

免费 API 报错导致会话中断后，本系统会自动切换到其它可用模型并**自动恢复未完成的工作**，
全程无需人工确认。公司电脑已上线并实测通过。

## 部署步骤（3 步）

### 1. 下载 auto_heal.py 到 scripts 目录

```bash
# 用 gh api（推荐，国内可达）或 git clone
mkdir -p "$HERMES_HOME/scripts" 2>/dev/null
# 方法A: gh api 下载
gh api repos/yipeng0428/hermes-skills/contents/scripts/auto_heal.py --jq '.content' | base64 -d > "$HERMES_HOME/scripts/auto_heal.py"
# 方法B: 如果 git 443 通
# curl -sL https://raw.githubusercontent.com/yipeng0428/hermes-skills/main/scripts/auto_heal.py -o "$HERMES_HOME/scripts/auto_heal.py"
```

### 2. 安装 skill

```bash
mkdir -p "$HERMES_HOME/skills/hermes-system-diagnostics/auto-heal"
gh api repos/yipeng0428/hermes-skills/contents/hermes-system-diagnostics/auto-heal/SKILL.md --jq '.content' | base64 -d > "$HERMES_HOME/skills/hermes-system-diagnostics/auto-heal/SKILL.md"
```

### 3. 验证 + 部署 cron

```bash
python "$HERMES_HOME/scripts/auto_heal.py" --status
# 看到 ✅ provider 列表即成功。然后用 cronjob 工具创建:
# schedule: */10 * * * * · no_agent=true · script=auto_heal.py · 名称「🩺 AI 中断自愈巡检」
```

## 重要：家里电脑的差异化配置

1. **HERMES_HOME 路径不同**：脚本硬编码了 `E:/hermes` 作为默认 HERMES_HOME，
   家里如果路径不同（如 `C:/Users/Administrator/AppData/Local/hermes/`），
   需要修改脚本开头的 `HERMES_HOME = Path(os.environ.get("HERMES_HOME", ...))`。
   **更简单**：部署前先 `export HERMES_HOME=你的路径`（脚本优先读环境变量）。
2. **provider 池不同**：家里的 custom_providers 列表可能不同，health check
   会自动按实际配置工作，无需改代码。
3. **死模型清理**：家里的 fallback 链如果有失效 provider，`--check` 会自动摘除。

## 验证方法

```bash
python "$HERMES_HOME/scripts/auto_heal.py" --status   # 各 provider 状态
python "$HERMES_HOME/scripts/auto_heal.py" --heal     # 全流程（无中断时静默）
```

模拟中断测试（可选）：
```python
# 往 state.db 插一条 finish_reason='error' 的会话，跑 --heal 看是否自动恢复
```

## 注意事项

- cron 用 `no_agent=true`，stdout 非空才会通知，正常时静默
- 修改脚本后 cron 无需重启
- 有问题在兄弟消息板找 🏢
