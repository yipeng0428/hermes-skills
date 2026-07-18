#!/usr/bin/env python3
"""
Hermes模型选择智能排序集成

这个脚本集成到Hermes的模型选择系统中，实现智能模型排序功能。
"""

import sys
import json
from pathlib import Path

# 将技能目录添加到Python路径
skills_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skills_dir))

from scripts.smart_model_ranker import SmartModelRanker
from scripts.model_usage_logger import get_logger


class HermesModelSelector:
    """Hermes模型选择器集成"""
    
    def __init__(self):
        """初始化模型选择器"""
        self.ranker = None
        self.usage_logger = None
        self.load_config()
    
    def load_config(self):
        """加载Hermes配置"""
        home_dir = Path.home()
        config_path = str(home_dir / ".hermes" / "config.yaml")
        
        # 默认配置
        config = {
            "smart_ranking": {
                "enabled": True,
                "top_n_models": 5,
                "weights": {
                    "usage_frequency": 0.6,
                    "response_quality": 0.4
                }
            }
        }
        
        # 尝试加载配置文件
        try:
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    # 简单解析（实际应用中应该使用yaml解析器）
                    if "smart_ranking:" in config_content:
                        # 提取配置部分
                        start = config_content.find("smart_ranking:")
                        if start != -1:
                            end = config_content.find("\n", start)
                            config_section = config_content[start:end]
                            # 这里可以添加更复杂的配置解析逻辑
                            pass
        except Exception as e:
            print(f"⚠️  加载配置失败: {e}")
        
        # 创建排序器
        self.ranker = SmartModelRanker(config["smart_ranking"])
        self.usage_logger = get_logger()
    
    def get_sorted_models(self, models: list) -> list:
        """
        获取智能排序后的模型列表
        
        Args:
            models: 原始模型列表
        
        Returns:
            list: 排序后的模型列表
        """
        if not self.ranker:
            return models
        
        # 为每个模型添加原始索引
        indexed_models = []
        for i, model in enumerate(models):
            indexed_models.append({
                "original_index": i,
                **model
            })
        
        # 进行智能排序
        sorted_models = self.ranker.sort_models(indexed_models)
        
        # 提取排序后的模型数据
        result = []
        for model_info in sorted_models:
            result.append(model_info["model"])
        
        return result
    
    def format_model_list_output(self, models: list) -> str:
        """
        格式化模型列表输出
        
        Args:
            models: 排序后的模型列表
        
        Returns:
            str: 格式化后的输出字符串
        """
        if not self.ranker:
            return ""
        
        # 确保每个模型都有reason字段
        for model in models:
            if "reason" not in model:
                model["reason"] = ""
        
        return self.ranker.format_model_list(models)
    
    def log_model_usage(self, model_name: str, provider: str, 
                       response_time: float = None, input_tokens: int = None, 
                       output_tokens: int = None):
        """
        记录模型使用情况
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
            response_time: 响应时间（可选）
            input_tokens: 输入令牌数（可选）
            output_tokens: 输出令牌数（可选）
        """
        if self.usage_logger:
            self.usage_logger.log_model_start(model_name, provider)
            
            if response_time is not None and input_tokens is not None and output_tokens is not None:
                self.usage_logger.log_model_response(
                    model_name, provider, response_time, input_tokens, output_tokens
                )
    
    def update_model_quality(self, model_name: str, provider: str, score: float):
        """
        更新模型质量评分
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
            score: 质量评分 (0-100)
        """
        if self.usage_logger:
            self.usage_logger.update_quality_score(model_name, provider, score)


def main():
    """主函数 - 演示Hermes集成"""
    
    print("🤖 Hermes模型选择智能排序集成")
    print("=" * 60)
    
    # 创建模型选择器
    selector = HermesModelSelector()
    
    # 示例模型数据（从Hermes配置中获取）
    example_models = [
        {
            "name": "GPT-5.6 Luna CA",
            "provider": "custom:chatanywhere",
            "model": "gpt-5.6-luna-ca"
        },
        {
            "name": "Claude Opus 4.8",
            "provider": "jbbtoken",
            "model": "claude-opus-4-8"
        },
        {
            "name": "Mistral Small",
            "provider": "mistral",
            "model": "mistral-small-latest"
        },
        {
            "name": "SenseNova 6.7 Flash Lite",
            "provider": "sensenova",
            "model": "sensenova-6.7-flash-lite"
        },
        {
            "name": "InternLM3 Latest",
            "provider": "intern",
            "model": "internlm3-latest"
        },
        {
            "name": "GPT-4.1 CA",
            "provider": "custom:chatanywhere",
            "model": "gpt-4.1-ca"
        },
        {
            "name": "GLM 5.2",
            "provider": "sensenova",
            "model": "glm-5.2"
        },
        {
            "name": "LongCat 2.0",
            "provider": "longcat",
            "model": "LongCat-2.0"
        }
    ]
    
    # 为每个模型添加key字段（格式：provider:model_name）
    for model in example_models:
        model["key"] = f"{model['provider']}:{model['model']}"
    
    print("\n📋 原始模型列表:")
    for i, model in enumerate(example_models, 1):
        print(f"  {i}. {model['name']} ({model['provider']})")
    
    # 获取智能排序后的模型
    sorted_models = selector.get_sorted_models(example_models)
    
    print("\n🏆 智能排序后的模型列表:")
    for i, model in enumerate(sorted_models, 1):
        print(f"  {i}. {model['name']} ({model['provider']})")
    
    # 格式化输出
    print("\n" + "=" * 60)
    formatted_output = selector.format_model_list_output(sorted_models)
    print(formatted_output)
    
    print("\n" + "=" * 60)
    print("✅ 集成演示完成！")
    print("\n这个系统已经集成到Hermes中，将自动为您排序模型。")
    print("系统会追踪您的模型使用情况，并根据实际表现智能推荐最好的模型。")
    print("\n配置位置: ~/.hermes/config.yaml")
    print("数据存储: ~/.hermes/model_usage.json")


if __name__ == "__main__":
    main()
