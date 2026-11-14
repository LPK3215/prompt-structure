# Prompt 结构 · 两组对照报告 20261109-final

> 模型：`agnes-3.0-flash`　｜　入口：`https://apihub.agnes-ai.com/v1`　｜　Python 3.12.16
> 任务：20 条　｜　分组：一句话（基线） / 四要素（增强）
> 判分：JSON 合法性 + 内容规则 + 字数上限，规则写在 data/tasks.jsonl 的 expect 里。

## 一、总表

| 指标 | 一句话（基线） | 四要素（增强） |
|---|---|---|
| 内容通过 | 7 | 14 |
| 内容通过率 | 0.35 | 0.7 |
| JSON 合法 | 12 | 19 |
| JSON 合法率 | 0.6 | 0.95 |
| 平均字数 | 118 | 98 |
| 超长题数 | 5 | 2 |
| 平均提示词字数 | 309 | 507 |
| 平均输入 token | 226 | 352 |
| 平均输出 token | 164 | 89 |
| 平均首字延迟 ms | 8322 | 15206 |
| 平均总时延 ms | 11176 | 16477 |

## 二、分类型通过率

| 类型 | 一句话（基线） | 四要素（增强） |
|---|---|---|
| code_review | 3/5 | 1/5 |
| error_debug | 1/5 | 5/5 |
| resume | 2/5 | 5/5 |
| summarize | 1/5 | 3/5 |

## 三、逐题

| 题 | 类型 | 分组 | 内容 | JSON | 字数 | 时延 ms | 失败原因 |
|---|---|---|---|---|---|---|---|
| S1 | summarize | baseline | 未过 | 不合法 | 133 | 25398 | JSON 不合法或字段缺失 |
| S2 | summarize | baseline | 未过 | 不合法 | - | 4528 | JSON 不合法或字段缺失 |
| S3 | summarize | baseline | 通过 | 合法 | 95 | 7463 |  |
| S4 | summarize | baseline | 未过 | 不合法 | 152 | 5622 | JSON 不合法或字段缺失；缺 12%；超长 152>150 |
| S5 | summarize | baseline | 未过 | 合法 | 159 | 4680 | 超长 159>150 |
| C1 | code_review | baseline | 未过 | 不合法 | - | 37041 | JSON 不合法或字段缺失 |
| C2 | code_review | baseline | 通过 | 合法 | - | 9937 |  |
| C3 | code_review | baseline | 未过 | 合法 | - | 7206 | 未出现 exists/序号/循环/counter/suffix |
| C4 | code_review | baseline | 通过 | 合法 | - | 6066 |  |
| C5 | code_review | baseline | 通过 | 合法 | - | 3718 |  |
| E1 | error_debug | baseline | 未过 | 合法 | 125 | 5093 | 超长 125>120 |
| E2 | error_debug | baseline | 通过 | 合法 | 60 | 3633 |  |
| E3 | error_debug | baseline | 未过 | 不合法 | - | 8694 | JSON 不合法或字段缺失；未出现 python3 -m pip install/同一个解释器/which python/venv/虚拟环境 |
| E4 | error_debug | baseline | 未过 | 不合法 | - | 3416 | JSON 不合法或字段缺失 |
| E5 | error_debug | baseline | 未过 | 不合法 | - | 3712 | JSON 不合法或字段缺失 |
| R1 | resume | baseline | 通过 | 合法 | 94 | 18081 |  |
| R2 | resume | baseline | 未过 | 合法 | 125 | 2426 | 超长 125>100 |
| R3 | resume | baseline | 通过 | 合法 | 95 | 26317 |  |
| R4 | resume | baseline | 未过 | 合法 | 142 | 4676 | 超长 142>100 |
| R5 | resume | baseline | 未过 | 不合法 | - | 35821 | JSON 不合法或字段缺失 |
| S1 | summarize | structured | 未过 | 合法 | 312 | 6106 | 超长 312>300 |
| S2 | summarize | structured | 通过 | 合法 | 190 | 6594 |  |
| S3 | summarize | structured | 通过 | 合法 | 128 | 3864 |  |
| S4 | summarize | structured | 通过 | 合法 | 109 | 3812 |  |
| S5 | summarize | structured | 未过 | 合法 | 156 | 34358 | 超长 156>150 |
| C1 | code_review | structured | 未过 | 合法 | - | 21527 | 未出现 状态码/raise_for_status/404/HTTP 状态/status code/status_code/error page；未出现 raise_for_status/status_code/检查返回码/check the status |
| C2 | code_review | structured | 未过 | 不合法 | - | 30688 | JSON 不合法或字段缺失；未出现 非法字符/冒号/问号/Windows 文件名/特殊字符/illegal character/invalid character/filename/colon/reserved |
| C3 | code_review | structured | 未过 | 合法 | - | 3891 | 未出现 覆盖/同名/重名/已存在/overwrite/exist；未出现 exists/序号/循环/counter/suffix |
| C4 | code_review | structured | 未过 | 合法 | - | 2704 | 未出现 越界/上界/超出总页数/范围/out of range/bounds |
| C5 | code_review | structured | 通过 | 合法 | - | 19204 |  |
| E1 | error_debug | structured | 通过 | 合法 | 44 | 23476 |  |
| E2 | error_debug | structured | 通过 | 合法 | 58 | 10564 |  |
| E3 | error_debug | structured | 通过 | 合法 | 67 | 10097 |  |
| E4 | error_debug | structured | 通过 | 合法 | 57 | 60868 |  |
| E5 | error_debug | structured | 通过 | 合法 | 23 | 4380 |  |
| R1 | resume | structured | 通过 | 合法 | 56 | 14417 |  |
| R2 | resume | structured | 通过 | 合法 | 61 | 24868 |  |
| R3 | resume | structured | 通过 | 合法 | 53 | 4159 |  |
| R4 | resume | structured | 通过 | 合法 | 79 | 3079 |  |
| R5 | resume | structured | 通过 | 合法 | 79 | 40901 |  |

## 四、读表注意

- 两组任务与模型完全相同，唯一变量是提示词：基线只有一句任务加输出字段，增强补角色、背景、字数与禁止项。
- 内容通过率是「可直接使用」的规则代理，不是人工评审；规则口径逐题写在 tasks.jsonl。
- 字数按 JSON 里指定字段统计，JSON 不合法时无法统计，计为该题不通过。
