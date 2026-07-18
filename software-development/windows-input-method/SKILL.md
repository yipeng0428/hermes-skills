---
name: windows-input-method
description: "Diagnose and fix Windows keyboard input method configuration — change default input method, reorder language priority, resolve shortcut malfunctions. Use when the user wants to set a specific IME (e.g. 微软五笔, 微软拼音,搜狗) as the default, fix 中英文切换 hotkeys, or reorder input language list on Windows 10/11."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, input-method, ime, keyboard, wubi, language, 五笔, 输入法]
    related_skills: [windows-troubleshooting]
---

# Windows Input Method Configuration

## Overview

Windows input method problems fall into three categories: (1) default IME is wrong (e.g. boots to English instead of 五笔), (2) language list order is wrong, (3) IME shortcuts don't behave. This skill covers diagnosis and repair for all three on Windows 10/11.

**Prerequisite awareness:** The `terminal` tool on Windows runs bash (git-bash/MSYS), NOT PowerShell. All commands below must be run as `powershell.exe -Command "..."` or via a `.ps1` file executed with `powershell.exe -File`. Direct PowerShell cmdlets do NOT work in the bare bash terminal.

## When to Use

- User wants a specific input method (微软五笔 / 微软拼音 / 第三方) as the default on boot
- Input method switches back to English unexpectedly
- 中英文切换 (Shift / Ctrl+Space) doesn't work as expected
- Language bar shows wrong order
- After Windows update, input method behavior changed

## Diagnosis

### 1. Identify current input methods and their CLSIDs

```powershell
$langs = Get-WinUserLanguageList
foreach ($l in $langs) {
    foreach ($im in $l.InputMethodTips) {
        Write-Host "$($l.LanguageTag) | $im"
    }
}
```

Key CLSIDs you'll see:

| Input Method | CLSID Pattern |
|---|---|
| 微软五笔 (Chinese Simplified) | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{82590C13-F4DD-44F4-BA1D-8667246FDF8E}` |
| 微软拼音 (Chinese Simplified) | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{70C97E25-34E1-4A5C-BC1E-9B73E03E142D}` |
| 美式键盘 (English US) | `0409:00000409` |

### 2. Check currently-set default

```powershell
$def = Get-WinDefaultInputMethodOverride
Write-Host "Default: $($def.InputMethodTip) ($($def.LanguageTag))"
```

### 3. Check registry preload order (determines boot default when no override)

```powershell
Get-ItemProperty "HKCU:\Keyboard Layout\Preload"
```

Output `1: 00000409` means English loads first — that's why the user boots into English.

## Fixes

### Fix A: Lock default input method (overrides everything)

```powershell
Set-WinDefaultInputMethodOverride -InputTip "<full-tip-with-CLSID>"
```

**PITFALL:** The parameter is `-InputTip`, NOT `-InputMethodTip`. `-InputMethodTip` produces a `ParameterBindingException`.

Example (force 微软五笔 as default):
```powershell
Set-WinDefaultInputMethodOverride -InputTip "0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{82590C13-F4DD-44F4-BA1D-8667246FDF8E}"
```

### Fix B: Reorder preload list (boot priority)

The registry `HKCU:\Keyboard Layout\Preload` uses numbered values.
- `1` = loads first = boot default
- `2` = loads second
- Each value is a keyboard layout hex code (`00000804` = Chinese, `00000409` = English US)

```powershell
$path = "HKCU:\Keyboard Layout\Preload"
Remove-ItemProperty -Path $path -Name "1" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $path -Name "2" -ErrorAction SilentlyContinue
New-ItemProperty -Path $path -Name "1" -Value "00000804" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $path -Name "2" -Value "00000409" -PropertyType String -Force | Out-Null
```

### Fix C: Reorder language list (affects language bar and Alt+Shift cycle)

```powershell
$list = Get-WinUserLanguageList
$zh = $list | Where-Object { $_.LanguageTag -eq "zh-Hans-CN" }
$en = $list | Where-Object { $_.LanguageTag -eq "en-US" }
$newList = New-Object System.Collections.Generic.List[Microsoft.InternationalSettings.Commands.WinUserLanguage]
$newList.Add($zh)
$newList.Add($en)
Set-WinUserLanguageList $newList -Force
```

### Fix D: When to apply all three together

When the user reports "default is English and I want 五笔" — apply Fix A + B + C together. Single fixes can be overridden by Windows language-switching logic; the triple approach is robust.

## Verification

```powershell
# Confirm default override
(Get-WinDefaultInputMethodOverride).InputMethodTip

# Confirm preload order
(Get-ItemProperty "HKCU:\Keyboard Layout\Preload").'1'

# Confirm language priority
(Get-WinUserLanguageList)[0].LanguageTag
```

All three should reflect 五笔 / 中文 as first.

## Important: Logoff/Restart Required

Registry preload and language list changes (Fix B, C) take full effect only after the user **logs off and back in** (or reboots). Tell the user explicitly. Fix A (override) often applies immediately but also benefits from a logoff.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `Set-WinDefaultInputMethodOverride: parameter not found` | Used `-InputMethodTip` instead of `-InputTip` | Use `-InputTip` |
| `powershell -Command "...$_..."` fails with "command not found" | bash expanding `$_` before PowerShell sees it | Write to `.ps1` file and run with `powershell.exe -File` |
| Changes don't stick after reboot | Only applied override, didn't fix Preload | Apply Fix A + B + C together |
| Chinese layout code is wrong | Used `00000409` thinking it's Chinese | Chinese = `00000804`, English = `00000409` |
| Wubi CLSID differs between machines | Wubi is an optional feature, CLSID can vary | Always read actual CLSID from `Get-WinUserLanguageList`, never hardcode from a guide |

## References

- `references/wubi-clsid.md` — Known 微软五笔 CLSID variants and how to verify
