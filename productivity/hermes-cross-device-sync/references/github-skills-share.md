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
- PAT 必须有 **`repo`** scope（否则 push 会报权限不足）

### 步骤 1: 认证 gh CLI

Windows PowerShell 下 gh 路径：`C:\\Program Files\\GitHub CLI\\gh.exe`

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

**已知限制**: 某些 PAT 会报 `GitHub token lacks permission to fork repos`。原因是官方 publish 需要先 fork 目标仓库，而 PAT 无 `repo` scope 时无法 fork。

### 步骤 4: 替代方案（推荐）— git clone + copy + push

这是目前最可靠的方式，避免了 publish 的 fork 限制：

```bash
# 配置代理（如果需要）
git config --global http.proxy http://127.0.0.1:10793
git config --global https.proxy http://127.0.0.1:10793

# Clone（URL 中嵌入 token 避免交互式认证）
git clone https://user:token@github.com/user/repo.git
cd repo

# 复制所有 local skills（保持目录结构）
for skill in skill1/skill-name skill2/skill-name; do
  src="$HOME/.hermes/skills/$skill"
  if [ -d "$src" ]; then
    mkdir -p "$(dirname "$skill")"
    cp -r "$src" "$skill"
  fi
done

# ⚠️ 推送前必须检查敏感信息（见下方"Push Protection"）

# 提交并推送
git add -A
git commit -m "Add local skills: description"
git push origin main
```

### 步骤 5: 家里电脑安装

```bash
# 方式 1: 直接从 GitHub 拉取后复制（最可靠）
git clone https://github.com/user/hermes-skills.git
cp -r hermes-skills/skills/* ~/.hermes/skills/

# 方式 2: 通过 Skills Hub（需要先 publish，可能受限）
hermes skills search "hermes-skills"
hermes skills install <skill-id>
```

---

## ⚠️ 关键陷阱与解决方案

### 陷阱 1: GitHub Push Protection 拦截

**症状**: `Push cannot contain secrets` / `GH013: Repository rule violations`

**原因**: GitHub secret scanning 自动检测提交中的 API keys、tokens。即使写在 SKILL.md 的示例代码或说明中也会被拦截。

**常见触发位置**:
- `vercel-ai-gateway.md` 中的 `vck_...` 示例 key
- `hermes-cross-device-sync/SKILL.md` 中的 `notion_api_key` 字段
- 其他 references 中引用的真实凭证（如 `ntn_...`、`sk-ag-...`）

**修复方法**:
1. 发布前扫描所有文件：`grep -r "vck_\|ntn_\|sk-ag-\|sk-" .`
2. 立即替换为占位符（不要等 push 失败才修）：
   ```bash
   # 批量替换示例
   find . -name "*.md" -exec sed -i 's/vck_[a-zA-Z0-9]\{40,\}/vck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g' {} \;
   find . -name "*.md" -exec sed -i 's/ntn_[a-zA-Z0-9]\{40,\}/ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g' {} \;
   ```
3. 把修改加入同一个 commit（或 amend 后 force push）
4. 验证：`git show --stat HEAD` 确认修改了敏感文件

**⚠️ Force push 注意**: 如果是已推送的 commit 被拦截，amend 后需要 `git push --force origin main`。确保家里电脑还没 pull，否则会造成分叉。

### 陷阱 2: gh API 通但 git push 443 不通

**症状**: `Failed to connect to github.com port 443` / `Connection was reset` / `Empty reply from server`

**原因**: 快柠檬等 VPN 的"智能模式"只代理浏览器流量，不代理 git HTTPS。gh API 走的是 HTTP/REST（可能被 API 网关代理），git push 走 HTTPS 443 直连被公司网络拦截。

**诊断方法**:
```bash
curl -s -o /dev/null -w "%{http_code}" https://api.github.com    # 200 = 通
curl -s -o /dev/null -w "%{http_code}" https://github.com        # 000 = 不通
curl -s --socks5 127.0.0.1:10793 https://api.github.com          # 测试 SOCKS5
curl -s --socks5 127.0.0.1:10793 https://github.com              # 测试 SOCKS5
```

**修复方法**（优先级从高到低）:
1. **✅ 首选（2026-08-01 实测）: 直接用 GitHub Contents API 推送/拉取文件** — `api.github.com` 在公司网络**直连可达**（无需代理！），完全绕开 443 拦截：
   ```bash
   # 推送/更新单个文件（存在则覆盖，无需 clone）
   gh api repos/<user>/<repo>/contents/<path> \
     -X PUT -f message="commit msg" \
     -f content="$(base64 -w 0 /local/file)" | python -c "import sys,json; print(json.load(sys.stdin)['content']['path'], 'OK')"
   # 下载文件（比 raw.githubusercontent.com 可靠，后者经快柠檬代理返回 HTTP 200 但 size=0）
   gh api repos/<user>/<repo>/contents/<path> --jq '.content' | base64 -d > /local/file
   ```
   ⚠️ 已知坑: `raw.githubusercontent.com` 经快柠檬代理返回 **HTTP 200 但 size=0**（`--noproxy '*'` 也一样）。**不要用它下载**，用 gh api 的 contents 接口（base64 解码）。
2. VPN 开**全局模式**（智能模式不够！）→ 重试 git push
3. 改用 SSH 推送（见下方备选方案）
4. 用 `git bundle` 离线传输（见下方备选方案）

**为什么 `git config http.proxy` 不够**: 某些代理（快柠檬）不是纯 HTTP 代理而是 SOCKS5，git config 的 `http.proxy` 只支持 HTTP/HTTPS 代理协议，不支持 SOCKS5。需要额外工具如 `proxychains` 或改用 SSH。

### 陷阱 3: bash/MSYS 环境下 git remote set-url 不生效

**症状**: 执行 `git remote set-url origin git@github.com:user/repo.git` 后，`git remote -v` 仍显示旧 URL

**原因**: MSYS bash 的 git 有时对 remote URL 的修改不写入 `.git/config`（可能是缓存或文件句柄问题）

**修复**: 直接用 `patch` 工具编辑 `.git/config`，把 `https://...` 改成 `git@github.com:...`：

```bash
# 用 patch 直接改 .git/config（不要依赖 git remote set-url）
# old_string: url = https://github.com/user/repo.git
# new_string: url = git@github.com:user/repo.git
```

同理，`git config --global http.proxy` 在 bash 中有时也不生效。如需设代理，建议在单个命令前加 `HTTP_PROXY=... HTTPS_PROXY=...`。

### 陷阱 4: git reset --soft HEAD~N 报 ambiguous argument

**症状**: `ambiguous argument 'HEAD~2': unknown revision or path not in the working tree`

**原因**: MSYS bash 把 `~` 当成 home 目录展开，`HEAD~2` 变成 `HEAD/home/user/2`

**修复**: 用 `--orphan` 方式创建全新 commit：
```bash
git checkout --orphan main-new
git add -A
git commit -m "New clean commit"
git branch -f main main-new
git checkout main
git branch -d main-new
```

或者直接用 hash：`git reset --soft <commit-hash>`（不含 `~` 语法）

### 陷阱 5: SSH 首次使用需要确认 host key

**症状**: `The authenticity of host 'github.com' can't be established`

**原因**: SSH 连接新服务器时需要确认 host key 指纹。

**修复**: 首次连接时输入 `yes` 确认，或预先添加：
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
```

---

## 备选方案

### 备选 1: SSH 推送（当 HTTPS 443 被拦截时）

```bash
# 1. 生成 SSH key
ssh-keygen -t ed25519 -C "yipeng0428@hermes" -f ~/.ssh/id_ed25519 -N ""

# 2. 把公钥添加到 GitHub: https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub

# 3. 修改 remote URL
git remote set-url origin git@github.com:user/repo.git

# 4. 预确认 host key
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null

# 5. 推送
git push origin main
```

**优点**: 不依赖 VPN 全局模式，SSH 端口 (22) 通常不被拦截
**缺点**: 需要手动配置 SSH key，每台设备都要添加公钥

### 备选 2: git bundle（完全离线）

```bash
# 公司电脑 - 打包整个 repo
git bundle create /tmp/hermes-skills.bundle --all

# 传输到家里（U盘/网盘）
# 家里电脑 - 解包
git clone /tmp/hermes-skills.bundle hermes-skills-repo
cd hermes-skills-repo
git remote set-url origin https://github.com/user/hermes-skills.git
# 有网络时再 push
```

**优点**: 完全不依赖网络
**缺点**: 手动操作，无法增量同步

---

## 方案 B 详解：tar 打包（最快，无网络依赖）

### 公司电脑
```bash
tar czf /tmp/hermes-skills-backup.tar.gz -C ~/.hermes/skills .
```

### 家里电脑
```bash
tar xzf /tmp/hermes-skills-backup.tar.gz -C ~/.hermes/skills
```

---

## Windows 下 gh CLI 的已知问题

1. **路径**: `C:\\Program Files\\GitHub CLI\\gh.exe`（不是 `bin\\gh.exe`）
2. **PowerShell 调用**: 必须用 `& "path"` 形式，单引号路径在某些 PS 版本下不行
3. **Token 传递**: 不能直接 `echo $token | gh`，PS 会报 "empty pipe element"。必须先存文件：
   ```powershell
   # 写 token 到临时文件（避免 PS 管道解析问题）
   $token | Out-File -FilePath C:\Users\win10\token_temp.txt -Encoding ASCII
   # 再用 cat | gh
   Get-Content C:\Users\win10\token_temp.txt | & $gh auth login --with-token
   ```
4. **执行策略**: 可能需要 `-ExecutionPolicy Bypass`
5. **winget 安装路径**: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\` — 不在系统 PATH，重启终端后才能用 `gh` 命令

---

## 代理配置（公司网络）

如果公司网络不能直连 GitHub：

```bash
# HTTP 代理（某些 VPN 支持）
git config --global http.proxy http://127.0.0.1:10793
git config --global https.proxy http://127.0.0.1:10793

# SOCKS5 代理（需要 proxychains 或类似工具）
# Linux: proxychains git push
# Windows: 没有原生 proxychains，建议用全局 VPN 或 SSH
```

**关键**: 如果 `curl --proxy http://127.0.0.1:10793 https://github.com` 返回 000，说明该代理不支持对 github.com 的 HTTPS 转发 → 必须全局模式。

---

## 用户-specific 信息

- GitHub 用户名: `yipeng0428`
- 仓库名: `yipeng0428/hermes-skills`
- PAT 已配置在公司电脑 gh auth 中
- 办公室 VPN: 快柠檬，代理 `127.0.0.1:10793`
- 37 个 local skills 已上传（2026-07-18）

---

## 参考

- `hermes skills publish --help`
- `gh auth login --help`
- Hermes docs: Skills Hub & Publishing
