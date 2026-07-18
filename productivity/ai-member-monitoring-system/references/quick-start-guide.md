# AI会员监控系统 - 快速开始指南

## 🚀 5分钟快速上手

### 第1步: 创建项目目录
```bash
mkdir -p ~/ai-member-monitor
cd ~/ai-member-monitor
```

### 第2步: 创建配置文件
```bash
cat > config.yaml << 'EOF'
# AI会员监控系统配置

monitoring:
  targets:
    - name: "Notion AI"
      keywords: ["Notion AI", "Notion Premium", "Notion Plus"]
      official_urls:
        - "https://www.notion.so/blog"
        - "https://www.notion.so/help"
        - "https://www.notion.so/pricing"

automation:
  headless: true
  timeout: 30

database:
  type: "notion"
  api_key: "ntn_your_api_key"
  database_id: "your_database_id"

notifications:
  dingtalk:
    webhook_url: "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
    secret: "YOUR_SECRET"
EOF
```

### 第3步: 安装依赖
```bash
pip install requests beautifulsoup4 schedule pyyaml selenium
```

### 第4步: 创建主监控脚本
```python
# monitor.py
from datetime import datetime
import yaml
import logging

class AIMemberMonitor:
    def __init__(self, config_path='config.yaml'):
        self.config = self.load_config(config_path)
        self.setup_logging()
    
    def load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_official_sources(self):
        import requests
        from bs4 import BeautifulSoup
        
        opportunities = []
        target = self.config['monitoring']['targets'][0]
        
        for url in target['official_urls']:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text()
                
                if any(keyword.lower() in content.lower() for keyword in target['keywords']):
                    opportunity = {
                        'target': target['name'],
                        'title': f"{target['name']} - 官方公告",
                        'source': 'official',
                        'source_url': url,
                        'type': ['official_announcement'],
                        'content': content[:300] + "...",
                        'discovered_at': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
                    logging.info(f"发现机会: {opportunity['title']}")
                    
            except Exception as e:
                logging.warning(f"检查 {url} 失败: {e}")
        
        return opportunities
    
    def run(self):
        opportunities = self.check_official_sources()
        logging.info(f"发现 {len(opportunities)} 个机会")
        return opportunities

if __name__ == "__main__":
    monitor = AIMemberMonitor()
    monitor.run()
```

### 第5步: 运行监控
```bash
python monitor.py
```

### 第6步: 设置定时任务
```bash
crontab -e
# 添加: 0 * * * * cd ~/ai-member-monitor && python monitor.py >> monitor.log 2>&1
```

## 📊 系统功能

- ✅ 多渠道监控 (官方、社交媒体、社区)
- ✅ 智能评分系统 (0-100分)
- ✅ 实时通知 (钉钉、Telegram、邮件)
- ✅ 自动执行 (Selenium自动化)
- ✅ 数据管理 (Notion数据库集成)

## 🛠️ 故障排除

### 常见问题

**问题**: 配置文件加载失败
**解决**: 确保 `config.yaml` 文件存在且格式正确

**问题**: 依赖安装失败
**解决**: 使用 `pip install -r requirements.txt`

**问题**: 网络请求超时
**解决**: 检查网络连接，或配置代理

**问题**: 通知发送失败
**解决**: 检查Webhook URL和API密钥

## 📚 更多资源

- [完整系统方案](https://github.com/nousresearch/hermes-agent)
- [AI会员监控系统技能文档](skill://ai-member-monitoring-system)
- [Notion API文档](https://developers.notion.com)