# GitHub Releases Binary Download Troubleshooting

## Overview

When downloading binary files from GitHub Releases (`.exe`, `.deb`, `.rpm`, `.dmg`, `.apk`, etc.), users often encounter connection timeouts, incomplete downloads, or "Exec format error" issues. This is common when:

- Behind corporate firewalls or GFW (Great Firewall of China)
- Using certain VPN/proxy configurations
- GitHub API rate limiting is triggered
- Downloads are interrupted and partial files remain

## Common Symptoms

### Symptom 1: Connection Timeout / Recv Failure
```
curl: (28) Failed to connect to github.com port 443 after XXXXX ms: Could not connect to server
```

**Cause:** Network blockage (GFW, corporate firewall, proxy misconfiguration)

**Solutions:**

1. **Use VPN/proxy explicitly**
   ```bash
   # Check if proxy is set
   echo "http_proxy: ${http_proxy:-未设置}"
   echo "https_proxy: ${https_proxy:-未设置}"
   
   # If using 快柠檬 or similar, ensure it's connected
   # Then retry with explicit proxy
   curl -x http://127.0.0.1:10793 -L -O <download-url>
   ```

2. **Use different download method**
   ```bash
   # Method 1: Use git (bypasses some restrictions)
   git clone --depth 1 --branch grok-dev@1.1.7 https://github.com/superagent-ai/grok-cli.git
   
   # Method 2: Use wget if available
   wget -c -O grok.exe <download-url>
   
   # Method 3: Use aria2c (faster, resumes downloads)
   aria2c -x 16 -s 16 -c <download-url>
   ```

### Symptom 2: Incomplete/Partial Download
```
File size is smaller than expected
Cannot execute binary: "Exec format error" or "Permission denied"
```

**Cause:** Download was interrupted or network dropped packets

**Solutions:**

1. **Delete partial file and retry**
   ```bash
   rm -f /path/to/partial/file
   # Then retry download
   ```

2. **Use `--continue` or `-c` flag**
   ```bash
   curl -L --continue-at - -O <url>
   wget -c -O <url>
   aria2c -c <url>
   ```

3. **Verify file integrity**
   ```bash
   # Check file size
   ls -lh grok.exe
   
   # Check file type
   file grok.exe
   
   # For Windows binaries, expect: PE32+ executable for MS Windows
   ```

### Symptom 3: "Exec format error" in MSYS2/WSL
```
./grok.exe: cannot execute binary file: Exec format error
```

**Cause:** The file is a Windows PE binary, not a Linux ELF binary

**Solutions:**

1. **Run in Windows native environment**
   ```bash
   # Use cmd.exe or PowerShell
   cmd /c "C:\path\to\grok.exe --version"
   
   powershell -Command "& 'C:\path\to\grok.exe' --version"
   ```

2. **Use Windows-style paths**
   ```bash
   # In MSYS2/WSL, use Windows paths with double backslashes
   /c/Users/win10/grok.exe --version
   ```

3. **Add to PATH properly**
   ```bash
   # Edit ~/.bashrc or ~/.zshrc
   echo 'export PATH="/c/Users/win10:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Best Practices for Downloading Binaries

### 1. Use Multiple Download Methods
```bash
# Try curl first
curl -L -f -o grok.exe "<url>" --retry 5 --retry-delay 5 --max-time 180

# If curl fails, try wget
wget -c -O grok.exe "<url>"

# If both fail, try git clone
GIT_TERMINAL_PROMPT=0 git clone --depth 1 --branch v1.1.7 https://github.com/superagent-ai/grok-cli.git
```

### 2. Verify Download with Checksums
```bash
# Download checksums file
curl -L -O https://github.com/superagent-ai/grok-cli/releases/download/grok-dev%401.1.7/checksums.txt

# Verify binary
sha256sum grok.exe
# Should match one of the checksums in checksums.txt
```

### 3. Use Download Managers
```bash
# aria2c (recommended for large files)
aria2c -x 16 -s 16 -c <download-url>

# wget with resume capability
wget -c --tries=5 --timeout=30 <download-url>
```

### 4. Alternative Download Sources
```bash
# Use jsDelivr CDN mirror
curl -L -o grok.exe "https://cdn.jsdelivr.net/gh/superagent-ai/grok-cli@grok-dev%401.1.7/grok-windows-x64.exe"

# Use GitHub raw content
curl -L -o grok.exe "https://raw.githubusercontent.com/superagent-ai/grok-cli/grok-dev%401.1.7/bin/grok-windows-x64.exe"
```

## Windows-Specific Issues

### PATH Configuration
```powershell
# Set PATH permanently via PowerShell (Admin)
[Environment]::SetEnvironmentVariable("PATH", [Environment]::GetEnvironmentVariable("PATH", "User") + ";C:\Users\win10", "User")

# Or edit via System Properties → Environment Variables
```

### File Permissions
```powershell
# If "Access is denied" error:
# 1. Check file properties in Windows Explorer
# 2. Right-click → Properties → Unblock if marked as downloaded from internet
# 3. Run PowerShell as Administrator and try again
```

### Antivirus Interference
```powershell
# Temporarily disable antivirus if download is blocked
# Add exception for the download directory
```

## Cross-Platform Binary Naming

| Platform | Architecture | Binary Name | Notes |
|----------|-------------|-------------|-------|
| Windows | x64 | `grok-windows-x64.exe` | PE32+ executable |
| Windows | ARM64 | `grok-windows-arm64.exe` | PE32+ executable |
| macOS | x64 | `grok-darwin-x64` | Mach-O binary |
| macOS | ARM64 (Apple Silicon) | `grok-darwin-arm64` | Mach-O binary |
| Linux | x64 | `grok-linux-x64` | ELF binary |
| Linux | ARM64 | `grok-linux-arm64` | ELF binary |

## Quick Reference: GROK CLI Installation

### Windows (PowerShell)
```powershell
# Method 1: npm (if Node.js installed)
npm install -g grok-dev@latest

# Method 2: Manual download
Invoke-WebRequest -Uri "https://github.com/superagent-ai/grok-cli/releases/download/grok-dev%401.1.7/grok-windows-x64.exe" -OutFile "$env:USERPROFILE\grok.exe"

# Add to PATH
$env:Path += ";$env:USERPROFILE"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")

# Verify
grok --version
```

### macOS/Linux (Terminal)
```bash
# Method 1: npm
npm install -g grok-dev@latest

# Method 2: Manual download
curl -L -o grok https://github.com/superagent-ai/grok-cli/releases/download/grok-dev%401.1.7/grok-$(uname -s)-$(uname -m)
chmod +x grok
sudo mv grok /usr/local/bin/

# Verify
grok --version
```

## Related Skills

- `hermes-provider-troubleshooting`: Network/proxy troubleshooting
- `hermes-config-providers`: Adding custom providers to Hermes
- `computer-use`: Browser automation for downloading files

## External References

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [curl Manual](https://curl.se/docs/manpage.html)
- [aria2 Download Manager](https://aria2.github.io/)
