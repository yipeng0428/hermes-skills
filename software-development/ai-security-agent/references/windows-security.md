# Windows Security Considerations for AI Agents

## Windows Defender coexistence

Windows Defender (Microsoft Defender Antivirus) is always running on Windows 10+. An AI security agent must coexist peacefully.

**Do NOT:**
- Attempt to disable Defender via registry/group policy
- Hook kernel APIs (ETW, minifilter) without proper signing
- Inject into other processes
- Use techniques that look like malware (process hollowing, APC injection)

**Do:**
- Run as a normal user-mode process
- Use documented APIs (psutil wraps WMI/Performance Counters)
- Register as a background service if running headless
- Add your agent to Defender exclusions if it triggers alerts

**If Defender flags your agent:**
1. Open Windows Security → Virus & threat protection → Manage settings
2. Add an exclusion for your project directory
3. Submit the file to Microsoft as false positive (optional)

## Windows-specific process quirks

### System processes that return None
- `System Idle Process` (pid 0) — no name, no exe, no user
- `System` (pid 4) — same
- `Registry` (pid ~148) — same
- `smss.exe`, `csrss.exe`, `wininit.exe` — access denied for many fields
- `Memory Compression` — no exe path
- `Secure System` — no fields available

**Always guard:** `(proc_info.get('name') or '').lower()`

### Processes with misleading names
- `cmd.exe` — could be git-bash, WSL, or scheduled tasks
- `powershell.exe` — could be Windows Update, Defender scans
- `wscript.exe` / `cscript.exe` — could be login scripts
- `dllhost.exe` — COM surrogate, usually legitimate
- `rundll32.exe` — could be legitimate or malicious
- `svchost.exe` — always legitimate, many instances

### Session 0 isolation
Services run in Session 0; user processes in Session 1+. Your agent runs in the user session and cannot directly interact with services (by design).

## Network connection monitoring

`psutil.net_connections()` returns:
- `status`: `ESTABLISHED`, `LISTEN`, `TIME_WAIT`, `CLOSE_WAIT`, etc.
- `laddr`: local address
- `raddr`: remote address (may be empty for listening sockets)
- `pid`: owning process (may be None for system sockets)

**Useful patterns:**
- Many `CLOSE_WAIT` → process not closing sockets properly (possible leak)
- Many `TIME_WAIT` → normal after HTTP requests
- Unknown process with many `ESTABLISHED` to foreign IPs → investigate
- Listening ports on unusual interfaces → possible backdoor

## Windows Firewall automation

The agent uses `netsh advfirewall` to block IPs. This requires:
- Administrator privileges (UAC prompt)
- Windows Firewall service running

**Command pattern:**
```powershell
netsh advfirewall firewall add rule name="APSA_Block_<ip>" dir=out action=block remoteip=<ip>
```

**To remove:**
```powershell
netsh advfirewall firewall delete rule name="APSA_Block_<ip>"
```

**Limitation:** If UAC is disabled or user is not admin, the command fails silently. Always check `result.returncode`.

## Windows Event Log (optional advanced)

For deeper visibility, read Windows Event Logs:
- `Microsoft-Windows-Sysmon/Operational` — if Sysmon installed
- `Security` — logon events, privilege escalation
- `System` — service crashes, driver failures
- `Application` — application crashes

Python access via `win32evtlog` (pywin32) or `wevtutil` CLI.

## Crash dump locations

- **Minidumps:** `C:\Windows\Minidump\` — small BSOD dumps
- **Full memory dump:** `C:\Windows\MEMORY.DMP` — complete RAM image
- **Application crash:** `%LOCALAPPDATA%\CrashDumps\` — per-app dumps

Check these if investigating system instability.

## Windows Update cache

`C:\Windows\SoftwareDistribution\Download\` — downloaded update files.
- Safe to delete after updates are installed
- Requires stopping `wuauserv` service first
- Windows will re-download if needed

## Task Scheduler integration

To run the agent at startup:
```powershell
schtasks /create /tn "APSA Security Agent" /tr "C:\path\to\python.exe C:\path\to\agent.py" /sc onstart /ru SYSTEM
```

Or use Task Scheduler GUI for more control.

## Permissions required

| Feature | Required privilege |
|---------|-------------------|
| Enumerate processes | Normal user |
| Terminate processes | Owner or admin |
| Read network connections | Normal user |
| Write to quarantine dir | Owner |
| Block IPs via firewall | Admin |
| Read event logs | Admin (for Security log) |
| Run as service | Admin (to install) |

## Antivirus false positive avoidance

Sign your executable if distributing. For local use, add exclusions.

Common AV triggers:
- Process termination APIs
- Firewall rule modification
- Reading other processes' memory
- Hooking keyboard/mouse (don't do this)
- Dropping files to startup folders

Stick to read-only monitoring + logging to minimize AV friction.
