"""不联网自检：模板、判分、JSON 解析。

    python src/selfcheck.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from grade import extract, grade
from templates import build, build_structured, check

PASS: list[str] = []
FAIL: list[str] = []


def check_(name: str, cond: bool, detail: str = "") -> None:
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  <- {detail}" if not cond and detail else ""))


def main() -> None:
    task = json.loads((Path(__file__).resolve().parents[1] / "data" / "tasks.jsonl")
                      .read_text(encoding="utf-8").splitlines()[0])

    terse = build(task, "baseline")
    structured = build(task, "structured")
    check_("基线只有一句任务", terse.count("\n") <= 6 and "[角色]" not in terse, terse[:80])
    check_("增强含四要素", all(k in structured for k in ("[角色]", "[任务]", "[背景]", "[限制]", "[输出]")))
    check_("增强提示词更长", len(structured) > len(terse), f"{len(structured)} vs {len(terse)}")

    try:
        check(STRUCTURED_PLACEHOLDER := "[角色] {a}\n{missing}", {"a": "x"})
        check_("模板缺变量必须报错", False)
    except KeyError:
        check_("模板缺变量必须报错", True)

    check_("裸 JSON 可解析", extract('{"summary":"x","numbers":[]}') is not None)
    check_("代码块围栏不算合法", extract('```json\n{"summary":"x"}\n```') is None)
    check_("数组不算对象", extract('[1,2]') is None)

    ok_task = {"expect": {"char_field": "summary", "max_chars": 10, "all_of": ["0.9558"],
                          "any_of": [], "forbid_regex": "首先", "json_fields": ["summary", "numbers"]}}
    good = {"answer": '{"summary":"0.9558 是结果","numbers":["0.9558"]}'}
    g = grade(ok_task, good)
    check_("合规答案判通过", g["content_ok"] and g["json_ok"] and g["chars"] == 10, str(g))

    long_ans = {"answer": '{"summary":"0.9558  ' + "很" * 20 + '","numbers":[]}'}
    g = grade(ok_task, long_ans)
    check_("超长判不通过", not g["content_ok"] and "超长" in g["fail_reason"], g["fail_reason"])

    bad = {"answer": '{"summary":"没有数字","numbers":[]}'}
    g = grade(ok_task, bad)
    check_("缺关键内容判不通过", not g["content_ok"] and "缺" in g["fail_reason"], g["fail_reason"])

    forbid = {"answer": '{"summary":"0.9558 首先这样","numbers":[]}'}
    g = grade(ok_task, forbid)
    check_("命中禁止词判不通过", not g["content_ok"], g["fail_reason"])

    print(f"\n{len(PASS)} 通过 / {len(FAIL)} 失败")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
