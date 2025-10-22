# BaseModel Agent - Restack-Native Implementation — **Restack-native BaseModel Agent** (from scratch, Python) that feels first-class in Restack instead of a port. Below is a **battle-tested plan** you can build against. I’ll cover goals, responsibilities, state & memory, planning, tool execution, safety, observability, events/interfaces, directory layout, and a phased roadmap.



> **Status**: ✅ **MVP v0.1.0 Complete** - All tests passing, service running successfully  ---

> **Last Updated**: October 22, 2025

# Goals (what this basemodel must guarantee)

A production-ready, event-driven AI agent built natively for the Restack framework. This agent provides a robust foundation for autonomous task execution with planning, memory management, tool execution, and observability.

1. **Agent-as-brain**: long-lived, event-driven orchestrator (`@agent.defn`) with clear state, deterministic run loop, and resumability.

---2. **Planning runtime**: a lightweight, pluggable planning engine (periodic or on-demand) that decides which steps/workflows to run next.

3. **Tool layer**: functions (`@function.defn`) as atomic tools; workflows (`@workflow.defn`) for multi-step jobs; clean contracts between layers.

## 🚀 Quick Start4. **Memory model**: durable, inspectable history with **automatic compaction** (budgeted by chars/tokens), and simple persistence hooks.

5. **Safety & governance**: guardrails for tools (validation, rate limiting, timeouts) and a restricted “code/execution” story.

```bash6. **Observability**: consistent structured logs, metrics, run context, and replayability.

# Prerequisites: Docker Desktop running with Restack engine7. **Config-first**: declarative Pydantic config; DI hooks for models/tools; zero hidden global state.

# docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main8. **Failure resilience**: retries/backoff, idempotence, and graceful recovery.



# Terminal 1: Start the agent serviceNon-goals: reimplementing a full agent framework; heavy DSLs; hidden implicit behavior.

python src/service.py

---

# Terminal 2: Schedule a task

python src/schedule.py# Core responsibilities of the basemodel



# Monitor execution at http://localhost:5233* **State keeper**: holds the “world state” (task queue, plan, memory, artifacts).

```* **Event router**: translates incoming events into state transitions and actions.

* **Planner**: picks the next step(s); can be scripted or model-driven.

---* **Dispatcher**: calls functions/workflows via `agent.step(...)` / `agent.child_execute(...)`.

* **Historian**: logs steps, observations, decisions; compacts when budget exceeded.

## 📊 Current Status (v0.1.0)* **Persistence**: save/load memory & snapshots via function calls (I/O outside the agent process).



### ✅ Completed Features---



**Core Agent**# Architecture (native Restack)

- ✅ Event-driven orchestrator with `@agent.defn`, `@agent.run`, `@agent.event`

- ✅ Heuristic planning engine with dependency resolution* **Agent (brain)**: `BaseModelAgent` with `@agent.defn`. Methods:

- ✅ Memory compaction with character budget (default 100K chars)

- ✅ Snapshot persistence (save/load via functions)  * `@agent.event` handlers: `configure`, `enqueue_task`, `inject_memory`, `shutdown`, optional `set_plan`.

- ✅ Null-safe configuration handling  * `@agent.run` loop: waits for work → plans → dispatches → persists → compacts → repeats.

- ✅ Tool allow-list validation* **Workflows (plans/missions)**: e.g., `ResearchWorkflow`, `DocPipelineWorkflow`, customizable; long-running, resumable.

- ✅ Continue-as-new pattern for long-running agents* **Functions (tools)**: atomic skills (search, summarize, run_experiment, compile_pdf, memory_io, memory_compactor, token_count).



**Functions (8 tools)****Design tenet**: Agents **decide**; workflows **execute**; functions **do**.

- ✅ `search_papers` - Research paper discovery

- ✅ `generate_ideas` - Idea generation from research---

- ✅ `refine_ideas` - Iterative idea refinement

- ✅ `run_experiment` - Simulated experiment execution# State & memory

- ✅ `collect_results` - Results aggregation

- ✅ `compile_writeup` - Document compilation**State fields (agent instance):**

- ✅ `reviewer` - Quality review and feedback

- ✅ `memory_compactor` - History summarization* `cfg`: configuration (Pydantic model)

* `inbox`: list/queue of pending tasks (typed)

**Workflows (2 pipelines)*** `plan`: latest plan object (typed, versioned)

- ✅ `ResearchWorkflow` - Multi-step research pipeline (search → generate → refine)* `history`: list of `HistoryEntry` (decision, step, observation, error)

- ✅ `DocPipelineWorkflow` - Document generation pipeline (collect → compile → review)* `artifacts`: dict of named artifacts (paths, IDs, hashes)

* `cursors`: per-workflow cursors / last step

**Quality & Testing*** `stats`: counters (steps, retries, last_compaction)

- ✅ Full test suite (6/6 tests passing)* `shutdown`: bool

- ✅ Pydantic v2 data models with validation

- ✅ Structured logging and history tracking**Memory compaction strategy:**

- ✅ All Restack conventions properly applied (see `RESTACK_CONVENTIONS.md`)

* Trigger when `estimated_tokens(history)` or `len(json.dumps(history))` exceeds `cfg.memory_budget`.

---* Use a **MemoryCompactor** function:



## 📁 Project Structure  * Keep last `cfg.keep_last` entries verbatim.

  * Summarize older entries (extractive and/or LLM summarizer).

```  * Replace `history = [<SUMMARY>, ...tail]`.

basemodelagent/* Optional **artifact-aware** compaction: preserve references, convert blobs to pointers.

├── src/

│   ├── agents/**Persistence:**

│   │   └── basemodel_agent.py      # Core agent orchestrator

│   ├── workflows/* Implement `save_snapshot()` / `load_snapshot()` as **functions** (I/O outside agent).

│   │   ├── research_workflow.py    # Research pipeline* Snapshot includes `cfg`, `plan`, `history`, `artifacts`, `cursors`, `stats`.

│   │   └── doc_pipeline_workflow.py # Document pipeline

│   ├── functions/---

│   │   ├── memory_io.py            # Snapshot persistence

│   │   ├── memory_compactor.py     # History compaction# Planning engine (pluggable)

│   │   ├── token_count.py          # Token estimation

│   │   └── tools/* **Cadence**: run on each task, or every `cfg.planning_interval` steps, or when certain signals fire (error, drift).

│   │       ├── search_papers.py* **Modes**:

│   │       ├── generate_ideas.py

│   │       ├── refine_ideas.py  * **Scripted**: static DAG/sequence chosen by plan rule.

│   │       ├── run_experiment.py  * **Heuristic**: simple rules (if no ideas → search; if results → write; else → review).

│   │       ├── collect_results.py  * **Model-driven**: call a planner function (LLM/tool) to output next step(s).

│   │       ├── compile_writeup.py* **Output**: a `Plan` object with an ordered list of `PlanStep(name, inputs, retry_policy, parallel_group?)`.

│   │       └── reviewer.py

│   ├── models/**Dispatching**:

│   │   ├── config.py               # BaseModelConfig

│   │   ├── task.py                 # Task model* Sequential steps → `await agent.step(function=..., function_input=...)`.

│   │   ├── plan.py                 # Plan & PlanStep* Multi-step heavy chains → `await agent.child_execute(workflow=..., workflow_input=...)`.

│   │   ├── history.py              # HistoryEntry* Parallel groups → launch multiple `step(...)` calls and join (inside a workflow, not agent).

│   │   └── artifact.py             # Artifact model

│   ├── service.py                  # Service registration---

│   └── schedule.py                 # Task scheduler

├── tests/# Tool execution layer

│   └── test_models.py              # Model validation tests

├── examples/* **Functions**: small, typed, idempotent where possible; built-in retries & timeouts.

│   └── custom_task.py              # Custom task example* **Validation**: Pydantic schemas for inputs/outputs; reject dangerous patterns (esp. code).

├── snapshots/                       # Persisted agent state* **Policies**: rate limits, concurrency queues (e.g., “openai”, “io”, “compute”), budget counters per run.

├── RESTACK_CONVENTIONS.md          # Framework patterns reference* **Catalog**: a registry mapping tool names → function objects, enforced by the plan.

├── README.md                       # User documentation

└── pyproject.toml                  # Dependencies---

```

# Safety & governance

---

* **Code execution**: avoid raw code path by default. If required, route through a **sandbox** function (deny-lists, container/WASM, hard timeouts).

## 🎯 Design Philosophy* **Data boundaries**: sanitize inputs/outputs, redact secrets in logs.

* **Plan-time checks**: require an allow-list per plan step; block unknown tool names.

### Goals (What This Agent Guarantees)* **Failure policies**: per step retry w/ exponential backoff; mark non-retryable errors.



1. **Agent-as-brain**: Long-lived, event-driven orchestrator with clear state, deterministic run loop, and resumability---

2. **Planning runtime**: Lightweight, pluggable planning engine (heuristic in v0.1, model-driven coming in v0.3)

3. **Tool layer**: Functions as atomic tools; workflows for multi-step jobs; clean contracts between layers# Observability & run hygiene

4. **Memory model**: Durable, inspectable history with automatic compaction (budgeted by chars/tokens)

5. **Safety & governance**: Tool validation, rate limiting, timeouts, and controlled execution* **Structured logs**: every decision/step gets a `HistoryEntry` with:

6. **Observability**: Structured logs, metrics, run context, and replayability

7. **Config-first**: Declarative Pydantic config; DI hooks for models/tools; zero hidden global state  * `ts`, `kind` (`plan|step|obs|error|meta`), `name`, `inputs_digest`, `result_digest`, `latency_ms`, `retries`, `tags`.

8. **Failure resilience**: Retries/backoff, idempotence, and graceful recovery* **Metrics**: counters (success/fail), histograms (latency), gauges (queue depth, token usage).

* **Replay**: history is serializable and compacted; supports inspection and “resume from”.

**Non-goals**: Reimplementing a full agent framework; heavy DSLs; hidden implicit behavior

---

---

# Configuration & DI

## 🏗️ Architecture

* **Config model** (`BaseModelConfig`):

### Core Responsibilities

  * identity: `agent_name`, `workspace_dir`

- **State keeper**: Holds the "world state" (task queue, plan, memory, artifacts)  * planning: `planning_interval`, `planner_mode`

- **Event router**: Translates incoming events into state transitions and actions  * memory: `memory_budget_chars/tokens`, `keep_last`, `safety_margin`

- **Planner**: Picks the next step(s); can be scripted or model-driven  * tool policy: `allowed_tools`, queues, timeouts

- **Dispatcher**: Calls functions/workflows via `agent.step(...)` / `agent.child_execute(...)`  * persistence: snapshot path, period

- **Historian**: Logs steps, observations, decisions; compacts when budget exceeded* **Dependency injection**:

- **Persistence**: Save/load memory & snapshots via function calls (I/O outside the agent process)

  * Pass tool registries and model clients through config or constructor events.

### Design Tenet  * No global singletons.



> **Agents decide; workflows execute; functions do.**---



### State & Memory# Error handling & resilience



**Agent instance state:*** **Failure taxonomy**: `ValidationError`, `ToolFailure(retryable: bool)`, `PlanError`, `PersistenceError`.

```python* **Retries**: only on retryable failures; bounded attempts; record in history.

self.cfg              # BaseModelConfig (Pydantic)* **Circuit breakers**: if repeated tool failures, pause or replan.

self.inbox            # List of pending tasks* **Idempotence**: whenever a step creates external side effects, require idempotent keys.

self.plan             # Current plan object

self.history          # List of HistoryEntry objects---

self.artifacts        # Dict of named artifacts

self.cursors          # Per-workflow cursors# Events & interfaces

self.stats            # Counters (steps, retries, last_compaction)

self.shutdown_flag    # Shutdown signal**Inbound events** (all `@agent.event`):

```

* `configure(cfg: BaseModelConfig)`

**Memory compaction strategy:*** `enqueue_task(task: Task)` — tasks can be typed: `ResearchTask`, `WriteupTask`, etc.

- Triggers when `len(json.dumps(history))` exceeds `cfg.memory_budget_chars` (default: 100K)* `inject_memory(frames: list[HistoryEntry] | SnapshotRef)` — optional.

- Uses `memory_compactor` function to summarize older entries* `set_plan(plan: Plan)` — optional manual plan override.

- Keeps last `cfg.keep_last` entries verbatim (default: 5)* `shutdown()`

- Replaces history with `[<SUMMARY>, ...tail]`

**Outputs**:

**Persistence:**

- `save_snapshot()` / `load_snapshot()` implemented as functions* `@agent.run` returns last cycle’s status plus `last_result` or a summary of artifacts.

- Snapshots include: `cfg`, `plan`, `history`, `artifacts`, `cursors`, `stats`* Downstream systems should rely on **history & snapshot functions** for full detail.

- Stored as JSON in `snapshots/` directory

---

---

# Directory layout (clean & extensible)

## 🔧 Data Models (Pydantic v2)

```

### BaseModelConfigsrc/

```python  agents/

agent_name: str                                    # Agent identifier    basemodel_agent.py           # BaseModelAgent (@agent.defn)

workspace_dir: str | None                          # Working directory  workflows/

planning_interval: int | None                      # Steps between replanning    research_workflow.py         # example long-running workflow

memory_budget_chars: int = 100000                  # History size limit    doc_pipeline_workflow.py     # optional: write-up pipeline

keep_last: int = 5                                 # Entries to preserve verbatim  functions/

planner_mode: Literal["scripted","heuristic","model"] = "heuristic"    memory_io.py                 # save_snapshot, load_snapshot

allowed_tools: list[str] = []                      # Tool whitelist    memory_compactor.py          # compaction logic

queues: dict[str,int] = {"openai": 4, "io": 8}    # Concurrency limits    token_count.py               # approximate token counter

```    tools/

      search_papers.py

### Task      generate_ideas.py

```python      refine_ideas.py

id: str                                            # Unique task ID      run_experiment.py

kind: Literal["research","writeup","review","custom"]      collect_results.py

description: str                                   # Human-readable description      compile_writeup.py

payload: dict[str, Any]                            # Task-specific data      reviewer.py

```      # add more as needed

  models/

### Plan & PlanStep    config.py                    # Pydantic config models

```python    events.py                    # Task, Plan, HistoryEntry, Artifact

# Plan    plan.py                      # Plan/PlanStep definitions

task_id: str                                       # Associated task```

steps: list[PlanStep]                              # Ordered steps

created_at: float                                  # Timestamp---



# PlanStep# Minimal data contracts (Pydantic)

name: str                                          # Tool/workflow name

inputs: dict[str, Any]                             # Step inputs* **Config**

depends_on: list[str] = []                         # Dependencies

timeout_seconds: int = 60                          # Execution timeout  * `agent_name: str`

retry_attempts: int = 2                            # Max retries  * `workspace_dir: str | None`

```  * `planning_interval: int | None`

  * `memory_budget_chars: int = 16000`

### HistoryEntry  * `keep_last: int = 5`

```python  * `planner_mode: Literal["scripted","heuristic","model"] = "heuristic"`

timestamp: float                                   # Unix timestamp  * `allowed_tools: list[str] = []`

kind: Literal["plan","step","observation","error","metadata"]  * `queues: dict[str,int] = {"openai": 4, "io": 8}`

name: str                                          # Step/event name* **Task**

inputs_digest: str | None                          # SHA256 of inputs

result_digest: str | None                          # SHA256 of outputs  * `id: str`

latency_ms: int | None                             # Execution time  * `kind: Literal["research","writeup","review","custom"]`

error: str | None                                  # Error message  * `payload: dict[str, Any]`

tags: list[str] = []                               # Custom tags* **Plan / PlanStep**

```

  * `steps: list[PlanStep]`

### Artifact  * `PlanStep(name: str, inputs: dict[str, Any], group: str | None = None, retry: int = 2, timeout_s: int = 60)`

```python* **HistoryEntry**

name: str                                          # Artifact identifier

kind: str                                          # Type (file, data, reference)  * `ts: float`

location: str                                      # Path or URL  * `kind: Literal["plan","step","obs","error","meta"]`

hash: str | None                                   # Content hash  * `name: str`

created_at: float                                  # Timestamp  * `inputs_digest: str`

```  * `result_digest: str | None`

  * `latency_ms: int | None`

---  * `error: str | None`

  * `tags: list[str] = []`

## 📋 Event Interface

---

### Inbound Events (all `@agent.event`)

# MVP scope (what we ship first)

```python

@agent.event1. **Agent** with events: `configure`, `enqueue_task`, `shutdown`.

async def configure(self, config: dict):2. **Heuristic planner**: scripted sequence per task kind.

    """Initialize or update agent configuration"""3. **Tool registry**: a handful of functions (search/ideas/refine/compile).

4. **Memory**: append-only history + **char-budget compaction** using `memory_compactor`.

@agent.event5. **Persistence**: `save_snapshot`/`load_snapshot` functions, called after each task.

async def enqueue_task(self, task: dict):6. **Observability**: structured logs + step timing; basic metrics counters.

    """Add a new task to the inbox"""

---

@agent.event

async def inject_memory(self, frames: list[dict]):# Phase-by-phase roadmap

    """Inject historical context (optional)"""

**v0.1 (MVP)**

@agent.event

async def set_plan(self, plan: dict):* Heuristic planner; sequential steps; compaction by char budget; simple snapshot to JSONL.

    """Override plan manually (optional)"""* Strict allow-list for tools from config.



@agent.event**v0.2 (Resilience & scale)**

async def shutdown(self):

    """Gracefully shutdown the agent"""* Per-tool retries/backoff; concurrency queues; non-retryable failure handling; circuit breaker.

```* Parallel step groups inside workflows.



### Main Run Loop**v0.3 (Model-driven planning)**



```python* Planner function using LLM to output `PlanStep[]` under policy checks.

@agent.run* Token-aware compaction (use a `token_count` tool).

async def run(self):

    """**v0.4 (Security & sandboxing)**

    Main agent loop:

    1. Wait for configuration* Optional WASM/containerized executor for “code steps”.

    2. Wait for tasks or shutdown* Auditable allow-list/deny-list policies and secrets-scrubbing in logs.

    3. Plan next steps

    4. Execute steps**v1.0 (Production)**

    5. Persist snapshot

    6. Compact memory if needed* Full metrics + traces; redaction; CLI for snapshot import/export; versioned plan schema.

    7. Continue or restart* Integration tests suite and replay tools.

    """

```---



---# Testing strategy



## 🧪 Testing* **Unit**: planner (inputs → steps), tool I/O validation, compactor invariants.

* **Workflow**: golden tests for sequence outputs, retry paths, partial failures.

### Test Suite Status* **Agent**: event → state transitions, persistence & resume, shutdown flow.

```bash* **Load**: many small tasks; compaction & snapshot under pressure.

$ python -m pytest tests/test_models.py -v

---

tests/test_models.py::TestModels::test_config_creation PASSED          [16%]

tests/test_models.py::TestModels::test_task_creation PASSED            [33%]# Performance notes

tests/test_models.py::TestModels::test_plan_creation PASSED            [50%]

tests/test_models.py::TestModels::test_plan_next_steps PASSED          [66%]* Keep agent loop CPU-light; push I/O and heavy work to **functions**.

tests/test_models.py::TestModels::test_history_entry_creation PASSED   [83%]* Prefer workflows when chaining many steps or when you need parallelism.

tests/test_models.py::TestModels::test_artifact_creation PASSED        [100%]* Snapshots on a schedule or after N steps, not after every log line.

* Use function queues to protect upstream APIs (e.g., “openai” rate limits).

============================================= 6 passed in 0.79s =============================================

```# Restack Python Framework - Quick Reference



### Test Coverage## Setup & Installation

- ✅ BaseModelConfig validation

- ✅ Task creation and validation**Requirements:** Docker Desktop, Python 3.10-3.13, UV/pipx

- ✅ Plan creation with multiple steps

- ✅ Plan dependency resolution (`next_ready_steps()`)```bash

- ✅ HistoryEntry creation# Install & create new app

- ✅ Artifact creationpipx install restackio.get-started --force && restackio.get-started



### Testing Strategy (Full Roadmap)# Start Restack engine

- **Unit**: Planner logic, tool I/O validation, compactor invariantsdocker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main

- **Workflow**: Sequence outputs, retry paths, partial failures

- **Agent**: Event → state transitions, persistence & resume, shutdown flow# Setup environment

- **Load**: Many small tasks; compaction & snapshot under pressureuv venv && source .venv/bin/activate

uv sync && uv run dev

---```



## 🗺️ Roadmap## Agents



### ✅ v0.1.0 (MVP) - **COMPLETE**Event-driven processes that persist state and run continuously.

- ✅ Heuristic planner with dependency resolution

- ✅ Sequential step execution```python

- ✅ Character-budget memory compactionfrom restack_ai.agent import agent, step, condition

- ✅ JSONL snapshot persistence

- ✅ Strict tool allow-list validation@agent.defn()

- ✅ Basic structured loggingclass MyAgent:

- ✅ Full test suite for data models    def __init__(self):

- ✅ All Restack conventions properly applied        self.end = False

        self.messages = []

### 🔜 v0.2.0 (Resilience & Scale) - **NEXT**    

**Goal**: Production-grade reliability and concurrency    @agent.event

    async def messages(self, messages: List[Message]):

- [ ] **Per-tool retry policies** with exponential backoff        self.messages = messages

- [ ] **Concurrency queues** enforcement (openai, io, compute)    

- [ ] **Non-retryable failure handling** (validation errors, auth failures)    @agent.run

- [ ] **Circuit breaker pattern** for repeated tool failures    async def run(self):

- [ ] **Parallel step execution** within workflows        await agent.step(

- [ ] **Function-level tests** for all 8 tools            function=send_email,

- [ ] **Workflow integration tests** (ResearchWorkflow, DocPipelineWorkflow)            function_input=SendEmailInput(text="Hello"),

- [ ] **Agent state transition tests** (configure → enqueue → plan → execute → persist)            start_to_close_timeout=timedelta(seconds=120)

        )

**Deliverables**:        await condition(lambda: self.end)

- Enhanced error taxonomy with retryable/non-retryable classification```

- Queue manager for rate limiting per provider

- Workflow tests with golden outputs and failure scenarios## Functions

- Agent tests for event handling and persistence

Regular Python functions made available to agents/workflows.

### 🔮 v0.3.0 (Model-Driven Planning)

**Goal**: LLM-powered autonomous planning```python

from restack_ai.function import function, log, FunctionFailure

- [ ] **Planner function** using LLM to generate `PlanStep[]`from pydantic import BaseModel

- [ ] **Policy-based plan validation** (safety checks, budget limits)

- [ ] **Token-aware compaction** using `token_count` toolclass FunctionInput(BaseModel):

- [ ] **Dynamic replanning** on failures or drift detection    email_content: str

- [ ] **Plan templates** for common task patterns

- [ ] **Planner performance metrics** (plan quality, token usage)@function.defn()

async def analyze_email(function_input: FunctionInput) -> str:

**Deliverables**:    log.info("Processing email")

- LLM planner with prompt templates    return "Analysis result"

- Plan validation framework```

- Token-based memory management

- Replanning triggers and logic## Workflows



### 🔐 v0.4.0 (Security & Sandboxing)Define sequences of steps for AI workflows.

**Goal**: Safe execution and compliance

```python

- [ ] **WASM/container sandbox** for code execution stepsfrom restack_ai.workflow import workflow

- [ ] **Secrets scrubbing** in logs and snapshotsfrom pydantic import BaseModel

- [ ] **Auditable allow-list/deny-list** policies

- [ ] **Input/output sanitization** for all toolsclass WorkflowInput(BaseModel):

- [ ] **Data redaction** for PII and sensitive information    email_context: str

- [ ] **Security audit logging** for compliance

@workflow.defn()

**Deliverables**:class AutomatedWorkflow:

- Sandboxed code executor function    @workflow.run

- Secret management system    async def run(self, input: WorkflowInput):

- Policy enforcement framework        text = await workflow.step(

- Audit log system            generate_content,

            input,

### 🏆 v1.0.0 (Production)            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10))

**Goal**: Enterprise-ready agent platform        )

        return {"result": text}

- [ ] **Full metrics & traces** (OpenTelemetry integration)```

- [ ] **CLI tools** for snapshot import/export, debugging

- [ ] **Versioned plan schema** with migration support## Client

- [ ] **Integration test suite** (end-to-end scenarios)

- [ ] **Replay tools** for debugging and analysisInterface for scheduling agents/workflows and sending events.

- [ ] **Performance benchmarks** and optimization

- [ ] **Documentation** (API reference, tutorials, examples)```python

- [ ] **Deployment guides** (Docker, Kubernetes, cloud)from restack_ai import Restack



**Deliverables**:client = Restack()

- Production monitoring stack

- CLI tool suite# Schedule agent

- Comprehensive documentationrun_id = await client.schedule_agent(

- Deployment templates    agent_name="MyAgent",

    agent_id="unique-id",

---    agent_input={"key": "value"}

)

## 🎯 Next Steps (Immediate)

# Send event to agent

### For v0.2.0 Developmentclient.send_agent_event(

    agent_id="agent-id",

1. **Implement Per-Tool Retry Policies**    run_id="run-id",

   ```python    event_name="message",

   # In src/models/config.py    event_input={"content": "Hello"}

   class ToolPolicy(BaseModel):)

       max_attempts: int = 3

       initial_interval_seconds: int = 10# Schedule workflow

       max_interval_seconds: int = 60await client.schedule_workflow(

       backoff_coefficient: float = 2.0    workflow_name="AutomatedWorkflow",

       non_retryable_errors: list[str] = []    workflow_id="unique-id",

       workflow_input={"key": "value"}

   # Update BaseModelConfig)

   tool_policies: dict[str, ToolPolicy] = {}```

   ```

## Services

2. **Add Queue Manager**

   ```pythonRegister agents, workflows, and functions with task queues.

   # New file: src/utils/queue_manager.py

   class QueueManager:```python

       """Enforce concurrency limits per queue"""from restack_ai import Restack

       def acquire(self, queue_name: str) -> boolfrom restack_ai.restack import ServiceOptions

       def release(self, queue_name: str)

   ```client = Restack()



3. **Enhance Error Handling**await client.start_service(

   ```python    agents=[MyAgent],

   # New file: src/models/errors.py    workflows=[AutomatedWorkflow],

   class ToolFailure(Exception):    functions=[analyze_email],

       retryable: bool    task_queue="custom-queue",

       error_code: str    options=ServiceOptions(

       message: str        rate_limit=1,

   ```        max_concurrent_function_runs=1

    )

4. **Write Function Tests**)

   ```python```

   # New file: tests/test_functions.py

   async def test_search_papers()## Running & Testing

   async def test_generate_ideas()

   async def test_memory_compactor()```bash

   # ... etc# Schedule agent from CLI

   ```uv run schedule



5. **Write Workflow Tests**# Access Developer UI

   ```python# http://localhost:5233

   # New file: tests/test_workflows.py

   async def test_research_workflow_happy_path()# API endpoint

   async def test_research_workflow_with_retries()# POST http://localhost:6233/api/agents/AgentName

   async def test_doc_pipeline_workflow()```

   ```

### Running the Agent (Current v0.1.0)

```bash
# 1. Ensure Restack engine is running
docker ps | grep restack

# 2. Start the service (Terminal 1)
python src/service.py
# Expected: "Service on task queue basemodel-agent-queue ready"

# 3. Schedule a task (Terminal 2)
python src/schedule.py
# Expected: Agent processes task, logs appear in Terminal 1

# 4. Monitor execution
# Open http://localhost:5233 in browser
# View: Agent runs, workflow executions, function calls

# 5. Inspect snapshots
ls snapshots/
# See: agent state snapshots in JSON format
```

### Custom Task Example

```python
# examples/custom_research_task.py
from restack_ai import Restack

async def schedule_custom_research():
    client = Restack()
    
    # Send configuration
    await client.send_agent_event(
        agent_id="basemodel-agent-1",
        run_id=await client.schedule_agent(
            agent_name="BaseModelAgent",
            agent_id="basemodel-agent-1",
        ),
        event_name="configure",
        event_input={
            "agent_name": "BaseModelAgent",
            "memory_budget_chars": 100000,
            "planner_mode": "heuristic",
            "allowed_tools": [
                "search_papers",
                "generate_ideas",
                "refine_ideas"
            ]
        }
    )
    
    # Send research task
    await client.send_agent_event(
        agent_id="basemodel-agent-1",
        run_id=run_id,
        event_name="enqueue_task",
        event_input={
            "id": "research-quantum-computing-2025",
            "kind": "research",
            "description": "Research latest quantum computing advances",
            "payload": {
                "topic": "quantum computing breakthroughs 2025",
                "depth": "comprehensive"
            }
        }
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(schedule_custom_research())
```

---

## 📚 Additional Resources

- **[RESTACK_CONVENTIONS.md](./RESTACK_CONVENTIONS.md)** - Complete reference for Restack Python patterns
- **[README.md](./README.md)** - User-facing documentation and setup guide
- **[Restack Python Docs](https://docs.restack.io/libraries/python/agents)** - Official framework documentation
- **Restack Engine UI**: http://localhost:5233 (when running)

---

## 🤝 Contributing

This is a reference implementation. To extend:

1. **Add new functions**: Create in `src/functions/tools/` following existing patterns
2. **Add new workflows**: Create in `src/workflows/` with `@workflow.defn()`
3. **Update models**: Modify Pydantic models in `src/models/`
4. **Write tests**: Add to `tests/` and ensure all pass
5. **Update docs**: Keep this file and README.md in sync

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with Restack** | Last verified: October 22, 2025
