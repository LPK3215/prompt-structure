"""四要素模板与两套 prompt 组装。

模板变量缺失直接报错，不静默填空（总纲 8.2）。
"""

from __future__ import annotations

import re

STRUCTURED = """[角色] {role}
[任务] {task}
[背景] {background}
[限制]
{constraints}
[输出] 只输出 JSON，不要代码块；字段：{fields}

[输入]
{input}"""

TERSE = """{terse}

[输入]
{input}"""

VAR_RE = re.compile(r"{(\w+)}")


def check(tpl: str, values: dict) -> None:
    missing = set(VAR_RE.findall(tpl)) - set(values)
    if missing:
        raise KeyError(f"模板缺少变量：{', '.join(sorted(missing))}")


def build_structured(task: dict) -> str:
    values = {
        "role": task["role"],
        "task": task["task"],
        "background": task["background"],
        "constraints": "\n".join(f"{i} {c}" for i, c in enumerate(task["constraints"], 1)),
        "fields": task["fields"],
        "input": task["input"],
    }
    check(STRUCTURED, values)
    return STRUCTURED.format(**values)


def build_terse(task: dict) -> str:
    values = {"terse": task["terse"], "input": task["input"]}
    check(TERSE, values)
    return TERSE.format(**values)


def build(task: dict, arm: str) -> str:
    if arm == "baseline":
        return build_terse(task)
    if arm == "structured":
        return build_structured(task)
    raise ValueError(f"未知分组 {arm}")
