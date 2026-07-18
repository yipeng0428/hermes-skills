---
name: windows-troubleshooting
description: "Diagnose and fix Windows application crashes, freezes, and unexpected closures. Covers Event Viewer analysis, disk space investigation, GPU driver checks, OpenCL/CUDA runtime component diagnosis, application log parsing, and safe cleanup procedures. Use when an application on Windows crashes, hangs, or behaves unexpectedly, or when GPU compute features (OpenCL/CUDA) are missing from an otherwise-up-to-date driver."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, troubleshooting, debugging, crash, freeze, application]
    related_skills: [systematic-debugging]
---

# Windows Troubleshooting

## Overview

Windows application crashes follow predictable patterns. This skill provides a systematic approach to diagnosing and fixing them, combining Windows-specific tools with general debugging principles.

**Pair with:** `systematic-debugging` for the 4-phase debugging framework. This skill adds Windows-specific investigation techniques.

## When to Use

- Application crashes or freezes on Windows
- Application won't start
- Unexpected behavior after Windows updates
- Performance degradation
- Blue screen / system instability

## Investigation Flow

### 1. Gather Crash Evidence

Use Event Viewer via PowerShell to find crash events:

```powershell
# Find crash events for a specific application (last 7 days)
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=(Get-Date).AddDays(-7)} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'ApplicationName' } | Select-Object -First 10 TimeCreated, Id, Message | Format-List
```

**Key fields to extract:**
- `Faulting application name` — the executable
- `Faulting module name` — the DLL where crash occurred
- `Exception code` — crash type (see table below)
- `Fault offset` — memory address

### Common Exception Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| `0xc0000005` | Access Violation | Null pointer, corrupted memory, driver bug |
| `0xc0000409` | STATUS_STACK_BUFFER_OVERRUN | Stack corruption, buffer overflow, disk space exhaustion |
| `0xc000001d` | Illegal Instruction | CPU incompatibility, corrupted binary |
| `0xc000007b` | STATUS_INVALID_IMAGE | 32/64-bit mismatch, corrupted DLL |
| `0xc0000135` | STATUS_DLL_NOT_FOUND | Missing runtime library |
| `0xc0000142` | STATUS_DLL_INIT_FAILED | DLL initialization failure |
| `0xe0434352` | CLR Exception | .NET runtime error |

### 2. Check System Resources

**Disk Space (CRITICAL for Adobe apps):**
```bash
df -h
# or
powershell -Command "Get-CimInstance Win32_LogicalDisk -Filter \"DriveType=3\" | Select-Object DeviceID, @{N='Free(GB)';E={[math]::Round(\$_.FreeSpace/1GB,1)}}, @{N='UsedPct';E={[math]::Round((\$_.Size-\$_.FreeSpace)/\$_.Size*100,1)}}"
```

Adobe recommends at least 15-20GB free on the system drive. If >85% full, this is likely the root cause.

**Memory:**
```bash
systeminfo | grep "Available Physical Memory"
```

**GPU Driver:**
```bash
powershell -Command "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate | Format-List"
```

If driver is >12 months old, update it. For creative apps, use NVIDIA Studio Driver.

### 3. Check Application Logs

Many applications write their own logs:
- `%APPDATA%\Vendor\Product\Logs\`
- `%LOCALAPPDATA%\Vendor\Product\Logs\`
- `%PROGRAMDATA%\Vendor\Product\Logs\`

### 4. Identify Disk Space Hogs

Common large folders to clean:
- `%TEMP%` — user temp files
- `C:\Windows\Temp` — system temp files
- `C:\Windows\SoftwareDistribution\Download` — Windows Update cache (admin required)
- `%LOCALAPPDATA%\crashdumps` — crash dumps
- `%LOCALAPPDATA%\npm-cache` — npm cache
- `%LOCALAPPDATA%\pip` — pip cache
- `%LOCALAPPDATA%\D3DSCache` — D3D shader cache
- `%LOCALAPPDATA%\NVIDIA` — NVIDIA shader cache
- `%LOCALAPPDATA%\Microsoft\Windows\Explorer` — thumbnail cache

**Safe to clean:** Temp folders, crash dumps, npm/pip caches, D3D cache, thumbnails, Recycle Bin

**Do NOT clean:** CameraRaw cache (used by Photoshop/Lightroom), Windows system files, Program Files

### 5. Application-Specific Cleanup

Old application versions often leave remnants in AppData even after uninstalling. Check:
```
%APPDATA%\Vendor\Product YYYY\
%LOCALAPPDATA%\Vendor\Product YYYY\
```

For Adobe Photoshop, old versions (2019, 2021, 2022, 2024, 2025) can be safely removed from AppData if you only use the latest version.

### 6. Reset Preferences

Corrupted preferences can cause crashes. To reset:
1. Close the application
2. Rename or delete the preferences file in the Settings folder
3. Restart the application (it will recreate defaults)

## PowerShell vs Bash Terminal Gotcha

On Windows, the `terminal` tool runs commands through **bash (git-bash/MSYS)**, NOT PowerShell. This causes issues:

1. **Redirection:** `2>$null` (PowerShell) fails in bash. Use `2>/dev/null` instead.
2. **Variable syntax:** `$var` (PowerShell) vs `$var` (bash) — same but escaping differs.
3. **Cmdlets:** `Get-CimInstance`, `Get-ChildItem`, etc. are NOT available in bash.
4. **WMI:** `wmic` works but is deprecated.

### CRITICAL: Inline PowerShell eats `$_` and variables — always use .ps1 files

**Bash expands PowerShell's automatic variables to empty strings.** `$_`, `$sz`, `$_.Name`, `$_.FullName`, and similar pipeline variables are silently consumed by bash before PowerShell sees them. `\$` escaping works for trivial one-liners but breaks on anything with variable assignment, nested loops, or `Measure-Object` pipelines. Errors appear as cryptic parse errors: `Missing expression after unary operator '+'`, `Unexpected token '}'`, or `The hash literal was incomplete`.

**Rule: for any PowerShell longer than a single pipeline, write to a .ps1 file first, then execute.**

```bash
# ❌ FAILS silently — $_ and $sz eaten by bash:
powershell -Command "Get-ChildItem C:\Users | ForEach-Object { $sz = $_.Length }"

# ✅ WORKS reliably:
write_file(path='~/tmp_scan.ps1', content='...full script...')
terminal('powershell -ExecutionPolicy Bypass -File "C:\\Users\\...\\tmp_scan.ps1"')
```

**Safe single-line pattern (truly trivial only):**
```bash
powershell -Command 'Get-Process | Where-Object { $_.Name -eq "app" }'
# Single quotes prevent bash expansion. Breaks if script needs internal double-quotes.
```

### Disk Space Analysis Pattern (via .ps1)

MSYS `du -sh` on large Windows directories times out (120s+). Use PowerShell `Get-ChildItem -Recurse | Measure-Object` in a `.ps1` file:

```powershell
# Scan C:\ root directory sizes:
Get-ChildItem -Path C:\ -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum
    $gb = [math]::Round($size/1GB, 1)
    if ($gb -gt 0.1) { Write-Host ("  " + $gb.ToString().PadLeft(6) + " GB  " + $_.Name) }
}
```

Common cleanup targets and their typical paths:
| Directory | Typical Size | Safe to Delete? |
|-----------|-------------|-----------------|
| `%LOCALAPPDATA%\Tabbit` | 1-2 GB | ✅ If unused |
| `%APPDATA%\TRAE SOLO CN` | 3-5 GB | ✅ IDE cache |
| `%APPDATA%\Tencent\xwechat` | 2-3 GB | ⚠️ WeChat data, close app first |
| `%LOCALAPPDATA%\npm-cache` | 0.5-1 GB | ✅ `npm cache clean --force` |
| `%LOCALAPPDATA%\Microsoft\WinGet\Packages` | 0.5-1 GB | ✅ Installer cache |
| `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache` | 0.5-1 GB | ✅ Browser cache |
| `C:\Windows\Temp` | varies | ✅ Files older than 7 days |
| `%TEMP%` | varies | ✅ Files older than 3 days |

**Cleanup script template:** see `references/disk-cleanup-scripts.md`.

## Quick Diagnostic Checklist

When an application crashes on Windows:

- [ ] Check Event Viewer for crash details (exception code, faulting module)
- [ ] Check disk space (must be >15% free, ideally >20GB)
- [ ] Check available memory
- [ ] Check GPU driver age (>12 months = update)
- [ ] Check application-specific logs
- [ ] Check for old version remnants in AppData
### 7. OpenCL / CUDA Runtime Diagnosis

When an application or game needs OpenCL (or CUDA runtime components) and fails despite an up-to-date NVIDIA driver, the driver package may be missing its runtime components. This is common after partial or upgrade installs.

**Symptoms:**
- App error: `"OpenCL.dll not found"`, `"No OpenCL platforms"`, `"OpenCL call failed"`
- App launches but GPU compute features are grayed-out
- `System32\OpenCL.dll` exists (Microsoft ICD loader) but registry keys are missing — see below

**OpenCL Diagnosis:**

The Microsoft ICD loader in `C:\Windows\System32\OpenCL.dll` is just a dispatcher — it needs to find NVIDIA's ICD driver via the registry.

Check the registry for NVIDIA's OpenCL ICD:
```bash
reg query "HKLM\SOFTWARE\Khronos\OpenCL\Vendors"
# 32-bit apps on 64-bit Windows:
reg query "HKLM\SOFTWARE\Wow6432Node\Khronos\OpenCL\Vendors"
```

If these keys are **missing**, the driver's OpenCL ICD was not installed. The NVIDIA driver file `nvopencl.dll` should be present in:
```bash
ls /c/Windows/System32/nvopencl.dll
ls /c/Windows/SysWOW64/nvopencl.dll        # 32-bit apps
```

**CUDA Runtime Diagnosis:**

CUDA runtime components live in `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vX.X\`. If `nvcc` is missing or a CUDA-using app fails, the toolkit isn't installed.

```bash
# Check for CUDA toolkit
find /c/Program\ Files -maxdepth 3 -name "nvcc.exe" 2>/dev/null
# Or simpler:
find /c/Program\ Files/NVIDIA\ GPU\ Computing\ Toolkit -maxdepth 1 -type d 2>/dev/null
```

**Fix:**

1. **Clean install the NVIDIA driver** — download from https://www.nvidia.cn/Download/index.aspx
   - Run installer → **Custom (Advanced)** → ☑ **Perform clean installation**
   - Do NOT skip "other components" during install
   - Reboot after install completes
2. **Verify fix** — check registry keys and `nvopencl.dll` existence as shown above
3. For CUDA runtime, install the CUDA Toolkit separately from https://developer.nvidia.com/cuda-toolkit

**Note:** `clinfo` (OpenCL Info) is an optional third-party tool not included with NVIDIA drivers. Install it separately (e.g., via `winget`, conda, or from https://github.com/Oblomov/clinfo) if you need to enumerate OpenCL devices.

---

### 8. Check for Portable-App Conflicts

When a commercial app (Adobe, Office, etc.) shows as "installed" in registry but its Program Files directory is empty, check for portable versions:

**Signs of portable-over-installer conflict:**
- `HKLM\SOFTWARE\Vendor\Product` exists but `C:\Program Files\Vendor\Product\` is empty
- Running process is `ProductPortable.exe` instead of `Product.exe`
- `*.BackupBy*Portable` directories in `C:\Program Files\Common Files\Vendor\`
- No Creative Cloud / main client app installed

**Cause:** Portable apps often back up and replace shared components (like Adobe's `Adobe Desktop Common`, `CEP`, `UXP`) with their own modified versions, breaking the official installer's dependency chain.

**Fix:** Uninstall portable → restore from `*.BackupByPortable` if available → reinstall official.
- [ ] Check Windows Update history (recent updates can break things)

## References

- `references/photoshop-crash.md` — Session-specific detail from a real Photoshop crash investigation (exception code analysis, disk space correlation, GPU driver age, cleanup results)
- `references/opencl-runtime-gap.md` — Session-specific detail for diagnosing OpenCL/CUDA runtime components missing from NVIDIA drivers (registry checks, nvopencl.dll, clean install fix)
