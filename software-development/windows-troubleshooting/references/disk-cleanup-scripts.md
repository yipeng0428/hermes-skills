# Windows Disk Cleanup Scripts (PowerShell)

Scripts used during the 2026-07-16 C-drive cleanup session. All run as `.ps1` files via `powershell -ExecutionPolicy Bypass -File`.

## Tiered Disk Scan

**Scan 1 — Root-level overview:**
```powershell
Get-ChildItem -Path C:\ -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum
    $gb = [math]::Round($size/1GB, 1)
    Write-Host ("  " + $gb.ToString().PadLeft(6) + " GB  " + $_.Name)
}
```

**Scan 2 — AppData subdirectories (the usual suspects):**
```powershell
# AppData/Local — usually 20-40 GB
Get-ChildItem -Path C:\Users\win10\AppData\Local -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum
    $gb = [math]::Round($size/1GB, 1)
    if ($gb -gt 0.1) { Write-Host ("  " + $gb.ToString().PadLeft(8) + " GB  " + $_.Name) }
}

# AppData/Roaming — usually 15-25 GB
Get-ChildItem -Path C:\Users\win10\AppData\Roaming -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum
    $gb = [math]::Round($size/1GB, 1)
    if ($gb -gt 0.1) { Write-Host ("  " + $gb.ToString().PadLeft(8) + " GB  " + $_.Name) }
}
```

## Batch Cleanup Script

Safe-to-delete targets with size reporting:

```powershell
$totalFreed = 0

function Free-Space($path, $name) {
    if (Test-Path $path) {
        $before = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum).Sum
        Write-Host "  Deleting $name ..." -NoNewline
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            $freed = [math]::Round($before/1MB, 0)
            $script:totalFreed += $freed
            Write-Host " OK — freed $freed MB"
        } catch {
            Write-Host " FAILED: $_"
        }
    } else {
        Write-Host "  SKIP: $name not found"
    }
}

# Known safe targets (confirmed 2026-07-16):
Free-Space "C:\Users\win10\AppData\Local\Tabbit" "Tabbit app"
Free-Space "C:\Users\win10\AppData\Roaming\TRAE SOLO CN" "TRAE IDE cache"
Free-Space "C:\Users\win10\AppData\Roaming\Trae CN" "Trae IDE cache"
Free-Space "C:\Users\win10\AppData\Local\Microsoft\WinGet\Packages" "WinGet cache"

# Temp files older than 7 days:
Get-ChildItem -Path "C:\Windows\Temp" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item -Force -ErrorAction SilentlyContinue

# User temp files older than 3 days:
Get-ChildItem -Path ([System.IO.Path]::GetTempPath()) -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } |
    Remove-Item -Force -ErrorAction SilentlyContinue

# npm cache (run in cmd, not PowerShell — npm may not be on PATH in PS):
# cmd /c "npm cache clean --force"

Write-Host "Total freed: $totalFreed MB"
$cDrive = Get-PSDrive C
$freeGB = [math]::Round($cDrive.Free/1GB, 1)
$pct = [math]::Round(($cDrive.Used/($cDrive.Used+$cDrive.Free))*100, 0)
Write-Host "C: now ${freeGB}GB free (${pct}% used)"
```

## 2026-07-16 Session Results

| Target | Freed | Notes |
|--------|-------|-------|
| Tabbit | 1,180 MB | ✅ |
| TRAE SOLO CN | 3,471 MB | ✅ Large, many small files — slow delete |
| Trae CN | 172 MB | ✅ |
| npm cache | — | ✅ `npm cache clean --force` |
| WinGet Packages | 711 MB | ✅ |
| Edge Cache | 0 MB | Already managed by browser |
| Windows Temp | — | ✅ 7-day cutoff |
| User Temp | — | ✅ 3-day cutoff |
| WeChat XPlugin | ❌ | Blocked — WeChat process holding `wmpf_host_export_x64.dll` |
| **Total** | **5,534 MB** | C: 91%→86%, 13GB→18.5GB free |

## Pitfalls

- **WeChat/XPlugin**: Cannot delete while WeChat is running. Close WeChat first.
- **MSYS `du` timeout**: `du -sh` on large Windows directories (>10GB) times out consistently. Always use PowerShell `Get-ChildItem` pattern above.
- **`$_` in inline PowerShell**: Never use inline `powershell -Command "..."` with `$_` or variable assignment in bash context — always use `.ps1` files.
- **npm in PowerShell**: `npm` may not be on PATH in PowerShell. Use `cmd /c "npm cache clean --force"` or run in bash terminal.
