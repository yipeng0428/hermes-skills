# 微软五笔 CLSID 参考表

微软五笔是 Windows 可选功能，在同版本 Windows 上 CLSID 基本一致，但不同大版本（如 Win10 21H2 vs 22H2 vs Win11）可能不同。

## 常见五笔输入法的 CLSID

| 输入法 | 语言标签 | InputMethodTip (CLSID) |
|---|---|---|
| 微软五笔 (简体中文) | `0804` | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{82590C13-F4DD-44F4-BA1D-8667246FDF8E}` |
| 微软拼音 (简体中文) | `0804` | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{70C97E25-34E1-4A5C-BC1E-9B73E03E142D}` |
| 微软双拼 | `0804` | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{FDE5A2B5-12C3-415B-830E-13FA45C6C971}` |
| 微软郑码 | `0804` | `0804:{6A498709-E00B-4C45-A018-8F9E4081AE40}{074929FE-1C69-4475-86D8-D7F0D8D0E4B5}` |
| 美式键盘 | `0409` | `0409:00000409` |
| 英文键盘 (其他) | `0409` | `0409:00000409` |

## 如何验证当前机器上的五笔 CLSID

```powershell
(Get-WinUserLanguageList | Where-Object { $_.LanguageTag -eq "zh-Hans-CN" }).InputMethodTips
```

输出后匹配已知 CLSID 中 "五笔" 形态特征：`{82590C13-...}` 是五笔；`{70C97E25-...}` 是拼音。

## 布局代码 (Preload 注册表用)

| 代码 | 含义 |
|---|---|
| `00000409` | 英文(美国)键盘 |
| `00000804` | 中文(简体)键盘 |
| `00000404` | 中文(繁体)键盘 |
| `00000412` | 韩文键盘 |

## 注册表路径

- `HKCU:\Keyboard Layout\Preload` — 预加载顺序（决定启动默认）
- `HKCU:\Keyboard Layout\Substitutes` — 替代字体（极少需修改）
- `HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts\` — 所有已安装布局的完整注册信息
