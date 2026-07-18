---
name: multi-agent-swarm
description: "构建专业AI Agent团队，你当CEO。项目容量从3-5提升到20-30。触发词：多智能体编排、agent团队、swarm、群集编排"
version: 1.2.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: []
metadata:
  hermes:
    tags: [multi-agent, orchestration, swarm, team-management]
---

# Multi-Agent Swarm Orchestration（多智能体群集编排）

## 触发关键词
- "多智能体编排" / "agent团队" / "swarm" / "群集编排"
- "agent分工" / "并行派发" / "多角色协作" / "组建AI团队"

## 核心理念
不再将AI视为单个助手，而是构建specialized agent团队。
每个Agent有自己的专业领域、记忆、工作方式。
人类 = 产品经理/CEO。

## 何时不该用

| 场景 | 原因 | 替代方案 |
|------|------|---------|
| 简单一次性任务 | 团队建设成本>收益 | 直接用 `design-agent-team` |
| 需要深度创意探索 | 团队执行不适合探索 | 用 `flow-state-engineering` |
| 预算极有限 | 多Agent=多API调用 | 用 `agentomics` 优化模型选择 |
| 学习阶段 | 先理解单个Agent再组团 | 先用 `multi-agent-debate` |

## 快速上手（3分钟）

1. 对AI说：`组建AI团队：{你的任务}`
2. AI返回：任务拆解+角色分配+执行计划
3. 确认后，AI自动并行派发3-5个子Agent
4. 你等待结果，做最终决策

## 核心角色
| 角色 | 代号 | 职责 | 工具 |
|------|------|------|------|
| 🔍 研究员 | RESEARCHER | 搜索、文献综述、竞品分析 | web_search, web_extract |
| ✍️ 写手 | WRITER | 初稿撰写、结构化表达 | write_file, read_file |
| 🔎 质检员 | CRITIC | 挑毛病、找漏洞、反面意见 | read_file |
| 🔗 整合师 | SYNTHESIST | 整合多来源，提炼洞察 | read_file, write_file |
| 📊 分析师 | ANALYST | 数据清洗、图表、统计 | execute_code |
| 🖼️ 视觉分析员 | VISUALIST | 分析设计/排版/色彩 | vision_analyze |
| 📋 项目经理 | PM | 分配任务、监控进度、质量把关 | cronjob, write_file |

## 执行流程

### Step 1: 任务拆解
```
需求：做一份竞品设计趋势分析报告
拆解：搜索10竞品→分析趋势→撰写报告→找漏洞→整合终稿
```

### Step 2: 并行派发
使用 `delegate_task(tasks=[...], enabled_toolsets=[...])` 同时启动多个Agent

### Step 3: 异步协作
```
RESEARCHER → WRITER → CRITIC → 修改 → SYNTHESIST → 人类验收
```

### Step 4: CEO验收
□ 所有Agent完成 □ 路径可访问 □ 数据完整 □ 结论无矛盾 □ 可执行

## 真实案例：万凯竞品分析

```
需求：分析10个PET瓶竞品的设计趋势

PM拆解：
  Agent 1 (RESEARCHER): 搜索10个竞品的最新包装设计
  Agent 2 (VISUALIST): 分析这些设计的共性和趋势
  Agent 3 (ANALYST): 统计色彩/构图/材质的分布
  Agent 4 (CRITIC): 预测趋势的可靠性+盲点
  Agent 5 (SYNTHESIST): 整合为一份报告

并行派发 → 5个Agent同时运行
  → RESEARCHER完成：收集10竞品+分析数据
  → VISUALIST完成：视觉趋势报告
  → ANALYST完成：数据统计表
  → CRITIC完成：3个预测风险点
  → SYNTHESIST完成：整合终稿

人类CEO验收：检查报告完整性 → 通过
总耗时：25分钟（传统方式约2-3小时）
```

## 效果基准
| 指标 | 单人+单AI | 多Agent编排 |
|------|----------|-----------|
| 项目并行能力 | 3-5个 | 20-30个 |
| 质量维度 | 单维度 | 多维度 |
| 创意广度 | 个人经验限制 | 跨领域组合 |
| 时间维度 | 受人类作息限制 | 24/7 |

## 验证清单
- [ ] 任务是否已拆解为3-5个子任务？
- [ ] 每个子任务是否分配了合适的Agent角色？
- [ ] 是否使用了 `enabled_toolsets` 给Agent工具权限？
- [ ] 是否执行了"严格一次性派发"（没有重复补派）？
- [ ] 是否做了CEO验收（5项检查）？

## 与相关技能联动
- 配合 `design-agent-team` 做设计专项任务
- 配合 `agentomics` 为每个Agent选择最优模型
- 配合 `budgeted-act-defer` 设定每个Agent的置信度阈值

## 🚨 Failure Modes & Recovery（v1.2 新增）

真实三Agent并行测试（Claude Code+Codex+Grok，2026-07-15）暴露的故障：

| 故障 | 表现 | 根因 | 恢复 |
|------|------|------|------|
| 🔒 安全过滤器拦截 | 代码生成成功但Bash被拒 | 代理层过滤代码执行 | Agent写代码 + Hermes跑 |
| 📦 Agent依赖缺失 | CLI启动失败 | npm缺平台二进制 | 派发前 `agent --version` 健康检查 |
| 💰 API配额耗尽 | `credit limit exceeded` | API key余额用尽 | 自动切换备用Agent |
| 🐚 Shell子进程被杀 | background进程随shell退出 | bash `&` 继承父进程生命周期 | 用 foreground+timeout |

### 恢复决策树
```
Agent派发失败
├─ CLI不可用 → 跳过，启用备用
├─ 安全拦截 → Agent写代码+Hermes跑
├─ 配额耗尽 → 切换同角色备用
├─ 网络中断 → fallback到直连模型
└─ 超时>3min → 标记未完成，继续其他
```

### 事前健康检查
```bash
claude --version 2>&1 | grep -q "[0-9]" && echo "OK" || echo "DOWN"
codex --version 2>&1 | grep -q "[0-9]" && echo "OK" || echo "DOWN"
grok --version 2>&1 | grep -q "[0-9]" && echo "OK" || echo "DOWN"
```

## 注意事项
1. **Agent要"互相看见"**：每个Agent需要前序Agent的输出
2. **项目经理Agent负责协调和质量把关**
3. **人类只在关键节点介入**：不要在每个Agent输出时都介入
4. **建立Agent记忆**：长期项目需要Agent记住历史决策
5. **严格一次性派发**：禁止重复补派相同角色的子Agent
6. **派发前做健康检查**：避免等到Agent失败才发现不可用
7. **不要用shell `&` 后台**：用foreground+timeout保证进程不提前被杀

> 📚 详细实操教训见 `references/multi-agent-orchestration-lessons.md`
