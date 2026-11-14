"""确定性判分：JSON 合法性 + 内容规则 + 长度。

主指标用规则判分代理「可直接使用」的人工通过率，规则口径写在 tasks.jsonl 的 expect 里。
"""

from __future__ import annotations

import json
import re
from statistics import mean


def extract(answer: str):
    """严格解析：带代码块围栏也算不合法。"""
    try:
        obj = json.loads(answer.strip())
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def grade(task: dict, record: dict) -> dict:
    exp = task["expect"]
    answer = record.get("answer") or ""
    obj = extract(answer)
    fields = exp.get("json_fields") or []
    types = exp.get("json_types") or {}
    json_ok = bool(obj) and all(f in obj for f in fields) and all(
        isinstance(obj.get(f), {"array": list, "string": str, "integer": int}.get(want))
        for f, want in types.items() if obj and f in obj
    )

    chars = None
    target = exp.get("char_field")
    if obj and target and isinstance(obj.get(target), str):
        chars = len(obj[target])

    reasons = []
    if not json_ok:
        reasons.append("JSON 不合法或字段缺失")

    text = answer.lower()
    for s in exp.get("all_of", []):
        if s.lower() not in text:
            reasons.append(f"缺 {s}")
    for group in exp.get("any_of", []):
        if not any(s.lower() in text for s in group):
            reasons.append("未出现 " + "/".join(group))
    rx = exp.get("forbid_regex")
    if rx:
        scope = obj.get(target) if (obj and target and isinstance(obj.get(target), str)) else answer
        if re.search(rx, scope or ""):
            reasons.append(f"命中禁止 {rx}")
    if exp.get("pct_check"):
        src = set(re.findall(r"\d+(?:\.\d+)?%", task["input"]))
        got = set(re.findall(r"\d+(?:\.\d+)?%", answer))
        extra = got - src
        if extra:
            reasons.append("编造百分比 " + "、".join(sorted(extra)))
    if exp.get("max_chars") and chars is not None and chars > exp["max_chars"]:
        reasons.append(f"超长 {chars}>{exp['max_chars']}")

    content_ok = not reasons
    over = None
    if chars is not None and exp.get("max_chars"):
        over = max(0, chars - exp["max_chars"])
    return {"json_ok": json_ok, "content_ok": content_ok, "chars": chars, "over_chars": over,
            "fail_reason": "；".join(reasons)}


def summarize(records: list[dict], tasks: list[dict]) -> dict:
    by_id = {t["id"]: t for t in tasks}
    for r in records:
        g = grade(by_id[r["task_id"]], r)
        r.update(g)

    def block(rs: list[dict]) -> dict:
        ok = sum(1 for r in rs if r["content_ok"])
        json_ok = sum(1 for r in rs if r["json_ok"])
        chars = [r["chars"] for r in rs if r["chars"] is not None]
        return {
            "tasks": len(rs),
            "content_pass": ok,
            "content_rate": round(ok / len(rs), 3) if rs else 0.0,
            "json_ok": json_ok,
            "json_rate": round(json_ok / len(rs), 3) if rs else 0.0,
            "avg_chars": int(mean(chars)) if chars else 0,
            "over_tasks": sum(1 for r in rs if (r["over_chars"] or 0) > 0),
            "avg_tokens_in": int(mean([r["tokens_in"] for r in rs])) if rs else 0,
            "avg_tokens_out": int(mean([r["tokens_out"] for r in rs])) if rs else 0,
            "avg_prompt_chars": int(mean([r["prompt_chars"] for r in rs])) if rs else 0,
            "avg_ttft_ms": int(mean([r["ttft_ms"] for r in rs if r["ttft_ms"]]))
            if any(r["ttft_ms"] for r in rs) else 0,
            "avg_latency_ms": int(mean([r["latency_ms"] for r in rs])) if rs else 0,
        }

    out = {"overall": {}, "by_type": {}, "tasks": []}
    for arm in sorted({r["arm"] for r in records}):
        rs = [r for r in records if r["arm"] == arm]
        out["overall"][arm] = block(rs)
        for t in sorted({r["type"] for r in rs}):
            sub = [r for r in rs if r["type"] == t]
            out["by_type"].setdefault(t, {})[arm] = block(sub)
    for r in records:
        out["tasks"].append({
            "task_id": r["task_id"], "type": r["type"], "arm": r["arm"],
            "content_ok": r["content_ok"], "json_ok": r["json_ok"], "chars": r["chars"],
            "latency_ms": r["latency_ms"], "ttft_ms": r["ttft_ms"],
            "tokens": [r["tokens_in"], r["tokens_out"]],
            "reason": r["fail_reason"], "answer": (r["answer"] or "")[:200],
        })
    return out
