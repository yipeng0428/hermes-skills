#!/usr/bin/env python3
"""
模型使用情况日志记录器

追踪每个模型的使用情况，包括会话数量、响应时间、令牌使用等数据。
这些数据将用于智能模型排序系统。
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ModelUsageLogger:
    """模型使用情况日志记录器"""
    
    def __init__(self, storage_path: str = None):
        """
        初始化日志记录器
        
        Args:
            storage_path: 数据存储文件路径，默认使用 ~/.hermes/model_usage.json
        """
        if storage_path is None:
            home_dir = Path.home()
            storage_path = str(home_dir / ".hermes" / "model_usage.json")
        
        self.storage_path = Path(storage_path)
        self._ensure_storage_path()
        self.usage_data = self._load_usage_data()
    
    def _ensure_storage_path(self):
        """确保存储路径存在"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """加载模型使用数据"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  加载模型使用数据失败，将创建新数据文件: {e}")
        
        return {"models": {}, "last_updated": None}
    
    def _save_usage_data(self):
        """保存模型使用数据"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️  保存模型使用数据失败: {e}")
    
    def log_model_start(self, model_name: str, provider: str):
        """
        记录模型会话开始
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
        """
        model_key = f"{provider}:{model_name}"
        
        if model_key not in self.usage_data["models"]:
            self.usage_data["models"][model_key] = {
                "model_name": model_name,
                "provider": provider,
                "usage_count": 0,
                "total_sessions": 0,
                "avg_response_time": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "error_count": 0,
                "quality_score": 85.0,  # 默认质量评分
                "last_used": None,
                "first_used": datetime.now().isoformat(),
                "session_start_times": []
            }
        
        # 记录会话开始时间
        session_start = datetime.now().isoformat()
        self.usage_data["models"][model_key]["session_start_times"].append(session_start)
        self.usage_data["models"][model_key]["last_used"] = session_start
        
        self._save_usage_data()
    
    def log_model_response(self, model_name: str, provider: str, 
                          response_time: float, input_tokens: int, output_tokens: int):
        """
        记录模型响应数据
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
            response_time: 响应时间（秒）
            input_tokens: 输入令牌数
            output_tokens: 输出令牌数
        """
        model_key = f"{provider}:{model_name}"
        
        if model_key not in self.usage_data["models"]:
            return
        
        model_data = self.usage_data["models"][model_key]
        
        # 更新会话统计
        model_data["usage_count"] += 1
        model_data["total_sessions"] += 1
        model_data["total_input_tokens"] += input_tokens
        model_data["total_output_tokens"] += output_tokens
        
        # 更新响应时间统计（简单平均）
        if model_data["avg_response_time"] == 0:
            model_data["avg_response_time"] = response_time
        else:
            model_data["avg_response_time"] = (
                model_data["avg_response_time"] * (model_data["total_sessions"] - 1) + response_time
            ) / model_data["total_sessions"]
        
        # 更新最后使用时间
        model_data["last_used"] = datetime.now().isoformat()
        
        self._save_usage_data()
    
    def log_model_error(self, model_name: str, provider: str):
        """
        记录模型错误
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
        """
        model_key = f"{provider}:{model_name}"
        
        if model_key in self.usage_data["models"]:
            self.usage_data["models"][model_key]["error_count"] += 1
            self._save_usage_data()
    
    def update_quality_score(self, model_name: str, provider: str, score: float):
        """
        更新模型质量评分
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
            score: 质量评分 (0-100)
        """
        model_key = f"{provider}:{model_name}"
        
        if model_key in self.usage_data["models"]:
            self.usage_data["models"][model_key]["quality_score"] = max(0, min(100, score))
            self._save_usage_data()
    
    def get_model_stats(self, model_name: str, provider: str) -> Optional[Dict[str, Any]]:
        """
        获取模型统计数据
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
        
        Returns:
            模型统计数据字典，如果不存在则返回None
        """
        model_key = f"{provider}:{model_name}"
        return self.usage_data["models"].get(model_key)
    
    def get_all_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型的统计数据
        
        Returns:
            所有模型的统计数据字典
        """
        return self.usage_data["models"]
    
    def reset_model_stats(self, model_name: str, provider: str):
        """
        重置模型统计数据
        
        Args:
            model_name: 模型名称
            provider: 模型提供商
        """
        model_key = f"{provider}:{model_name}"
        
        if model_key in self.usage_data["models"]:
            del self.usage_data["models"][model_key]
            self._save_usage_data()
    
    def get_top_models(self, n: int = 5, weights: Dict[str, float] = None) -> list:
        """
        获取评分最高的前N个模型
        
        Args:
            n: 要获取的模型数量
            weights: 评分权重配置
        
        Returns:
            排序后的模型列表
        """
        if weights is None:
            weights = {"usage_frequency": 0.6, "response_quality": 0.4}
        
        models = []
        for model_key, model_data in self.usage_data["models"].items():
            # 计算使用频率评分 (0-100)
            usage_score = min(model_data["usage_count"] * 2, 100)
            
            # 质量评分 (0-100)
            quality_score = model_data["quality_score"]
            
            # 综合评分
            score = (usage_score * weights["usage_frequency"] + 
                     quality_score * weights["response_quality"])
            
            models.append({
                "model_key": model_key,
                "data": model_data,
                "score": score,
                "usage_score": usage_score,
                "quality_score": quality_score
            })
        
        # 按分数降序排序
        models.sort(key=lambda x: x["score"], reverse=True)
        
        return models[:n]


# 全局实例
logger = None

def get_logger() -> ModelUsageLogger:
    """获取全局日志记录器实例"""
    global logger
    if logger is None:
        logger = ModelUsageLogger()
    return logger


if __name__ == "__main__":
    # 测试代码
    print("📊 模型使用情况日志记录器 - 测试模式")
    
    logger = get_logger()
    
    # 测试记录模型使用
    print("\n📝 记录模型使用数据...")
    logger.log_model_start("gpt-5.6-luna-ca", "custom:chatanywhere")
    logger.log_model_response("gpt-5.6-luna-ca", "custom:chatanywhere", 1.2, 100, 500)
    logger.update_quality_score("gpt-5.6-luna-ca", "custom:chatanywhere", 92.5)
    
    logger.log_model_start("claude-opus-4-8", "jbbtoken")
    logger.log_model_response("claude-opus-4-8", "jbbtoken", 1.5, 120, 600)
    logger.update_quality_score("claude-opus-4-8", "jbbtoken", 94.2)
    
    logger.log_model_start("mistral-small-latest", "mistral")
    logger.log_model_response("mistral-small-latest", "mistral", 0.8, 80, 400)
    logger.update_quality_score("mistral-small-latest", "mistral", 89.7)
    
    # 获取统计数据
    print("\n📈 模型统计数据:")
    all_stats = logger.get_all_model_stats()
    for model_key, stats in all_stats.items():
        print(f"  {model_key}:")
        print(f"    使用次数: {stats['usage_count']}")
        print(f"    响应时间: {stats['avg_response_time']:.2f}s")
        print(f"    质量评分: {stats['quality_score']:.1f}%")
        print(f"    最后使用: {stats['last_used']}")
    
    # 获取前5名模型
    print("\n🏆 前5名模型:")
    top_models = logger.get_top_models(5)
    for i, model in enumerate(top_models, 1):
        print(f"  {i}. {model['model_key']} - 评分: {model['score']:.1f}")
        print(f"     使用频率评分: {model['usage_score']:.1f}, 质量评分: {model['quality_score']:.1f}")
        print(f"     理由: 使用{model['data']['usage_count']}次, 质量评分{model['data']['quality_score']:.1f}%")
