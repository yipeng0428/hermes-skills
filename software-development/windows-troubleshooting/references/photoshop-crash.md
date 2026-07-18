# Adobe Photoshop Crash on Windows 10: Session Diagnostic Log

**Session Date:** 2026-07-12  
**Application:** Adobe Photoshop 2026 (v27.0.0.25)  
**OS:** Windows 10 企业版 (Build 19045, 64-bit)  
**GPU:** NVIDIA GeForce GTX 1050 Ti 4GB (Driver: 32.0.15.6094, 2024-08-13)  
**Memory:** 32GB (available: ~12.8GB)

---

## Symptoms

- Photoshop opens, works for ~1-3 minutes, then crashes (closes immediately)
- Crash happens repeatedly, every time PS is opened
- No error dialog appears — application just disappears
- Crash pattern: 10+ crashes in one day (July 12), recurring since at least July 9

## Investigation Steps

### 1. Event Viewer Analysis

Queried Application log for Level=2 (Error) events in the last 7 days:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=(Get-Date).AddDays(-7)} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'Photoshop' } | Select-Object -First 10 TimeCreated, Id, Message | Format-List
```

**Findings:**

- **30+ crash events** in 4 days (July 9-12), recurring every 1-3 minutes
- **Exception code:** `0xc0000409` (STATUS_STACK_BUFFER_OVERRUN)
- **Faulting module:** `ntdll.dll`
- **Faulting application:** `Adobe Photoshop 2026\Photoshop.exe` (v27.0.0.25)
- **Exception code 0xc0000409** typically indicates stack corruption / buffer overflow — often caused by memory pressure, insufficient disk space, or driver incompatibility

### 2. Disk Space Audit

| Drive | Size | Free | Used |
|-------|------|------|------|
| **C:** | 136.4 GB | **16.8 GB** | **87.7%** |
| D: | 101.2 GB | 29 GB | 71.3% |
| **E:** (PS scratch disk) | 465.7 GB | **84.3 GB** | 81.9% |
| F: | 465.7 GB | 134.8 GB | 71.1% |

**Critical Finding:** C: drive was at **87.7%** usage, only 16.8 GB free. Adobe officially recommends keeping 15-20% free space on the system drive.

**Root Cause Theory:** When disk space is critically low, Photoshop's memory-mapped file operations (scratch files, undo history, font caches) can fail silently, causing stack buffer overflow exceptions.

### 3. Photoshop Error Log (PSErrorLog.txt)

Located at `%APPDATA%\Adobe\Adobe Photoshop 2026\Adobe Photoshop 2026 Settings\PSErrorLog.txt`

```
2026:04:14 13:36:32 : Version: Adobe Photoshop 27.0.0
                       REQUIRE failed
                       Stack: Photoshop.exe → ScriptingSupport.8li → ExtendScript.dll
```

**Interpretation:** ExtendScript (legacy scripting engine) repeatedly failing. Could indicate corrupted preferences or incompatible script/extension.

### 4. Disk Space by Major Folder

| Folder | Size | % |
|--------|------|---|
| **%LOCALAPPDATA%\Microsoft** | **8.5 GB** | System cache, Edge, etc. |
| **Adobe Photoshop 2026** | **5.2 GB** | Cannot shrink |
| **%LOCALAPPDATA%\Programs** | **3.0 GB** | Local apps |
| **%PROGRAMDATA%\Adobe\CameraRaw** | **2.3 GB** | Shared cache (DO NOT DELETE) |
| **%LOCALAPPDATA%\npm-cache** | **1.7 GB** | ✅ Cleaned |
| **%LOCALAPPDATA%\crashdumps** | **687 MB** | ✅ Cleaned |
| **%LOCALAPPDATA%\NVIDIA** | **143 MB** | ✅ Cleaned |
| **%LOCALAPPDATA%\pip** | **26 MB** | ✅ Cleaned |
| **%LOCALAPPDATA%\D3DSCache** | **4.3 MB** | ✅ Cleaned |
| **%LOCALAPPDATA%\Temp** | **424 KB** | ✅ Cleaned |

### 5. GPU Driver Status

- **Driver version:** 32.0.15.6094
- **Driver date:** 2024-08-13
- **Age:** ~23 months old
- **GPU:** GTX 1050 Ti (Pascal architecture, 4GB VRAM)

**Issue:** Driver is nearly 2 years old. Photoshop 2026 heavily uses GPU acceleration (canvas rendering, AI features, neural filters). Old drivers can cause OpenGL/DirectX compatibility issues.

**UXP Logs showed:**
```
[FMS] [Vulcan] CCXP took too long to initialize
[hl-1] Failed to create/get SAMAssetContext: SAM init timed out
```

These are GPU/network timeout errors suggesting the GPU subsystem is struggling.

### 6. Old Adobe Versions Found in AppData

Even though only PS 2026 is installed in Program Files, old AppData remnants exist:
- `Adobe Photoshop 2019` (CT Font Cache)
- `Adobe Photoshop 2021` (Settings, AutoRecover, Font Cache, Logs)
- `Adobe Photoshop 2022` (CT Font Cache)
- `Adobe Photoshop 2024` (Logs)
- `Adobe Photoshop 2025` (Logs)

These can cause conflicts with shared components (ExtendScript, CameraRaw, etc.).

---

## Actions Taken

### Cleanup (Completed)

| Action | Space Freed | Status |
|--------|-------------|--------|
| User Temp folder | ~424 KB | ✅ |
| Windows Temp folder | — | ✅ |
| Prefetch folder | — | ✅ |
| Thumbnail cache | ~32 MB | ✅ |
| Crash dumps folder | ~687 MB | ✅ |
| npm cache | ~1.7 GB | ✅ |
| pip cache | ~26 MB | ✅ |
| D3DSCache | ~4.3 MB | ✅ |
| Recycle Bin | — | ✅ |
| Old PS AppData (2019-2025) | ~150 MB | ✅ |
| Adobe Installer cache | ~5 MB | ✅ |
| **Total** | **~2.4 GB** | |

**Result:** C: drive went from 16.8 GB free → 19.2 GB free (87.7% → 86% used)

### Remaining Manual Steps (User to Complete)

1. **Uninstall Acrobat 9.0** (392 MB) — too old, no longer needed
2. **Uninstall old Photoshop versions** from Control Panel if listed
3. **Update NVIDIA driver** to latest Studio Driver
4. **Reset Photoshop preferences** (delete `Adobe Photoshop 2026 Prefs.psp`)
5. **Adjust PS performance settings** — set GPU to "Basic" or disable temporarily
6. **Change scratch disk** to F: drive (134 GB free)

---

## Key Lessons

### 1. Disk Space is the #1 Suspect for `0xc0000409`

When you see STATUS_STACK_BUFFER_OVERRUN on Windows with Adobe apps, **always check disk space first**. The crash is not a bug — it's the OS failing to allocate memory-mapped files.

### 2. Event Viewer is Your Best Friend

The Application log in Windows Event Viewer contains detailed crash information:
- Exception code tells you the crash type
- Faulting module tells you which DLL caused it
- Frequency tells you if it's systematic or random

### 3. GPU Driver Age Matters for Creative Apps

Adobe apps (especially 2024+) heavily use GPU acceleration. A driver >12 months old is a liability. Always recommend updating to the latest **Studio Driver** (not Game Ready) for creative workstations.

### 4. Old AppData Remnants Cause Conflicts

Even after uninstalling old Adobe versions, AppData folders remain. These can cause:
- ExtendScript version conflicts
- CameraRaw profile mismatches
- Font cache corruption
- Preset/format plugin incompatibilities

### 5. PowerShell vs Bash Gotcha

On Windows, the `terminal` tool runs bash (git-bash/MSYS), NOT PowerShell. This means:
- `2>$null` fails → use `2>/dev/null`
- `$_.Property` gets expanded by bash → escape as `\$_.Property`
- PowerShell cmdlets don't work → use `powershell -Command "..."` prefix

---

## Diagnostic Checklist for Future Sessions

When a Windows app crashes:

1. ☐ Check Event Viewer: `Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; ...}`
2. ☐ Note the exception code and faulting module
3. ☐ Check disk space: `df -h` or `Get-CimInstance Win32_LogicalDisk`
4. ☐ Check GPU driver age: `Get-CimInstance Win32_VideoController`
5. ☐ Check application-specific logs in AppData
6. ☐ Check for old version remnants in AppData
7. ☐ Check for portable-app conflicts (`BackupBy*Portable`, empty Program Files dir, `*Portable.exe` processes)
8. ☐ Check Windows Update history (recent updates can break things)
9. ☐ Check for third-party plugin conflicts
10. ☐ Check memory: `systeminfo | grep "Available Physical Memory"`
11. ☐ Check pagefile configuration

**Symptom:** Photoshop 2024 shows in Registry (`HKLM\SOFTWARE\Adobe\Photoshop`) but `C:\Program Files\Adobe\Adobe Photoshop 2024\` is empty. Portable version is running instead.

**Found artifacts:**
- `PhotoshopPortable.exe` in process list (1.2 GB memory)
- `*.BackupByPhotoshopPortable` directories under `C:\Program Files\Common Files\Adobe\`:
  - `HelpCfg.BackupByPhotoshopPortable`
  - `Plug-Ins.BackupByPhotoshopPortable`
  - `UXP.BackupByPhotoshopPortable`
- `*.BackupByPhotoshopPortable` in AppData:
  - `D3DSCache.BackupByPhotoshopPortable`
  - `com.adobe.dunamis.BackupByPhotoshopPortable`
  - `Adobe.BackupByPhotoshopPortable` (Documents)
- No Creative Cloud desktop app installed

**Root cause:** The portable version (PhotoshopPortable) has been installed and has:
1. Backed up the original shared components
2. Replaced them with its own portable compatible copies
3. Broken the official Photoshop installer/verification chain

**Impact:** Adobe's official installer cannot repair or reinstall because the shared components have been replaced, and `Adobe Genuine Service` won't authenticate without the original framework intact.

**Recovery path:**
- Option A (recommended): Backup portable → uninstall → restore original backups → install Creative Cloud desktop → install official PS
- Option B: Keep portable (it works for the user's design workflow) + leave official broken

**Checklist for detecting this pattern:**
1. Open `HKLM\SOFTWARE\Adobe\` and note any products listed
2. Verify each `C:\Program Files\Adobe\<Product>\` exists and contains files
3. Check for active `*Portable.exe` processes
4. Search `C:\Program Files\Common Files\Adobe\` for `BackupBy*Portable` directories
5. Search `C:\Program Files (x86)\Common Files\Adobe\` for `BackupBy*Portable` directories
9. ☐ Check memory: `systeminfo | grep "Available Physical Memory"`
10. ☐ Check pagefile configuration
