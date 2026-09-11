# AI 客户线索研究与方案决策 Agent

这是一个面向 AI 服务团队的客户线索研究工作流。它接收企业名称、已表达需求和我方可交付能力，自动完成公开资料检索、资料筛选、机会判断、Agent 方案生成和证据审核，最后把报告与跟进任务草稿保存到本地 SQLite。任何外部写操作都停在人工批准之前。

## 这个二次开发项目做了什么

项目基于 [guy-hartstein/company-research-agent](https://github.com/guy-hartstein/company-research-agent)，保留了原项目的多节点调研结构，并完成了面向客户线索场景的改造：

- 使用阿里云百炼 DashScope 的 OpenAI 兼容接口调用通义千问；Tavily 负责网页搜索和正文抽取。
- 增加客户需求、我方能力、痛点、证据、Agent 方案和五项商机评分的结构化数据模型。
- 增加证据质量门：引用不是检索结果中的真实 URL，或引用覆盖率不足时，自动退回方案分析节点修订一次。
- 增加 SQLite 落库，保存客户线索、报告、评分、质量审核结果和任务草稿。
- 增加人工审批边界：系统只能生成本地任务草稿，批准前不会调用外部写 API，也不会伪造飞书同步成功。
- 前端增加评分、痛点证据、推荐方案和任务审批面板。

上游项目和本项目改造边界必须在简历或 GitHub 说明中保留，不能把开源代码直接当成原创项目。

## Windows 本地运行

要求：Python 3.11+、Node.js 18+。首次安装依赖：

```powershell
cd C:\Users\陈仕涛\Documents\Codex\2026-09-10\5\outputs\ai-lead-research-agent
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ui
npm install
```

在项目根目录复制 `.env.example` 为 `.env`，填写自己的 Key。不要把 `.env` 提交到 GitHub：

```env
DASHSCOPE_API_KEY=你的百炼APIKey
TAVILY_API_KEY=你的TavilyKey
DASHSCOPE_RESEARCH_MODEL=qwen-plus
DASHSCOPE_BRIEFING_MODEL=qwen-plus
DASHSCOPE_REPORT_MODEL=qwen-plus
```

启动两个终端：

终端一：

```powershell
cd C:\Users\陈仕涛\Documents\Codex\2026-09-10\5\outputs\ai-lead-research-agent
.\.venv\Scripts\python.exe -m uvicorn application:app --reload --port 8000
```

终端二：

```powershell
cd C:\Users\陈仕涛\Documents\Codex\2026-09-10\5\outputs\ai-lead-research-agent\ui
npm run dev
```

浏览器打开 `http://localhost:5173`。在表单里填写企业、需求和我方能力，完成后先看引用和评分，再点击“生成跟进任务草稿”，最后人工批准本地待办。

## API

- `POST /research`：创建异步调研任务。
- `GET /research/{job_id}/stream`：接收 SSE 进度和最终报告。
- `GET /leads`、`GET /leads/{lead_id}`：查看本地线索和审核记录。
- `POST /leads/{lead_id}/task-drafts`：从推荐方案生成任务草稿。
- `POST /task-drafts/{task_id}/approve`：人工批准本地任务。

## 评测与投递前检查

项目提供 30 条脱敏样本于 `eval/samples.jsonl`，运行：

```powershell
.\.venv\Scripts\python.exe scripts/run_eval.py
```

该脚本只检查输入覆盖和结构化结果约束，不会伪造模型效果。投递前应使用自己的 Key 跑至少 3 个真实案例，并记录结构完整率、引用有效率、工具调用成功率、失败重试次数、平均耗时和模型成本。当前自动化测试与前端构建均已通过，但真实 API 指标需要你在本地运行后再填写。

## 面试讲法

可以按“检索规划 → 并行搜索 → 资料治理 → 机会分析 → 证据质量门 → 人工审批”的链路讲。重点说明：模型负责需要判断的任务，代码负责评分、URL 白名单校验、SQLite 落库和审批状态机；这样既有 Agent 的动态决策，也有可追溯和安全边界。
