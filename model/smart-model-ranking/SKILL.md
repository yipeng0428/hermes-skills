---
name: smart-model-ranking
version: 1.0.0
description: 智能模型排序 - 基于使用频率和表现数据，将最好的5个模型优先展示在模型选择列表中
tags:
  - model-selection
  - performance-tracking
  - user-experience
  - optimization

# 触发条件
# - 用户在hermes config中设置了模型排序偏好
# - 用户手动触发模型排序命令
# - Hermes启动时自动加载

# 使用场景
# 1. 用户运行 `hermes model list` 时，最好的5个模型会优先显示
# 2. 用户在对话中使用 `/model` 命令时，智能推荐最适合的模型
# 3. 在模型选择界面中，最好的5个模型会被高亮显示

# 实现原理
# 1. 追踪每个模型的使用频率（会话数量）
# 2. 记录每个模型的响应质量评分（用户反馈/自动评估）
# 3. 计算综合排序分数 = 使用频率权重 × 响应质量权重
# 4. 将得分最高的5个模型移动到列表前端

# 配置选项
config_options:
  - name: smart_ranking_enabled
    type: boolean
    default: true
    description: 是否启用智能模型排序功能
  
  - name: ranking_weights
    type: object
    default:
      usage_frequency: 0.6
      response_quality: 0.4
    description: 排序权重配置
  
  - name: top_n_models
    type: integer
    default: 5
    description: 要优先展示的模型数量

# 实现步骤
implementation_steps:
  
  1. 创建模型使用数据收集系统:
     - 追踪每个模型的会话开始时间
     - 记录会话持续时间
     - 记录响应令牌数量
     - 记录用户反馈（如果有）

  2. 创建模型性能评分系统:
     - 自动评分：响应速度、令牌效率、错误率
     - 用户评分：收集用户对模型的反馈
     - 综合评分 = (响应速度评分 × 0.3) + (令牌效率评分 × 0.2) + (错误率评分 × 0.5) + (用户反馈评分 × 0.5)

  3. 实现智能排序算法:
     - 计算每个模型的综合分数
     - 使用加权公式：score = (usage_count × usage_weight) + (quality_score × quality_weight)
     - 对模型列表进行排序
     - 将得分最高的N个模型移动到列表前端

  4. 创建用户界面显示:
     - 在模型选择列表中高亮显示前5名
     - 添加排序原因说明（如"已使用25次，响应质量92%"）
     - 提供"重置排序"选项恢复默认顺序

  5. 添加配置管理:
     - 通过hermes config命令配置排序参数
     - 支持临时禁用排序功能
     - 支持调整权重和显示数量

# 文件结构
files:
  - path: scripts/hermes_model_selector.py
    description: "Hermes集成接口（胶水层，处理配置加载和格式化输出）"
    
  - path: scripts/model_usage_logger.py
    description: "模型使用数据收集和持久化 - 数据存储: ~/.hermes/model_usage.json"
    
  - path: scripts/smart_model_ranker.py
    description: "智能排序核心逻辑（评分计算、排序算法、格式化输出）"
    
  - path: scripts/configure_smart_ranking.sh
    description: "快速配置脚本（自动创建配置文件和数据文件）"
    
  - path: references/config_guide.md
    description: "配置指南（所有配置选项、使用场景、配置示例）"
    
  - path: references/bug-fix-log.md
    description: "集成Bug修复日志（KeyError/AttributeError修复记录）"

# 验证步骤
verification:
  - 测试模型排序是否正确应用
  - 验证配置选项是否生效
  - 检查性能数据收集是否正常
  - 测试用户界面显示是否正确
  - 验证排序算法的公平性和准确性

# 优化方向
optimization:
  - 添加机器学习模型来预测最佳模型
  - 集成用户行为分析（如常用任务类型）
  - 添加模型间的协同过滤推荐
  - 支持个性化排序（基于用户偏好）
  - 添加A/B测试框架评估排序效果

# 常见问题和调试
pitfalls:
  - "Python路径问题": 当脚本在Hermes内部执行时，需要确保Python能够导入技能目录。解决方案：在脚本开头添加 `sys.path.insert(0, str(Path(__file__).parent.parent))` 来添加技能目录到Python路径
  
  - "文件权限问题": 在Windows系统上，确保Hermes有权限创建和写入 `~/.hermes/model_usage.json` 文件。如果文件不存在，系统会自动创建
  
  - "配置文件格式": YAML配置文件需要严格的缩进格式。建议使用 `hermes config edit` 命令编辑配置以避免格式错误
  
  - "缓存文件": Python缓存文件（__pycache__）可以安全删除，不会影响功能。在调试脚本时，删除缓存文件后重新运行可以确保加载最新版本
  
  - "数据文件损坏": 如果 `model_usage.json` 文件损坏，系统会自动创建新的空文件。可以删除损坏的文件并重启Hermes让系统重建
  
  - "模型键格式": 模型标识符需要使用 `provider:model_name` 格式（如 `custom:chatanywhere:gpt-5.6-luna-ca`），确保在配置和代码中保持一致
  
  - "排序算法稳定性": 当使用频率和质量评分权重相等时，系统会优先选择使用次数更多的模型。调整权重可以改变排序行为
  
  - "Hermes集成测试": 在测试集成时，确保使用 `hermes reset` 重启Hermes以加载新的配置和技能。简单的 `/refresh` 命令可能不足以重新加载技能

# 示例输出
# 使用 `hermes model list` 命令的输出示例:
#
# 🏆 智能推荐模型 (基于使用频率和表现):
# 1. GPT-5.6 Luna CA (使用25次, 响应质量92%)
# 2. Claude Opus 4.8 (使用22次, 响应质量94%)
# 3. Mistral Small (使用18次, 响应质量89%)
# 4. SenseNova 6.7 Flash Lite (使用15次, 响应质量87%)
# 5. InternLM3 Latest (使用12次, 响应质量85%)
#
# 其他可用模型:
# 6. GPT-4.1 CA (使用8次, 响应质量91%)
# 7. GLM 5.2 (使用7次, 响应质量88%)
# ...

# 配置示例
# 在 ~/.hermes/config.yaml 中添加:
#
# smart_ranking:
#   enabled: true
#   top_n_models: 5
#   weights:
#     usage_frequency: 0.6
#     response_quality: 0.4

---

# 智能模型排序系统

## 功能概述

这个技能实现了您想要的功能：基于使用频率和表现数据，将最好的5个模型优先展示在模型选择列表中。系统会自动追踪每个模型的使用情况，计算综合评分，然后对模型列表进行智能排序。

## 核心功能

### 1. 使用数据收集
- **会话追踪**: 自动记录每个模型的使用会话数量
- **响应时间**: 记录模型响应时间，评估速度表现
- **令牌效率**: 追踪输入输出令牌数量，评估效率
- **错误率**: 记录模型错误和异常情况

### 2. 性能评分系统
- **自动评分**: 基于响应时间、令牌效率、错误率等客观指标
- **用户反馈**: 收集用户对模型的主观评价
- **综合评分**: 结合多个维度的加权评分

### 3. 智能排序算法
- **加权计算**: 使用 `score = (usage_count × 0.6) + (quality_score × 0.4)` 计算综合分数
- **动态更新**: 每次使用模型后自动更新排序
- **实时生效**: 排序结果立即应用于模型选择界面

### 4. 用户界面优化
- **高亮显示**: 前5名模型会被特殊标记和高亮
- **详细说明**: 显示每个模型的使用次数和质量评分
- **一键重置**: 支持恢复默认排序顺序

## 安装和配置

### 1. 启用智能排序

在您的 `~/.hermes/config.yaml` 文件中添加配置：

```yaml
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
```

### 2. 重启Hermes

配置修改后，需要重启Hermes才能生效：

```bash
hermes reset
```

## 使用方法

### 查看模型列表

使用以下命令查看智能排序后的模型列表：

```bash
hermes model list
```

输出示例：

```
🏆 智能推荐模型 (基于使用频率和表现):
1. GPT-5.6 Luna CA (使用25次, 响应质量92%)
2. Claude Opus 4.8 (使用22次, 响应质量94%)
3. Mistral Small (使用18次, 响应质量89%)
4. SenseNova 6.7 Flash Lite (使用15次, 响应质量87%)
5. InternLM3 Latest (使用12次, 响应质量85%)

其他可用模型:
6. GPT-4.1 CA (使用8次, 响应质量91%)
7. GLM 5.2 (使用7次, 响应质量88%)
8. LongCat 2.0 (使用5次, 响应质量83%)
...
```

### 临时切换模型

在对话中使用 `/model` 命令临时切换模型：

```
/model GPT-5.6 Luna CA
```

系统会智能推荐最适合当前任务的模型。

### 调整排序参数

您可以通过配置文件调整排序行为：

```yaml
smart_ranking:
  enabled: true
  top_n_models: 3  # 只显示前3个模型
  weights:
    usage_frequency: 0.7  # 更看重使用频率
    response_quality: 0.3  # 质量权重降低
```

## 技术实现

### 数据存储

模型使用数据存储在 `~/.hermes/model_usage.json` 文件中：

```json
{
  "models": {
    "gpt-5.6-luna-ca": {
      "usage_count": 25,
      "total_sessions": 25,
      "avg_response_time": 1.2,
      "total_input_tokens": 45000,
      "total_output_tokens": 180000,
      "error_count": 2,
      "quality_score": 92.3,
      "last_used": "2026-07-13T18:30:00Z"
    },
    "claude-opus-4-8": {
      "usage_count": 22,
      "total_sessions": 22,
      "avg_response_time": 1.5,
      "total_input_tokens": 52000,
      "total_output_tokens": 210000,
      "error_count": 1,
      "quality_score": 94.1,
      "last_used": "2026-07-13T18:25:00Z"
    }
  },
  "last_updated": "2026-07-13T18:35:00Z"
}
```

### 排序算法

```python
# 智能排序核心算法
def calculate_model_score(model_data, weights):
    """
    计算模型的综合评分
    
    参数:
        model_data: 模型数据字典
        weights: 权重配置字典
    
    返回:
        float: 综合评分
    """
    # 使用频率评分 (0-100)
    usage_score = min(model_data['usage_count'] * 2, 100)  # 每次使用得2分，上限100分
    
    # 响应质量评分 (0-100)
    quality_score = model_data['quality_score']
    
    # 综合评分
    score = (usage_score * weights['usage_frequency'] + 
             quality_score * weights['response_quality'])
    
    return score

def sort_models(models, config):
    """
    对模型列表进行智能排序
    
    参数:
        models: 模型列表
        config: 配置字典
    
    返回:
        list: 排序后的模型列表
    """
    # 计算每个模型的分数
    scored_models = []
    for model in models:
        score = calculate_model_score(model['data'], config['weights'])
        scored_models.append({
            'model': model,
            'score': score,
            'reason': f"使用{model['data']['usage_count']}次, 质量评分{model['data']['quality_score']:.1f}%"
        })
    
    # 按分数降序排序
    scored_models.sort(key=lambda x: x['score'], reverse=True)
    
    # 将前N个模型移动到前面
    top_models = scored_models[:config['top_n_models']]
    other_models = scored_models[config['top_n_models']:]
    
    # 合并结果
    sorted_models = top_models + other_models
    
    return sorted_models
```

## 优势和特点

### ✅ 智能推荐
基于实际使用数据，而不是固定顺序，确保推荐的模型真正适合您的需求。

### ✅ 动态更新
每次使用模型后自动更新排序，确保推荐始终基于最新的使用情况。

### ✅ 透明可解释
每个模型的排序理由都会显示出来，您可以了解为什么某个模型被推荐。

### ✅ 可配置性强
支持调整权重、显示数量等参数，完全适配您的使用习惯。

### ✅ 无缝集成
完全集成到现有的Hermes模型选择系统中，无需额外操作。

### ✅ Bug修复记录
集成过程中已修复的 Bug 请见 **references/bug-fix-log.md**：
- `display_index` KeyError — 排序结果未携带索引信息
- `reason` KeyError — 调用链中字段被过滤丢失
- `model.get()` AttributeError — 格式化层输入类型不一致

## 示例配置

### 情况1：偏好速度和效率

```yaml
smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.5
    response_quality: 0.5
```

### 情况2：偏好质量和稳定性

```yaml
smart_ranking:
  enabled: true
  top_n_models: 3
  weights:
    usage_frequency: 0.3
    response_quality: 0.7
```

### 情况3：临时禁用排序

```yaml
smart_ranking:
  enabled: false
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4
```

## 未来扩展

这个智能模型排序系统可以进一步扩展：

1. **个性化推荐**: 基于用户的任务类型偏好推荐模型
2. **任务上下文感知**: 根据当前对话内容推荐最适合的模型
3. **模型协同**: 根据任务复杂度自动选择多个模型协同工作
4. **成本优化**: 集成模型成本信息，在性能和成本间找到平衡
5. **实时反馈**: 收集用户即时反馈，动态调整模型排序

## 🛠️ 故障排除与调试

如果在使用过程中遇到任何问题，请参考技能中的 **"常见问题和调试"** 小节，其中包含了详细的故障排除指南和调试技巧。

系统完全自动化，无需手动维护，同时提供了丰富的配置选项，让您可以根据自己的需求调整排序策略。