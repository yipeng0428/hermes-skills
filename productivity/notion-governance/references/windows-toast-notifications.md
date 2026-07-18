# Windows 原生 Toast 通知

> 在 Windows 10/11 上从 Python 脚本发送桌面通知的可靠方法。用于 watchdog、cron job 等需要主动推送的场景。

## 方法：PowerShell + WinRT Toast API

无需安装任何第三方包，纯 PowerShell 调用 Windows 内置 API。

```python
import subprocess

def send_windows_toast(title: str, message: str) -> bool:
    """Send a native Windows 10/11 toast notification"""
    ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$texts = $template.GetElementsByTagName('text')
$texts.Item(0).AppendChild($template.CreateTextNode('{title}')) | Out-Null
$texts.Item(1).AppendChild($template.CreateTextNode('{message}')) | Out-Null
$toast = [Windows.UI.Notifications.ToastNotification]::new($template)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Hermes Agent').Show($toast)
'''
    try:
        subprocess.run(
            ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
            timeout=10, capture_output=True
        )
        return True
    except:
        return False
```

## 要求

- Windows 10 或 Windows 11
- PowerShell 5.0+
- 通知在系统通知中心显示，无需 Hermes 桌面应用在前台

## 验证

```bash
powershell -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$texts = $template.GetElementsByTagName('text')
$texts.Item(0).AppendChild($template.CreateTextNode('测试')) | Out-Null
$texts.Item(1).AppendChild($template.CreateTextNode('如果你看到这条消息，通知可用')) | Out-Null
$toast = [Windows.UI.Notifications.ToastNotification]::new($template)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Hermes Agent').Show($toast)
"
```

## 故障排除

- 如果通知不显示：检查 Windows 设置 → 系统 → 通知 → 确保"获取来自应用和其他发送者的通知"已开启
- 如果 PowerShell 报错关于 WinRT 类型：确认是 Windows 10 以上版本

## 生产使用

`~/.hermes/scripts/hermes_watchdog.py` 中已集成此方法。配合 cron job（`no_agent=True`，每30分钟），发现问题时同时通过 Windows 弹窗和 Hermes 应用内消息推送。
