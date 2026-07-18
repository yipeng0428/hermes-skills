---
# 智能模型排序配置示例

## 配置文件位置
`~/.hermes/config.yaml`

## 基础配置

```yaml
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
```

## 配置选项说明

### enabled (布尔值)
- **默认**: `true`
- **说明**: 是否启用智能模型排序功能
- **示例**: `enabled: false` 临时禁用排序

### top_n_models (整数)
- **默认**: `5`
- **说明**: 要优先展示的模型数量
- **示例**: `top_n_models: 3` 只显示前3个模型
- **范围**: 1-10

### weights (对象)
- **默认**:
  ```yaml
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
  ```
- **说明**: 排序权重配置，决定使用频率和质量评分的相对重要性
- **参数**:
  - `usage_frequency`: 使用频率权重 (0.0-1.0)
  - `response_quality`: 响应质量权重 (0.0-1.0)
- **示例**:
  ```yaml
  weights:
    usage_frequency: 0.7
    response_quality: 0.3
  ```
  这意味着更看重使用频率，质量评分的权重降低。

## 使用场景配置

### 情况1: 偏好速度和效率
```yaml
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.5
    response_quality: 0.5
```
**适用于**: 日常对话、快速响应需求

### 情况2: 偏好质量和稳定性
```yaml
smart_ranking:
  enabled: true
  top_n_models: 3
  weights:
    usage_frequency: 0.3
    response_quality: 0.7
```
**适用于**: 复杂任务、代码生成、创意写作

### 情况3: 平衡使用
```yaml
smart_ranking:
  enabled: true
  top_n_models: 4
  weights:
    usage_frequency: 0.55
    response_quality: 0.45
```
**适用于**: 通用场景，平衡速度和质量

### 情况4: 临时禁用排序
```yaml
smart_ranking:
  enabled: false
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
```
**适用于**: 测试、调试、特殊需求

## 数据存储位置

模型使用数据存储在:
```
~/.hermes/model_usage.json
```

### 数据格式示例
```json
{
  "models": {
    "custom:chatanywhere:gpt-5.6-luna-ca": {
      "model_name": "gpt-5.6-luna-ca",
      "provider": "custom:chatanywhere",
      "usage_count": 25,
      "total_sessions": 25,
      "avg_response_time": 1.2,
      "total_input_tokens": 45000,
      "total_output_tokens": 180000,
      "error_count": 2,
      "quality_score": 92.3,
      "last_used": "2026-07-13T18:30:00Z",
      "first_used": "2026-07-01T10:15:00Z",
      "session_start_times": [
        "2026-07-01T10:15:00Z",
        "2026-07-02T11:20:00Z",
        ...
      ]
    },
    "jbbtoken:claude-opus-4-8": {
      "model_name": "claude-opus-4-8",
      "provider": "jbbtoken",
      "usage_count": 22,
      "total_sessions": 22,
      "avg_response_time": 1.5,
      "total_input_tokens": 52000,
      "total_output_tokens": 210000,
      "error_count": 1,
      "quality_score": 94.1,
      "last_used": "2026-07-13T18:25:00Z",
      "first_used": "2026-07-01T09:30:00Z",
      "session_start_times": [
        "2026-07-01T09:30:00Z",
        "2026-07-03T14:45:00Z",
        ...
      ]
    }
  },
  "last_updated": "2026-07-13T18:35:00Z"
}
```

## 评分计算公式

### 使用频率评分
```
usage_score = min(usage_count × 2, 100)
```
- 每次使用得2分
- 上限100分（使用50次后不再增加分数）

### 响应质量评分
```
quality_score = 模型的质量评分 (0-100)
```
- 由系统自动评估和用户反馈决定
- 默认初始值85.0

### 综合评分
```
score = (usage_score × usage_frequency_weight) + (quality_score × quality_weight)
```

## 质量评分来源

1. **自动评估**:
   - 响应时间评分 (基于平均响应时间)
   - 令牌效率评分 (输入输出令牌比例)
   - 错误率评分 (错误次数占比)

2. **用户反馈**:
   - 收集用户对模型的主观评价
   - 通过对话中的隐式反馈评估

3. **综合评分**:
   ```
   quality_score = (response_speed_score × 0.3) +
                   (token_efficiency_score × 0.2) +
                   (error_rate_score × 0.5) +
                   (user_feedback_score × 0.5)
   ```

## 命令行使用

### 查看模型列表
```bash
hermes model list
```

输出示例:
```
🏆 智能推荐模型 (基于使用频率和表现):

1. GPT-5.6 Luna CA
   使用25次, 响应质量92.3%

2. Claude Opus 4.8
   使用22次, 响应质量94.1%

3. Mistral Small
   使用18次, 响应质量89.7%

4. SenseNova 6.7 Flash Lite
   使用15次, 响应质量87.2%

5. InternLM3 Latest
   使用12次, 响应质量85.8%

其他可用模型:

6. GPT-4.1 CA (使用8次, 响应质量91.5%)
7. GLM 5.2 (使用7次, 响应质量88.4%)
8. LongCat 2.0 (使用5次, 响应质量83.1%)
```

### 临时切换模型
```bash
/model GPT-5.6 Luna CA
```

## API集成

### 记录模型使用
```python
from scripts.model_usage_logger import get_logger

logger = get_logger()

# 记录会话开始
logger.log_model_start("gpt-5.6-luna-ca", "custom:chatanywhere")

# 记录响应数据
logger.log_model_response(
    "gpt-5.6-luna-ca", 
    "custom:chatanywhere", 
    response_time=1.2, 
    input_tokens=100, 
    output_tokens=500
)

# 更新质量评分
logger.update_quality_score("gpt-5.6-luna-ca", "custom:chatanywhere", 92.5)
```

### 获取排序后的模型
```python
from scripts.smart_model_ranker import SmartModelRanker

ranker = SmartModelRanker({
    "enabled": True,
    "top_n_models": 5,
    "weights": {"usage_frequency": 0.6, "response_quality": 0.4}
})

sorted_models = ranker.sort_models(original_models)
formatted_output = ranker.format_model_list_output(sorted_models)
```

## 故障排除

### 问题1: 排序功能没有生效
**检查项**:
- ✅ 配置文件中的 `smart_ranking.enabled` 是否设置为 `true`
- ✅ 配置文件路径是否正确 (`~/.hermes/config.yaml`)
- ✅ Hermes是否重新启动以加载新配置
- ✅ 模型使用数据文件是否存在 (`~/.hermes/model_usage.json`)

**解决方案**:
```bash
# 重新加载配置
hermes reset

# 或者手动创建配置
mkdir -p ~/.hermes
cat > ~/.hermes/config.yaml << EOF
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
EOF
```

### 问题2: 模型数据没有更新
**检查项**:
- ✅ 确保使用了正确的模型名称和提供商
- ✅ 检查数据存储文件是否有写入权限
- ✅ 验证 `model_usage_logger.py` 是否被正确调用

**解决方案**:
```bash
# 检查文件权限
ls -la ~/.hermes/model_usage.json

# 手动创建测试数据
python3 ~/.hermes/skills/model/smart-model-ranking/scripts/model_usage_logger.py
```

### 问题3: 排序结果不符合预期
**检查项**:
- ✅ 配置中的权重设置是否合理
- ✅ 模型的实际使用情况是否与预期一致
- ✅ 质量评分是否准确反映了模型表现

**解决方案**:
```yaml
# 调整权重示例
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.7  # 更看重使用频率
    response_quality: 0.3 # 质量权重降低
```

## 最佳实践

### 1. 定期检查配置
建议每月检查一次配置，确保排序策略仍然符合您的使用习惯。

### 2. 根据任务类型调整权重
- **编程任务**: 更看重响应质量
- **快速对话**: 更看重响应速度
- **创意写作**: 平衡使用频率和质量

### 3. 监控模型表现
定期查看模型使用数据，了解哪些模型表现最佳。

```bash
# 查看模型使用统计
cat ~/.hermes/model_usage.json
```

### 4. 提供用户反馈
系统会自动收集使用数据，但您也可以主动提供反馈来改进排序。

### 5. 备份重要数据
虽然模型使用数据不是关键数据，但建议定期备份配置文件。

```bash
cp ~/.hermes/config.yaml ~/.hermes/config_backup_$(date +%Y%m%d).yaml
cp ~/.hermes/model_usage.json ~/.hermes/model_usage_backup_$(date +%Y%m%d).json
```

## 技术支持

如果遇到问题，请检查:

1. **技能是否正确安装**:
   ```bash
   ls ~/.hermes/skills/model/smart-model-ranking/
   ```

2. **Python依赖是否满足**:
   ```bash
   python3 -c "import json; print('JSON模块可用')"
   ```

3. **配置文件格式是否正确**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"
   ```

## 未来扩展

这个智能模型排序系统设计为可扩展的，您可以考虑以下扩展功能:

1. **个性化推荐**: 基于用户的任务类型偏好推荐模型
2. **任务上下文感知**: 根据当前对话内容推荐最适合的模型
3. **模型协同**: 根据任务复杂度自动选择多个模型协同工作
4. **成本优化**: 集成模型成本信息，在性能和成本间找到平衡
5. **实时反馈**: 收集用户即时反馈，动态调整模型排序

---

**最后更新**: 2026-07-13
**版本**: 1.0.0
**作者**: Hermes Agent智能模型排序系统
