#!/usr/bin/env python3
"""
Notion 治理系统 - 健康评分计算器
用于计算 Notion 知识库的健康评分

用法:
    python health_score.py /path/to/scan_report.json
    python health_score.py /path/to/scan_report.json --output score.txt
"""

import json
import sys
import argparse
from datetime import datetime


def calculate_health_score(summary):
    """计算健康评分"""
    total_pages = summary.get('total_pages', 1)
    critical = summary.get('critical', 0)
    warning = summary.get('warning', 0)
    
    # 基础分数
    score = 100
    
    # 严重问题扣分 (每个扣 0.5 分)
    score -= critical * 0.5
    
    # 警告问题扣分 (每个扣 0.1 分)
    score -= warning * 0.1
    
    # 保护底线
    score = max(0, min(100, score))
    
    # 趋势调整
    trend = summary.get('trend', 'stable')
    if trend == 'improving':
        score += 5
    elif trend == 'worsening':
        score -= 5
    
    return round(score, 1)


def generate_health_report(summary, output_file=None):
    """生成健康报告"""
    score = calculate_health_score(summary)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "health_score": score,
        "severity_breakdown": {
            "critical": summary.get('critical', 0),
            "warning": summary.get('warning', 0),
            "info": summary.get('info', 0)
        },
        "recommendations": []
    }
    
    # 生成建议
    if score >= 90:
        report["recommendations"].append("✅ 知识库状态优秀，继续保持!")
    elif score >= 70:
        report["recommendations"].append("👍 知识库状态良好，轻微问题可逐步处理")
    elif score >= 50:
        report["recommendations"].append("🟡 知识库需要关注，建议处理警告问题")
        report["recommendations"].append("🔧 考虑运行自动修复: python fixer.py")
    else:
        report["recommendations"].append("🔴 知识库状态较差，需要立即处理!")
        report["recommendations"].append("🚨 建议运行全量扫描并手动处理严重问题")
    
    if summary.get('critical', 0) > 0:
        report["recommendations"].append(f"⚠️ 发现 {summary['critical']} 个严重问题，需要立即处理")
    
    if summary.get('warning', 0) > 100:
        report["recommendations"].append(f"⚠️ 发现 {summary['warning']} 个警告问题，建议逐步处理")
    
    # 打印报告
    print("=" * 60)
    print("💖 Notion 知识库健康评分报告")
    print("=" * 60)
    print(f"📊 健康评分: {score}/100")
    print(f"🔴 严重问题: {summary.get('critical', 0)} 个")
    print(f"🟡 警告问题: {summary.get('warning', 0)} 个")
    print(f"🟢 信息问题: {summary.get('info', 0)} 个")
    print()
    
    print("📋 建议:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    print()
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 报告已保存到: {output_file}")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Notion 治理系统 - 健康评分计算器"
    )
    parser.add_argument(
        "report_file",
        help="扫描报告 JSON 文件路径"
    )
    parser.add_argument(
        "--output",
        help="输出文件路径 (可选)",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        with open(args.report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        if not summary:
            print("❌ 报告文件格式错误，缺少 'summary' 字段")
            sys.exit(1)
        
        report = generate_health_report(summary, args.output)
        
        # 返回状态码
        if report['health_score'] < 60:
            sys.exit(2)  # 需要立即处理
        elif report['health_score'] < 80:
            sys.exit(1)  # 需要关注
        else:
            sys.exit(0)  # 状态良好
            
    except FileNotFoundError:
        print(f"❌ 文件不存在: {args.report_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ 文件格式错误: {args.report_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
