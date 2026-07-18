# AI会员监控系统 - 配置模板

## 📋 基础配置模板

```yaml
# config.yaml - 基础配置
monitoring:
  targets:
    - name: "Notion AI"
      keywords:
        - "Notion AI"
        - "Notion Premium"
        - "Notion Plus"
        - "Get Notion AI"
        - "Notion AI free trial"
        - "Notion AI student"
        - "Notion AI education"
      official_urls:
        - "https://www.notion.so/blog"
        - "https://www.notion.so/help"
        - "https://www.notion.so/pricing"
        - "https://www.notion.so/whats-new"

automation:
  headless: true
  timeout: 30
  chrome_path: "/c/Users/your-user/.cache/puppeteer/chrome/win64-150.0.7871.24/chrome-win64/chrome.exe"

database:
  type: "notion"
  api_key: "ntn_your_notion_api_key_here"
  database_id: "your_database_id_here"

notifications:
  dingtalk:
    webhook_url: "https://oapi.dingtalk.com/robot/send?access_token=your_webhook_token"
    secret: "your_secret_key"
  telegram:
    bot_token: "your_telegram_bot_token"
    chat_id: "your_telegram_chat_id"
  email:
    smtp_server: "smtp.example.com"
    port: 587
    username: "your-email@example.com"
    password: "your-email-password"
    from: "monitor@example.com"
    to: ["your-email@example.com"]

logging:
  level: "INFO"
  file: "monitor.log"
  max_size: 10485760
  backup_count: 5
```

## 🎯 高级配置模板

```yaml
# config-advanced.yaml - 高级配置
monitoring:
  targets:
    - name: "Notion AI"
      keywords: [...]
      official_urls: [...]
    - name: "Claude AI"
      keywords: [...]
      official_urls: [...]
    - name: "Gemini AI"
      keywords: [...]
      official_urls: [...]

proxy:
  enabled: true
  host: "127.0.0.1"
  port: 10793
  username: ""
  password: ""

automation:
  headless: true
  timeout: 60
  chrome_path: "/path/to/chrome"
  retry_attempts: 3
  implicit_wait: 10
  page_load_timeout: 30

database:
  type: "notion"
  api_key: "ntn_your_api_key"
  database_id: "your_database_id"
  auto_create_pages: true
  update_existing: true

notifications:
  priority_threshold: 80
  daily_summary: true
  weekly_report: true
  monthly_report: true

logging:
  level: "DEBUG"
  file: "monitor-debug.log"
  max_size: 52428800  # 50MB
  backup_count: 10
  console_output: true
```

## 🔧 环境变量配置

```bash
# .env文件 - 环境变量配置
NOTION_API_KEY=ntn_your_api_key_here
NOTION_DATABASE_ID=your_database_id_here
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=your_token
DINGTALK_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password

# 代理配置
HTTP_PROXY=http://127.0.0.1:10793
HTTPS_PROXY=http://127.0.0.1:10793
```

## 📝 配置文件最佳实践

### 1. 使用环境变量
```yaml
# config.yaml
database:
  api_key: "${NOTION_API_KEY}"
  database_id: "${NOTION_DATABASE_ID}"
```

### 2. 多环境配置
```yaml
# config-dev.yaml - 开发环境
monitoring:
  targets:
    - name: "Notion AI Dev"
      keywords: [...]

automation:
  headless: false  # 非无头模式便于调试
  timeout: 10

# config-prod.yaml - 生产环境
monitoring:
  targets:
    - name: "Notion AI"
      keywords: [...]

automation:
  headless: true
  timeout: 60
```

### 3. 模块化配置
```yaml
# config-base.yaml - 基础配置
monitoring:
  targets: []

automation:
  headless: true

database:
  type: "notion"

# config-notion.yaml - Notion配置
monitoring:
  targets:
    - name: "Notion AI"
      keywords: [...]

database:
  api_key: "${NOTION_API_KEY}"
  database_id: "${NOTION_DATABASE_ID}"

# config-social.yaml - 社交媒体配置
monitoring:
  targets:
    - name: "Twitter AI"
      keywords: [...]
```

## 🛠️ 配置验证脚本

```python
# validate_config.py - 配置文件验证
import yaml
import sys

def validate_config(config_path):
    """验证配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查必填字段
        required_fields = ['monitoring', 'database']
        for field in required_fields:
            if field not in config:
                print(f"❌ 缺少必填字段: {field}")
                return False
        
        # 检查目标配置
        targets = config['monitoring'].get('targets', [])
        if not targets:
            print("⚠️  未配置监控目标")
        
        # 检查数据库配置
        db_config = config['database']
        if db_config.get('type') == 'notion':
            if not db_config.get('api_key'):
                print("❌ Notion API密钥未配置")
                return False
            if not db_config.get('database_id'):
                print("❌ Notion数据库ID未配置")
                return False
        
        print("✅ 配置文件验证通过!")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python validate_config.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    success = validate_config(config_file)
    sys.exit(0 if success else 1)
```

## 📊 配置文件示例库

### 示例1: Notion AI监控
```yaml
monitoring:
  targets:
    - name: "Notion AI"
      keywords:
        - "Notion AI"
        - "Notion Premium"
        - "Notion Plus"
        - "Get Notion AI"
        - "Notion AI free trial"
        - "Notion AI student"
        - "Notion AI education"
        - "Notion AI discount"
        - "Notion AI giveaway"
      official_urls:
        - "https://www.notion.so/blog"
        - "https://www.notion.so/help"
        - "https://www.notion.so/pricing"
        - "https://www.notion.so/whats-new"

automation:
  headless: true
  timeout: 30

database:
  type: "notion"
  api_key: "${NOTION_API_KEY}"
  database_id: "${NOTION_DATABASE_ID}"

notifications:
  dingtalk:
    webhook_url: "${DINGTALK_WEBHOOK_URL}"
    secret: "${DINGTALK_SECRET}"
  telegram:
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
```

### 示例2: Claude AI监控
```yaml
monitoring:
  targets:
    - name: "Claude AI"
      keywords:
        - "Claude AI"
        - "Claude Pro"
        - "Claude subscription"
        - "Get Claude"
        - "Claude free trial"
        - "Claude student discount"
      official_urls:
        - "https://www.anthropic.com/claude"
        - "https://www.anthropic.com/pricing"

automation:
  headless: true
  timeout: 45

database:
  type: "notion"
  api_key: "${NOTION_API_KEY}"
  database_id: "${ANTHROPIC_DATABASE_ID}"

notifications:
  email:
    smtp_server: "smtp.gmail.com"
    port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"
    from: "claude-monitor@gmail.com"
    to: ["${EMAIL_USERNAME}"]
```

### 示例3: 多产品监控
```yaml
monitoring:
  targets:
    - name: "Notion AI"
      keywords: [...]
      official_urls: [...]
    - name: "Claude AI"
      keywords: [...]
      official_urls: [...]
    - name: "Gemini AI"
      keywords: [...]
      official_urls: [...]
    - name: "Mistral AI"
      keywords: [...]
      official_urls: [...]

automation:
  headless: true
  timeout: 60

database:
  type: "notion"
  api_key: "${NOTION_API_KEY}"
  database_id: "${MULTI_PRODUCT_DATABASE_ID}"

notifications:
  dingtalk:
    webhook_url: "${DINGTALK_WEBHOOK_URL}"
  telegram:
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
```

## 🔄 配置文件管理脚本

```bash
# config-manager.sh - 配置文件管理脚本

#!/bin/bash

CONFIG_DIR="~/ai-member-monitor/configs"
CURRENT_CONFIG="config.yaml"

# 创建配置目录
mkdir -p "$CONFIG_DIR"

# 切换配置
switch_config() {
    local config_name=$1
    if [ -f "$CONFIG_DIR/$config_name" ]; then
        cp "$CONFIG_DIR/$config_name" "~/ai-member-monitor/config.yaml"
        echo "✅ 已切换到配置: $config_name"
    else
        echo "❌ 配置文件不存在: $config_name"
    fi
}

# 创建新配置
create_config() {
    local config_name=$1
    cat > "$CONFIG_DIR/$config_name" << 'EOF'
# $config_name 配置文件
monitoring:
  targets: []

automation:
  headless: true

database:
  type: "notion"
  api_key: ""
  database_id: ""

notifications:
  dingtalk:
    webhook_url: ""
    secret: ""
EOF
    echo "✅ 已创建配置文件: $config_name"
}

# 列出所有配置
list_configs() {
    echo "📋 可用配置文件:"
    ls -1 "$CONFIG_DIR"
}

# 验证配置
validate_config() {
    python ~/ai-member-monitor/validate_config.py ~/ai-member-monitor/config.yaml
}

# 显示帮助
show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  switch <config_name>    切换到指定配置"
    echo "  create <config_name>    创建新配置文件"
    echo "  list                   列出所有配置"
    echo "  validate               验证当前配置"
    echo "  help                   显示帮助"
}

# 主逻辑
case "$1" in
    switch)
        switch_config "$2"
        ;;
    create)
        create_config "$2"
        ;;
    list)
        list_configs
        ;;
    validate)
        validate_config
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
```

## 📚 配置最佳实践

### ✅ 好的配置实践
- 使用环境变量存储敏感信息
- 为不同环境创建不同的配置文件
- 添加详细的注释说明每个字段
- 定期备份配置文件
- 使用版本控制管理配置变更

### ❌ 不好的配置实践
- 直接在配置文件中写入密码
- 使用硬编码的API密钥
- 不验证配置文件格式
- 不备份配置文件
- 配置文件权限设置不当

### 🔧 配置文件安全
```bash
# 设置配置文件权限
chmod 600 config.yaml
chmod 600 .env

# 使用git忽略敏感文件
cat >> .gitignore << 'EOF'
config.yaml
.env
*.log
__pycache__/
EOF

# 使用git-crypt加密敏感文件
# git-crypt unlock
```