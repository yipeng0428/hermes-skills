# Windows 磁盘扫描 — MSYS vs PowerShell

## 问题

在 MSYS (Git Bash) 环境下对 Windows 大目录执行 `du -sh` 极慢，经常超时：

```bash
# ❌ 不要这样做——会超时（>60s 甚至 >120s）
du -sh /c/Windows/
du -sh /c/Windows/WinSxS/
du -sh /c/Users/win10/AppData/Local/
```

原因：MSYS 的 `du` 对 NTFS 文件系统的 stat 调用效率远低于原生 Windows API。

## 正确做法

### 方法 1：PowerShell 脚本文件（推荐）

```bash
# 1. 写入 .ps1 文件
# 2. 用 -File 执行
powershell -ExecutionPolicy Bypass -File "C:\Users\win10\.hermes\tmp_disk_scan.ps1"
```

⚠️ **不要 inline PowerShell**：bash 会转义 `$_`、管道变量等，导致解析错误。

### 方法 2：快速检查关键位置

```bash
# 系统隐藏文件（通常几个 GB）
ls -lh /c/pagefile.sys /c/hiberfil.sys /c/swapfile.sys

# 小目录可以安全 du
du -sh /c/Users/win10/.hermes
du -sh /c/Users/win10/Downloads
du -sh /c/Users/win10/Desktop
```

### 方法 3：Windows 原生工具

让用户自己在 Windows 中运行：
- `cleanmgr` — 磁盘清理（含系统文件清理）
- 设置 → 系统 → 存储 → 临时文件

## 已知数据点（本机，2026-07）

| 位置 | 大小 | 说明 |
|------|------|------|
| C:\ 总计 | 137GB | |
| 已用 | ~125GB | |
| pagefile.sys | 4.8GB | 虚拟内存 |
| Windows/Installer | 2.2GB | MSI 缓存 |
| Program Files | 11.9GB | |
| Program Files (x86) | 10.4GB | |
| npm-cache | 597MB | 可清理 |
| Chrome Cache | 214MB | |
| WeChat Files | 554MB | |
| .hermes | 35MB | 正常 |
