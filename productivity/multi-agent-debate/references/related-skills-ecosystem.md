# 相关技能生态系统

> 本文档记录与 `multi-agent-debate`（群智模式）相关的完整技能家族。
> 按依赖深度从近到远排列，供 Agent 在选择技能组合时参考。

## 第一圈：群智模式直接衍生（2026-07-15 创建）

这些技能由群智模式研究流水线发现并自行创建，是群智模式的自然延伸：
- `allocation-economy` — 配称经济：AI 批量生成，人类策展。群智模式"分析后执行"的批量版本
- `multi-agent-swarm` — 多智能体群集编排：你当 CEO，管理 AI 团队
- `mixture-of-agents` — MoA 多层精炼：层层精炼，超越单模型
- `consilium-protocol` — BFT 认知审议：便宜模型 + 认知人设 ≈ 昂贵模型

## 第二圈：群智模式执行配套

- `design-agent-team` — 设计 Agent 团队：专为美工设计的 6 角色流水线，是 Execute 框架在设计领域的专项实现
- `grade-routing` — 门控路由：根据任务动态选模型和深度，是群智模式"多模型调用"的自动化版本
- `agentomics` — AI 代理经济学：按 Shapley 值计算各 Agent 贡献，实现成本最优分配
- `budgeted-act-defer` — 预算化决策：何时 AI 自己做 vs 升级人工，是群智模式的置信度基线

## 第三圈：群智模式状态支撑

- `flow-state-engineering` — 心流工程：2 分钟进入 Flow，群智模式分析前先破题用
- `90-30-deep-work` — 超频协议：AI 预热 → 执行 → 整理三段式，适合群智模式分析后的深度产出期
- `cognitive-externalization-loop` — 认知外化循环：群智模式产出存入知识图谱，AI 自动关联
- `sdof-framework` — 状态约束分派：群智模式的"流程约束版"，适合有严格阶段要求的企业场景

## 第四圈：外部技能联动

- `web-search` — 群智模式中 RESEARCHER Agent 的底层搜索引擎配置
- `notion` — 群智模式产出备份到 Notion 的通道
- `hermes-config-providers` — 多模型回退链配置（群智模式依赖多模型可用性）
- `notion-governance-os` — 群智模式产出的 Notion 知识库持续治理

## 技能选择决策树

```
任务类型？
├─ 需要分析/决策 → multi-agent-debate（群智三模式）
│   ├─ + 需要交叉审查 → consilium-protocol
│   ├─ + 需要层层精炼 → mixture-of-agents
│   └─ + 需要成本最优 → agentomics
├─ 需要执行/产出 → design-agent-team（设计专项）/ multi-agent-swarm（通用）
│   ├─ + 需要动态路由 → grade-routing
│   └─ + 需要预算管控 → budgeted-act-defer
├─ 需要深度工作 → flow-state-engineering / 90-30-deep-work
└─ 需要知识积累 → cognitive-externalization-loop
```

## 真实组合案例

### 案例 1：万凯新品详情页（全程群智模式）
```
flow-state-engineering（破题预热）
  → multi-agent-debate（三模式分析：闪电+辩论+专家）
    → allocation-economy（基于终审报告批量生成10个方案）
      → design-agent-team（选定方向后深度执行）
        → cognitive-externalization-loop（成果存入知识库）
```

### 案例 2：月度竞品报告（低成本版本）
```
agentomics（按重要性分配模型预算）
  → multi-agent-swarm（RESEARCHER + ANALYST + CRITIC + SYNTHESIST）
    → consilium-protocol（对关键结论做 BFT 审议）
      → budgeted-act-defer（P3 级任务全自动，P2 抽样审计）
```

### 案例 3：系统自检修复（分析后执行桥梁）
```
multi-agent-debate（分析三模式）
  → 用户："去吧执行" 
    → 主Agent直接用 cronjob/terminal 工具操作（不派发子Agent）
      → 耗时 <3 分钟
```
