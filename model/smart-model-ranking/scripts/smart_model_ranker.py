#!/usr/bin/env python3
"""
智能模型排序核心逻辑

实现模型的智能排序算法，基于使用频率和表现数据。
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class SmartModelRanker:
    """智能模型排序器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化智能排序器
        
        Args:
            config: 配置字典，包含排序参数
        """
        if config is None:
            config = {
                "enabled": True,
                "top_n_models": 5,
                "weights": {
                    "usage_frequency": 0.6,
                    "response_quality": 0.4
                }
            }
        
        self.config = config
        self.usage_logger = None
    
    def load_usage_data(self):
        """加载模型使用数据"""
        home_dir = Path.home()
        storage_path = str(home_dir / ".hermes" / "model_usage.json")
        
        try:
            if Path(storage_path).exists():
                with open(storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        
        return {"models": {}}
    
    def calculate_model_score(self, model_data: Dict[str, Any]) -> float:
        """
        计算单个模型的综合评分
        
        Args:
            model_data: 模型数据字典
        
        Returns:
            float: 综合评分 (0-100)
        """
        # 使用频率评分 (0-100)
        # 每次使用得2分，上限100分
        usage_score = min(model_data.get("usage_count", 0) * 2, 100)
        
        # 响应质量评分 (0-100)
        quality_score = model_data.get("quality_score", 85.0)
        
        # 综合评分
        score = (usage_score * self.config["weights"]["usage_frequency"] +
                 quality_score * self.config["weights"]["response_quality"])
        
        return score
    
    def generate_reason_text(self, model_data: Dict[str, Any]) -> str:
        """
        生成模型排序理由文本
        
        Args:
            model_data: 模型数据字典
        
        Returns:
            str: 理由文本
        """
        usage_count = model_data.get("usage_count", 0)
        quality_score = model_data.get("quality_score", 85.0)
        
        return f"使用{usage_count}次, 响应质量{quality_score:.1f}%"
    
    def sort_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对模型列表进行智能排序
        
        Args:
            models: 原始模型列表
        
        Returns:
            List[Dict]: 排序后的模型列表
        """
        if not self.config["enabled"]:
            # 如果禁用排序，返回原始列表
            return models
        
        # 为每个模型计算评分
        scored_models = []
        for model in models:
            model_key = model.get("key", "")
            model_data = model.get("data", {})
            
            # 从使用数据中获取更详细的统计
            usage_data = self.load_usage_data()
            detailed_data = usage_data.get("models", {}).get(model_key, {})
            
            # 合并数据
            merged_data = {**model_data, **detailed_data}
            
            score = self.calculate_model_score(merged_data)
            reason = self.generate_reason_text(merged_data)
            
            scored_models.append({
                "original_index": model.get("original_index", 0),
                "model": model,
                "score": score,
                "reason": reason,
                "usage_count": merged_data.get("usage_count", 0),
                "quality_score": merged_data.get("quality_score", 85.0)
            })
        
        # 按分数降序排序
        scored_models.sort(key=lambda x: x["score"], reverse=True)
        
        # 将前N个模型移动到前面
        top_models = scored_models[:self.config["top_n_models"]]
        other_models = scored_models[self.config["top_n_models"]:]
        
        # 合并结果，保持原始顺序中的其他模型
        sorted_models = top_models + other_models
        
        # 恢复原始顺序中的索引
        for i, model_info in enumerate(sorted_models):
            model_info["display_index"] = i + 1
        
        return sorted_models
    
    def format_model_list(self, models: List[Dict[str, Any]]) -> str:
        """
        格式化模型列表显示
        
        Args:
            models: 排序后的模型列表
        
        Returns:
            str: 格式化后的模型列表字符串
        """
        output = []
        
        # 添加智能推荐标题
        output.append("🏆 智能推荐模型 (基于使用频率和表现):")
        output.append("")
        
        # 添加前5名模型
        for i, model_info in enumerate(models[:self.config["top_n_models"]], 1):
            model = model_info["model"]
            if isinstance(model, dict):
                model_name = model.get('name', '未知模型')
            else:
                model_name = str(model)
            output.append(f"{i}. {model_name}")
            output.append(f"   {model_info['reason']}")
        
        output.append("")
        
        # 添加其他模型
        if len(models) > self.config["top_n_models"]:
            output.append("其他可用模型:")
            for i, model_info in enumerate(models[self.config["top_n_models"]:], self.config["top_n_models"] + 1):
                model = model_info["model"]
                if isinstance(model, dict):
                    model_name = model.get('name', '未知模型')
                else:
                    model_name = str(model)
                output.append(f"{i}. {model_name} ({model_info['reason']})")
        
        return "\n".join(output)


def main():
    """主函数 - 演示智能排序功能"""
    
    print("🤖 智能模型排序系统 - 演示")
    print("=" * 50)
    
    # 示例模型数据
    example_models = [
        {
            "key": "custom:chatanywhere:gpt-5.6-luna-ca",
            "name": "GPT-5.6 Luna CA",
            "provider": "custom:chatanywhere",
            "data": {"model": "gpt-5.6-luna-ca"}
        },
        {
            "key": "jbbtoken:claude-opus-4-8",
            "name": "Claude Opus 4.8",
            "provider": "jbbtoken",
            "data": {"model": "claude-opus-4-8"}
        },
        {
            "key": "mistral:mistral-small-latest",
            "name": "Mistral Small",
            "provider": "mistral",
            "data": {"model": "mistral-small-latest"}
        },
        {
            "key": "sensenova:glm-5.2",
            "name": "SenseNova 6.7 Flash Lite",
            "provider": "sensenova",
            "data": {"model": "sensenova-6.7-flash-lite"}
        },
        {
            "key": "intern:internlm3-latest",
            "name": "InternLM3 Latest",
            "provider": "intern",
            "data": {"model": "internlm3-latest"}
        },
        {
            "key": "custom:chatanywhere:gpt-4.1-ca",
            "name": "GPT-4.1 CA",
            "provider": "custom:chatanywhere",
            "data": {"model": "gpt-4.1-ca"}
        },
        {
            "key": "sensenova:deepseek-v4-flash",
            "name": "DeepSeek V4 Flash",
            "provider": "sensenova",
            "data": {"model": "deepseek-v4-flash"}
        }
    ]
    
    # 默认配置
    config = {
        "enabled": True,
        "top_n_models": 5,
        "weights": {
            "usage_frequency": 0.6,
            "response_quality": 0.4
        }
    }
    
    # 创建排序器
    ranker = SmartModelRanker(config)
    
    # 进行排序
    sorted_models = ranker.sort_models(example_models)
    
    # 格式化输出
    formatted_output = ranker.format_model_list(sorted_models)
    
    print(formatted_output)
    
    print("\n" + "=" * 50)
    print("✅ 智能排序演示完成！")
    print("\n这个系统会自动追踪您的模型使用情况，并根据实际表现智能排序。")
    print("您可以通过配置文件调整排序参数，完全适配您的使用习惯。")


if __name__ == "__main__":
    main()
