# prompt-structure

一句话提示词与四要素结构化提示词的对照实验：同一批 20 条真实任务、同一模型，只换提示词，看「可直接使用」的通过率。

## 结论

| 组 | 提示词写法 | 内容通过 |
|---|---|---|
| baseline | 只给任务与输出字段 | 7/20 |
| structured | 角色 / 任务 / 背景 / 限制四要素 | 14/20 |

代价：指令部分涨 4.5 倍，但整体提示词只涨 1.64 倍，总 token 涨 13%——输出被字数约束压短，抵掉了多半成本。

边界：主指标是规则代理判分，不是人工评审；单模型单次采样，延迟数字没有统计意义。

## 安装

```bash
pip install -r requirements.txt
copy .env.example .env      # 非 Windows 用 cp
```

`.env` 填 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL` 三项，任何 OpenAI 兼容端点都可以。

## 怎么跑

```bash
python src/selfcheck.py                 # 不联网自检，11 项
python src/experiment.py                # 全量 20 题两组
python src/experiment.py --ids S1,C1    # 抽查
python src/experiment.py --arms structured
```

模型读 `.env`；命令行 `--model/--base-url/--api-key` 可覆盖。做对照实验必须固定单条模型，不要用带负载均衡的路由组。

## 目录

| 路径 | 内容 |
|---|---|
| `src/templates.py` | 四要素模板与两套 prompt 组装，变量缺失直接报错 |
| `src/runner.py` | 一次流式调用，记首字延迟与 token |
| `src/grade.py` | JSON 合法性、内容规则、字数上限、百分比编造 |
| `src/experiment.py` | 两组入口，产出 `runs/<时间戳>/` |
| `data/tasks.jsonl` | 20 条任务，摘要润色 / 代码审查 / 报错定位 / 简历改写各 5 条 |
| `runs/20261109-final/` | 主实验结果与报告 |

设计与判断见 `过程文档.md`。
