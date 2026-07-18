#!/usr/bin/env python3
"""
Hermes Watchdog — Proactive desktop & system monitor.
Runs silently via cron (no_agent=True). Only outputs when something needs attention.
Notifies via: Windows Toast + DingTalk webhook + stdout (cron delivery).
"""
import os, sys, json, time, urllib.request, subprocess
from datetime import datetime

ALERTS = []

# ── Notification helpers ──────────────────────────────────────────

def send_windows_toast(title, message):
    """Native Windows 10/11 toast notification via PowerShell WinRT API"""
    ps = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$t.GetElementsByTagName('text').Item(0).AppendChild($t.CreateTextNode('{title}')) | Out-Null
$t.GetElementsByTagName('text').Item(1).AppendChild($t.CreateTextNode('{message}')) | Out-Null
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Hermes Agent').Show([Windows.UI.Notifications.ToastNotification]::new($t))
'''
    try:
        subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', ps], timeout=10, capture_output=True)
        return True
    except:
        return False


def send_dingtalk(title, details):
    """Send to company DingTalk bot webhook"""
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=1702d8dca47489f0f308976315760f4ce2e5ed909127e6f5b63398daa9d7fcd2"
    md = f"### {title}\n\n{details}\n\n---\n> 🏢 Hermes·公司 Watchdog · {datetime.now().strftime('%m/%d %H:%M')}"
    payload = {"msgtype": "markdown", "markdown": {"title": title, "text": md}}
    try:
        req = urllib.request.Request(webhook, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

# ── Checks ────────────────────────────────────────────────────────

def check_desktop():
    desktop = os.path.expanduser("~/Desktop")
    try: items = os.listdir(desktop)
    except: return

    pngs = [f for f in items if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('.')]
    if len(pngs) > 10:
        ALERTS.append(f"🖼️ 桌面有 {len(pngs)} 张散落图片，建议归档或清理")

    for f in items:
        fp = os.path.join(desktop, f)
        if os.path.isfile(fp):
            sz = os.path.getsize(fp) / (1024 * 1024)
            if sz > 100:
                ALERTS.append(f"📦 桌面有大文件: {f} ({sz:.0f}MB)")

    week_ago = time.time() - 7 * 86400
    old = [f for f in items if os.path.isfile(os.path.join(desktop, f))
           and os.path.getmtime(os.path.join(desktop, f)) < week_ago
           and os.path.splitext(f)[1].lower() in ('.tmp', '.crdownload', '.partial', '.download')]
    if old:
        ALERTS.append(f"🗑️ 桌面有 {len(old)} 个残留下载文件，建议清理")


def check_disk():
    try:
        import shutil
        u = shutil.disk_usage("C:\\")
        free = u.free / (1024**3)
        pct = (u.used / u.total) * 100
        if pct > 90:
            ALERTS.append(f"💾 C盘仅剩 {free:.1f}GB ({pct:.0f}%已用)，建议清理")
        elif pct > 85:
            ALERTS.append(f"💾 C盘空间紧张: {free:.1f}GB 可用 ({pct:.0f}%已用)")
    except: pass


def check_notion():
    cf = os.path.expanduser("~/.hermes/.notion_last_error")
    if os.path.exists(cf):
        with open(cf) as f:
            c = f.read().strip()
        if c:
            ALERTS.append(f"🔌 Notion API 上次报错: {c[:80]}")


def check_stalled():
    """Only flag user-actionable stalls (not customer-waiting LOGO效果图)"""
    key = os.environ.get('NOTION_API_KEY', '')
    if not key: return
    try:
        DS = "139e8c07-a5f0-4537-87f7-73c4ba691f67"
        H = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
        q = {"page_size": 30, "sorts": [{"property": "日期", "direction": "descending"}],
             "filter": {"or": [{"property":"状态","select":{"equals":"🔄 进行中"}},
                                {"property":"状态","select":{"equals":"📅 计划"}}]}}
        req = urllib.request.Request(f"https://api.notion.com/v1/data_sources/{DS}/query",
                                     data=json.dumps(q).encode(), method="POST", headers=H)
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        today = datetime.now()
        for p in data.get("results", []):
            props = p.get("properties", {})
            st = (((props.get("状态") or {}).get("select") or {}).get("name") or "")
            ds = (props.get("日期") or {}).get("date") or {}
            ds = ds.get("start", "") if ds else ""
            title = "".join(t.get("text",{}).get("content","") for t in (props.get("Name") or {}).get("title", []))
            try: days = (today - datetime.strptime(ds, "%Y-%m-%d")).days
            except: continue
            if st == "🔄 进行中" and days > 3:
                ALERTS.append(f"⏰ 滞留: [{st}] {title[:40]} — {days}天")
            elif st == "📅 计划" and days > 5:
                ALERTS.append(f"⏰ 未启动: [{st}] {title[:40]} — {days}天")
    except Exception as e:
        with open(os.path.expanduser("~/.hermes/.notion_last_error"), 'w') as f:
            f.write(str(e)[:100])


def main():
    check_desktop()
    check_disk()
    check_notion()
    check_stalled()

    if not ALERTS:
        return  # SILENT

    ts = datetime.now().strftime('%H:%M')
    summary = f"🔔 Hermes Watchdog · {ts}"
    details = "\n".join(f"  {a}" for a in ALERTS)
    print(summary); print(); print(details); print()

    send_windows_toast("🔔 Hermes Watchdog", ALERTS[0][:150] if len(ALERTS) == 1
                       else f"🔔 Hermes Watchdog ({len(ALERTS)}项)")
    if len(ALERTS) > 1:
        send_windows_toast(f"🔔 Hermes Watchdog ({len(ALERTS)}项)", ALERTS[0][:150])
    send_dingtalk(summary, details)


if __name__ == "__main__":
    main()
