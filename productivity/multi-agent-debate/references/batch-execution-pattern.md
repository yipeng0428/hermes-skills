# Batch Execution Pattern

> Proven pattern for running N parallel sub-agents, collecting outputs, and converting to deliverables.
> Reverse-engineered from 2026-07-15 session that produced 12 production-ready skills in one pass.

## When to Use

- User asks for "research X, then create skills"
- Multiple independent search/analysis tasks
- Need to synthesize many findings into one report + many deliverables

## The 6-Step Pattern

### Step 1: Decompose
Break the big ask into 3-5 parallel sub-tasks. Each sub-task should be independent and answer a different angle.

```
Big ask: "Research frontier work modes and create skills"
├─ Sub-agent A: Search real commercial cases
├─ Sub-agent B: Search frontier workflow models
└─ Sub-agent C: Search advanced AI collaboration paradigms
```

### Step 2: Execute (parallel)
```python
delegate_task(
  tasks=[
    {goal: "Search real cases...", context: "..."},
    {goal: "Search workflow models...", context: "..."},
    {goal: "Search AI collaboration paradigms...", context: "..."}
  ],
  enabled_toolsets: ["web", "terminal", "file"]
)
```

### Step 3: Collect
Save each sub-agent's output to a local file:
```
E:/hermes/output/{date}_{topic}_raw.md
```

### Step 4: Synthesize
Merge all findings into a single 终审报告 with:
- 铁律共识 (100% agreed directions)
- Core disagreements + system rulings
- Prioritized roadmap
- Counterfactual pre-analysis

### Step 5: Convert to Skills
For each distinct finding that is a "class of work" (not a one-off):
1. `skill_manage(action="create", name="class-level-name", content="...")`
2. Include: 何时不该用 + 快速上手 + 真实案例 + 验证清单 + 联动说明

### Step 6: Verify
- `skills_list()` confirms all registered
- `skill_view()` spot-checks content quality
- Cross-skill联动 links are bidirectional

## Quality Checklist for Each Skill
- [ ] 何时不该用 table (when NOT to use)
- [ ] 快速上手 (≤3 minute start)
- [ ] 真实案例 (real example)
- [ ] 验证清单 (verification checklist)
- [ ] 联动说明 (links to related skills)
- [ ] Class-level name (not session-specific)

## Pitfall: execute_code on Windows
`execute_code` is blocked on Windows (runs arbitrary Python). Use `write_file` + `terminal` instead for batch file operations.

## Pitfall: skill_manage create when exists
If skill already exists, use `skill_manage(action="edit", ...)` or `skill_manage(action="patch", ...)`.

---

*Last updated: 2026-07-15*
