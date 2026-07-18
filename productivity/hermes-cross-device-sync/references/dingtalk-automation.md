# 钉钉打卡自动化 — 方案汇总

> 适用场景：通过 Hermes cron 自动触发钉钉考勤打卡
> 创建：2026-07-16 · 验证：Windows 10 + DingTalk PC + 华为 Nova 10 (Android)

## 方案优先级

| 方案 | 可靠性 | 复杂度 | 说明 |
|------|--------|--------|------|
| 🥇 钉钉极速打卡 | ★★★★★ | 零配置 | 手机后台自动检测 WiFi/GPS，到点自动打 |
| 🥈 MacroDroid | ★★★★☆ | 低 | 手机端定时触发，模拟点击 |
| 🥉 Win32 API 托盘恢复 | ★★★☆☆ | 中 | PC 端脚本，需电脑不锁屏 |
| ❌ VBS AppActivate | ★☆☆☆☆ | 低 | 托盘缩小时找不到窗口，不可用 |

## 🥇 首选：钉钉极速打卡

钉钉内置功能，无需任何脚本。**这是应该是第一选择**。

### 配置
1. 钉钉 → 工作台 → 考勤打卡 → 右上角 ⚙️ → 极速打卡
2. 开启「上班极速打卡」和「下班极速打卡」
3. 确认时间范围覆盖目标时间（如 13:27）
4. 确保手机连接公司 WiFi（极速打卡依赖 WiFi/GPS 定位）

### 华为手机防杀后台
- 设置 → 应用 → 钉钉 → 耗电详情 → 「不允许电池优化」+「允许后台活动」
- 锁屏清理设为「不清理」

### 注意事项
- 不需要亮屏、不需要打开钉钉——后台全自动
- 如果一直没自动打过，99% 是系统杀了钉钉后台

## 🥈 备选：MacroDroid 手机端自动化

当极速打卡不可用时使用。华为应用市场搜索 MacroDroid（免费）。

触发器：每周一至六 13:27
动作：启动钉钉 → 等待 5 秒 → UI 交互 → 点击「打卡」

## 🥉 PC Win32 API 托盘恢复技术

仅当手机方案都不可行时才考虑。**PC 端打卡可能被公司限制**——钉钉 PC 端搜索栏（Ctrl+K）不一定有打卡入口，取决于公司配置。

### 核心技术问题

Windows 应用缩到系统托盘后，VBScript 的 `AppActivate` 无法找到隐藏窗口。需要先用 Win32 API 恢复窗口再操作。

### 步骤 1：枚举所有窗口（含隐藏）

```python
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

def enum_windows_by_title(keyword):
    windows = []
    def callback(hwnd, lParam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if keyword in buf.value:
                visible = user32.IsWindowVisible(hwnd)
                windows.append((hwnd, buf.value, visible))
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return windows
```

### 步骤 2：恢复隐藏窗口

```python
SW_RESTORE = 9
def restore_window(hwnd):
    user32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(1)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)
```

### 步骤 3：发送按键

```python
# Ctrl+K 打开搜索（注意：PC 钉钉可能不支持此快捷键）
user32.keybd_event(0x11, 0, 0, 0)  # Ctrl down
user32.keybd_event(0x4B, 0, 0, 0)  # K down
user32.keybd_event(0x4B, 0, 2, 0)  # K up
user32.keybd_event(0x11, 0, 2, 0)  # Ctrl up
```

### Pitfall 记录

| Pitfall | 表现 | 原因 | 解决 |
|---------|------|------|------|
| 托盘窗口不可激活 | VBS `AppActivate("钉钉")` 返回 False | 窗口被隐藏（ShowWindow SW_HIDE），不在可见窗口列表中 | 用 Win32 `EnumWindows` 枚举所有窗口（含隐藏），`ShowWindow(SW_RESTORE)` 恢复 |
| Ctrl+K 无反应 | 按键发出但钉钉无响应 | PC 钉钉不一定支持全局搜索快捷键，或该功能被公司禁用 | 检查手动是否可用；否则转 MacroDroid 手机方案 |
| keybd_event 中文失败 | 输入框里打出乱码或英文 | `keybd_event` 发送虚拟键码，中文需 IME 上下文 | 改用 VBS `SendKeys` 输入中文（但需窗口已激活） |
| 锁屏时全方案失效 | 脚本运行但窗口无法操作 | 锁屏状态下 `SetForegroundWindow` 和 `keybd_event` 均被阻止 | 午休时电脑不锁屏，或使用手机端方案 |
| PC 端被限制打卡 | 窗口恢复成功但找不到打卡入口 | 公司可能仅开放手机端打卡 | ✅ 转用钉钉极速打卡 |

## Cron 配置

```yaml
schedule: "27 13 * * 1-6"   # 周一至六 13:27
no_agent: true               # 纯脚本，无需 LLM
deliver: origin              # 结果发回对话
script: dingtalk_checkin.py
```

## 通用托盘恢复模式

此技术可用于任何需要从托盘恢复窗口的 Windows 桌面自动化：

| 应用 | 窗口标题 | 恢复方法 |
|------|---------|---------|
| 钉钉 | "钉钉" | ShowWindow(SW_RESTORE) |
| 微信 | "微信" | ShowWindow(SW_RESTORE) |
| QQ | "QQ" | ShowWindow(SW_RESTORE) |

---

📝 由 [🏢 Hermes·公司] 记录 · 2026-07-16
