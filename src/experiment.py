"""两组对照入口：一句话提示词 vs 四要素结构化。

    python src/experiment.py                       # 全量 20 题，两组
    python src/experiment.py --ids S1,C1 --limit 5  # 抽查
    python src/experiment.py --arms structured      # 只跑一组
"""

from __future__ import annotations

import argparse
import json
import os
import platform
from datetime import datetime
from pathlib import Path

from config import DATA, RUNS, make_model
from grade import summarize
from runner import run_task


def load_tasks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="baseline,structured")
    ap.add_argument("--ids", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default="")
    ap.add_argument("--base-url", default="")
    ap.add_argument("--api-key", default="")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    if args.model:
        os.environ["OPENAI_MODEL"] = args.model
    if args.base_url:
        os.environ["OPENAI_BASE_URL"] = args.base_url
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key

    tasks = load_tasks(DATA / "tasks.jsonl")
    if args.ids:
        keep = {x.strip() for x in args.ids.split(",")}
        tasks = [t for t in tasks if t["id"] in keep]
    if args.limit:
        tasks = tasks[: args.limit]

    model = make_model()
    tag = args.tag or datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = RUNS / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for arm in [a.strip() for a in args.arms.split(",") if a.strip()]:
        for t in tasks:
            rec = run_task(t, arm, model)
            records.append(rec)
            print(f"[{arm:10s}] {t['id']:3s} {rec['latency_ms']:5d}ms "
                  f"in={rec['tokens_in']:4d} out={rec['tokens_out']:4d} "
                  f"ttft={rec['ttft_ms']} ans={len(rec['answer'])}")

    with (out_dir / "records.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    result = {
        "tag": tag,
        "model": model.model_name,
        "base_url": str(model.openai_api_base),
        "python": platform.python_version(),
        "tasks": len(tasks),
        "arms": [a.strip() for a in args.arms.split(",") if a.strip()],
        "metrics": summarize(records, tasks),
    }
    (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    print(f"\n-> {out_dir}")


def render_report(result: dict) -> str:
    m = result["metrics"]
    arms = list(m["overall"])
    label = {"baseline": "一句话（基线）", "structured": "四要素（增强）"}
    lines = [
        f"# Prompt 结构 · 两组对照报告 {result['tag']}",
        "",
        f"> 模型：`{result['model']}`　｜　入口：`{result['base_url']}`　｜　Python {result['python']}",
        f"> 任务：{result['tasks']} 条　｜　分组：{' / '.join(label.get(a, a) for a in arms)}",
        "> 判分：JSON 合法性 + 内容规则 + 字数上限，规则写在 data/tasks.jsonl 的 expect 里。",
        "",
        "## 一、总表",
        "",
        "| 指标 | " + " | ".join(label.get(a, a) for a in arms) + " |",
        "|---|" + "---|" * len(arms),
    ]
    rows = [("内容通过", "content_pass"), ("内容通过率", "content_rate"),
            ("JSON 合法", "json_ok"), ("JSON 合法率", "json_rate"),
            ("平均字数", "avg_chars"), ("超长题数", "over_tasks"),
            ("平均提示词字数", "avg_prompt_chars"),
            ("平均输入 token", "avg_tokens_in"), ("平均输出 token", "avg_tokens_out"),
            ("平均首字延迟 ms", "avg_ttft_ms"), ("平均总时延 ms", "avg_latency_ms")]
    for name, key in rows:
        lines.append(f"| {name} | " + " | ".join(str(m['overall'][a][key]) for a in arms) + " |")

    lines += ["", "## 二、分类型通过率", "", "| 类型 | " + " | ".join(label.get(a, a) for a in arms) + " |",
              "|---|" + "---|" * len(arms)]
    for t, sub in m["by_type"].items():
        cells = [f"{sub[a]['content_pass']}/{sub[a]['tasks']}" if a in sub else "-" for a in arms]
        lines.append(f"| {t} | " + " | ".join(cells) + " |")

    lines += ["", "## 三、逐题", "", "| 题 | 类型 | 分组 | 内容 | JSON | 字数 | 时延 ms | 失败原因 |",
              "|---|---|---|---|---|---|---|---|"]
    for row in m["tasks"]:
        lines.append(f"| {row['task_id']} | {row['type']} | {row['arm']} | "
                     f"{'通过' if row['content_ok'] else '未过'} | {'合法' if row['json_ok'] else '不合法'} | "
                     f"{row['chars'] if row['chars'] is not None else '-'} | {row['latency_ms']} | {row['reason']} |")

    lines += ["", "## 四、读表注意", "",
              "- 两组任务与模型完全相同，唯一变量是提示词：基线只有一句任务加输出字段，增强补角色、背景、字数与禁止项。",
              "- 内容通过率是「可直接使用」的规则代理，不是人工评审；规则口径逐题写在 tasks.jsonl。",
              "- 字数按 JSON 里指定字段统计，JSON 不合法时无法统计，计为该题不通过。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
