# Skills 跨设备共享 — GitHub 仓库方案

## 问题

用户的 Hermes 在公司电脑（🏢 win10）和家里电脑（🏠）各运行一台实例。在公司创建的 local skills 如何迁移到家里？

## 方案对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **A. GitHub 仓库同步** | 永久可用、支持更新、可版本控制 | 需要 VPN/代理、首次配置稍复杂 | 长期方案、多设备频繁同步 |
| **B. 直接 tar 打包拷贝** | 5分钟搞定、零依赖 | 手动操作、无法增量更新 | 一次性迁移、无 VPN 环境 |
| **C. Skills Hub 发布** | 官方方式、可搜索安装 | 需要 `gh` + hub 账号、PAT 可能受限 | 公开分享、社区发布 |

## 方案 A 详解：GitHub 仓库同步

### 前置条件

- 公司电脑能访问 GitHub（办公室可能需要 VPN，代理端口 `127.0.0.1:10793`）
- 已安装 `gh` CLI（GitHub CLI）
- GitHub 账号（用户: `yipeng0428`）

### 步骤 1: 认证 gh CLI

Windows PowerShell 下 gh 路径：`C:\Program Files\GitHub CLI\gh.exe`

```powershell
powershell -Command "$token = 'github_pat_XXXX'; $gh = 'C:\Program Files\GitHub CLI\gh.exe'; $token | & $gh auth login --with-token; & $gh auth status"
```

**注意**：`execute_code` 不支持 subprocess，必须用 terminal + PowerShell 脚本文件。

### 步骤 2: 创建 GitHub 仓库

```powershell
powershell -Command "& 'C:\Program Files\GitHub CLI\gh.exe' repo create yipeng0428/hermes-skills --public --description 'Hermes Skills Repo'"
```

### 步骤 3: 尝试官方 publish（可能受限）

```bash
export GITHUB_TOKEN="github_pat_XXXX"
hermes skills publish /path/to/skill --to github --repo user/repo
```

**已知限制**: 某些 PAT 会报 `GitHub token lacks permission to fork repos`。

### 步骤 4: 替代方案 — git clone + copy + push

```bash
# Clone
git clone https://user:token@github.com/user/repo.git

# 复制所有 local skills
cp -r ~/.hermes/skills/skill-name repo/skills/

# Commit & push
cd repo
git add -A
git commit -m "Add skills: 90-30-deep-work, agentomics, ..."
git push origin main
```

### 步骤 5: 家里电脑安装

```bash
# 搜索
hermes skills search "hermes-skills"

# 安装
hermes skills install <skill-id>
```

或者直接从 GitHub 拉取：
```bash
git clone https://github.com/user/hermes-skills.git
cp -r hermes-skills/skills/* ~/.hermes/skills/
```

## 方案 B 详解：tar 打包（最快）

### 公司电脑
```bash
tar czf /tmp/hermes-skills-backup.tar.gz -C ~/.hermes/skills .
```

### 家里电脑
```bash
tar xzf /tmp/hermes-skills-backup.tar.gz -C ~/.hermes/skills
```

## Windows 下 gh CLI 的已知问题

1. **路径**: `C:\Program Files\GitHub CLI\gh.exe`（不是 `bin\gh.exe`）
2. **PowerShell 调用**: 必须用 `& "path"` 形式，单引号路径在某些 PS 版本下不行
3. **Token 传递**: 不能直接 `echo $token | gh`，PS 会报 "empty pipe element"。必须先存文件再用 `cat file | gh auth login --with-token`，或直接用 `$token | & $gh auth login --with-token`（但注意 PS 解析）
4. **执行策略**: 可能需要 `-ExecutionPolicy Bypass`

## 代理配置（公司网络）

如果公司网络不能直连 GitHub：

```bash
git config --global http.proxy http://127.0.0.1:10793
git config --global https.proxy http://127.0.0.1:10793
```

## 用户-specific 信息

- GitHub 用户名: `yipeng0428`
- PAT 已配置在公司电脑（`~/.hermes/.env` 或 gh auth）
- 办公室 VPN: 快柠檬，代理 `127.0.0.1:10793`

## 参考

- `hermes skills publish --help`
- `gh auth login --help`
- Hermes docs: Skills Hub & Publishing