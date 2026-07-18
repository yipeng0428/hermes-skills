# Companion Skills Map

> These skills extend `multi-agent-debate` with concrete proven execution patterns.
> Each was reverse-engineered from real commercial/arXiv case studies in 2026-07-15 session.

## The Ecosystem

```
                    ┌──────────────────────┐
                    │  multi-agent-debate  │
                    │  (root analysis +    │
                    │   execute framework) │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐         ┌─────▼──────┐         ┌─────▼─────┐
   │ ANALYSIS │         │  EXECUTION │         │  HYBRID   │
   │ enhancers│         │  patterns  │         │ (both)    │
   └────┬─────┘         └─────┬──────┘         └─────┬─────┘
        │                     │                      │
   ┌────▼────────────────┐ ┌──▼───────────────────┐ ┌▼────────────────────┐
   │ allocation-economy  │ │ design-agent-team    │ │ flow-state-engineering│
   │ mixture-of-agents   │ │ multi-agent-swarm    │ │ 90-30-deep-work       │
   │ consilium-protocol  │ │ grade-routing        │ │ agentomics            │
   │                     │ │ budgeted-act-defer   │ │ cognitive-externalization│
   │                     │ │ sdof-framework       │ │                       │
   └─────────────────────┘ └──────────────────────┘ └───────────────────────┘
```

## When to Use Each Companion

| If you need... | Reach for... | Root idea |
|---|---|---|
| Many versions curated by human | `allocation-economy` | Maker → Manager |
| Enter flow state fast | `flow-state-engineering` | AI pre-flow priming |
| Right model for right price | `agentomics` | Shapley-value routing |
| External knowledge structure | `cognitive-externalization-loop` | AI-maintained knowledge graph |
| Deep work with AI orchestration | `90-30-deep-work` | T-15 / T+90 / T+15 protocol |
| Parallel specialized agents | `multi-agent-swarm` | Human as CEO |
| Layered refinement | `mixture-of-agents` | Each layer refines last |
| Multi-viewpoint deliberation | `consilium-protocol` | Cognitive persona engineering |
| Auto model routing | `grade-routing` | 4-gate adaptive budget |
| Automation with reliability | `budgeted-act-or-defer` | Error-budget control |
| Strict process enforcement | `sdof-framework` | Constraint state machine |
| End-to-end design workflow | `design-agent-team` | 6-role creative team |

## Batch Execution Pattern (proven 2026-07-15)

When user asks for "research → create skills" at scale:

1. **Decompose** into N parallel search tasks (3 sub-agents works well)
2. **Run Execute framework** with `delegate_task`, each sub-agent getting `enabled_toolsets: ["web", "terminal", "file"]`
3. **Collect** all outputs into local `.md` files under `E:/hermes/output/`
4. **Synthesize** 终审报告 combining all findings
5. **Convert** each finding into a class-level skill using `skill_manage(action="create")`
6. **Enrich** every skill with: 何时不该用 + 快速上手 + 真实案例 + 验证清单 + 联动说明

That 6-step pattern produced 12 production-ready skills in one session.

## Routing Decision Tree

```
                      ┌─ Need deep analysis?
                      │   ├─ Yes → multi-agent-debate (analysis)
                      │   └─ No ──┐
                      │           │
                      ├─ Need execution?
                      │   ├─ Yes ──┐
                      │   │        ├─ Research/collect → multi-agent-swarm
                      │   │        │   + design-agent-team (if design-focused)
                      │   │        ├─ One artifact, max quality → mixture-of-agents
                      │   │        ├─ Structured process → sdof-framework
                      │   │        └─ Budget-constrained → grade-routing
                      │   │
                      │   └─ No ──┐
                      │           │
                      ├─ Need decision support?
                      │   ├─ Yes → consilium-protocol (multi-viewpoint deliberation)
                      │   └─ No ──┐
                      │           │
                      └─ Need personal workflow?
                          ├─ Focus → flow-state-engineering
                          ├─ Knowledge → cognitive-externalization-loop
                          ├─ Output batch → allocation-economy
                          ├─ Schedule → 90-30-deep-work
                          └─ Cost routing → agentomics
```

---

*Last updated: 2026-07-15 — reverse-engineered from real commercial cases + arXiv papers.*
