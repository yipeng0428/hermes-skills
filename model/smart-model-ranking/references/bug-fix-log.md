# Smart Model Ranking - Integration Bug Log (2026-07-13)

All bugs hit during real-session testing. Useful when re-loading the skill.

## Bug #1 — `display_index` KeyError

**Symptom:** `format_model_list()` raised `KeyError: 'display_index'` because `sort_models()` returned raw model dicts for `get_sorted_models()` but the `format_model_list()` method expected a `display_index` key that only existed in the `sort_models()` local `formatted_models` variable.

**Root cause:** `get_sorted_models()` stripped down scored output by doing `result = [m["model"]` which lost the `display_index` and `reason` fields.

**Fix:** In `format_model_list()` — use `enumerate(sorted_models, 1)` and `enumerate(sorted_models[top_n:], top_n+1)` to derive indices instead of reading `display_index`.

## Bug #2 — `reason` KeyError

**Symptom:** `model_info['reason']` raised `KeyError: 'reason'` when `format_model_list()` was called by `HermesModelSelector.format_model_list_output()` with objects returned from `get_sorted_models()`.

**Root cause:** `get_sorted_models()` returned only `{"name": ..., "provider": ..., "model": ..., "key": ...}` — the `reason` field was dropped during the sort+filter step.

**Fix:** Either:
- Option A: Include `reason` in `get_sorted_models()` output (recommended)
- Option B: In `HermesModelSelector.format_model_list_output()`, pre-fill `"reason"` key with empty string before calling `ranker.format_model_list()` (used as a quick fix)

## Bug #3 — `model.get('name', ...)` AttributeError

**Symptom:** `format_model_list()` attempted `model.get('name', '未知模型')` but `model` was a string (the model key), not a dict.

**Root cause:** Same cascade from Bug #1 — `get_sorted_models()` returned strings instead of the wrapper dict.

**Fix:** In `format_model_list()`, unsafely access model fields. Use:
```python
if isinstance(model, dict):
    model_name = model.get('name', '未知模型')
else:
    model_name = str(model)
```

This defensive pattern should be the standard when processing input to any formatting function.

## Correct flow for next session

Currently three scripts interlink. If any of them is rewritten:

1. `ModelUsageLogger` — pure data layer. Self-contained, just tracks runs.
2. `SmartModelRanker` — pure logic. Accepts any list and returns scored+reason+display_index wrapped objects.
3. `HermesModelSelector` — thin glue that calls #2 and #3, loads config, and handles `format_model_list_output`.

The invariant that MUST be maintained: **caller-level wrappers MUST preserve `reason` and `display_index` through the function chain, OR format functions must defensively re-derive these from the original list.**
