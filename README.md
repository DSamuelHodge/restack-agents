# BaseModel Agent

A **Restack-native BaseModel Agent** built from scratch in Python. This agent provides event-driven orchestration with planning, memory management, tool execution, and full observability.

## 🎯 Goals

- **Agent-as-brain**: Long-lived, event-driven orchestrator with clear state and resumability
- **Planning runtime**: Pluggable planning engine (scripted/heuristic/model-driven)
- **Tool layer**: Clean contracts between functions and workflows
- **Memory model**: Durable history with automatic compaction
- **Safety & governance**: Guardrails, validation, rate limiting
- **Observability**: Structured logs, metrics, and replayability
- **Config-first**: Declarative Pydantic config with no hidden state

## 📁 Project Structure

```
basemodelagent/
├── src/
│   ├── agents/
│   │   └── basemodel_agent.py      # Core agent with event handlers
│   ├── workflows/
│   │   ├── research_workflow.py    # Research pipeline
│   │   └── doc_pipeline_workflow.py # Document generation
│   ├── functions/
│   │   ├── memory_io.py            # Snapshot save/load
│   │   ├── memory_compactor.py     # History compaction
│   │   ├── token_count.py          # Token estimation
│   │   └── tools/
│   │       ├── search_papers.py    # Paper search tool
│   │       ├── generate_ideas.py   # Idea generation
│   │       ├── refine_ideas.py     # Idea refinement
│   │       ├── run_experiment.py   # Experiment execution
│   │       ├── collect_results.py  # Results aggregation
│   │       ├── compile_writeup.py  # Document compilation
│   │       └── reviewer.py         # Quality review
│   ├── models/
│   │   ├── config.py               # Configuration model
│   │   ├── events.py               # Task, HistoryEntry, Artifact
│   │   └── plan.py                 # Plan, PlanStep
│   ├── service.py                  # Service registration
│   ├── schedule.py                 # Agent scheduling
│   └── shutdown.py                 # Graceful shutdown
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (for Restack engine)
- **Python 3.10-3.13**
- **UV** (recommended) or pip

### Installation

1. **Clone and navigate to project**:
   ```bash
   cd basemodelagent
   ```

2. **Start Restack engine**:
   ```bash
   docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main
   ```

3. **Setup Python environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Activate (macOS/Linux)
   source .venv/bin/activate
   
   # Install dependencies
   pip install -e .
   ```

4. **Configure environment**:
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your settings
   # (Optional: Add OPENAI_API_KEY if using LLM features)
   ```

### Running the Agent

**Terminal 1: Start the service**
```bash
python src/service.py
```

**Terminal 2: Schedule agent and send tasks**
```bash
python src/schedule.py
```

**View progress**: Open http://localhost:5233 in your browser

**Shutdown agent**:
```bash
python src/shutdown.py --agent-id basemodel-agent-1 --run-id <run-id>
```

## 🧠 Architecture

### Agent (Brain)
- **BaseModelAgent** with `@agent.defn`
- Event handlers: `configure`, `enqueue_task`, `inject_memory`, `set_plan`, `shutdown`
- Main run loop: waits for work → plans → dispatches → persists → compacts → repeats

### Workflows (Missions)
- **ResearchWorkflow**: Search papers → Generate ideas → Refine ideas
- **DocPipelineWorkflow**: Collect results → Compile writeup → Review

### Functions (Tools)
- **Memory**: `save_snapshot`, `load_snapshot`, `memory_compactor`, `token_count`
- **Research**: `search_papers`, `generate_ideas`, `refine_ideas`
- **Execution**: `run_experiment`, `collect_results`
- **Writing**: `compile_writeup`, `reviewer`

## 📝 Configuration

Edit `.env` or pass config via `configure` event:

```python
BaseModelConfig(
    agent_name="BaseModelAgent",
    workspace_dir="./workspace",
    planning_interval=5,           # Steps between planning
    planner_mode="heuristic",      # scripted|heuristic|model
    memory_budget_chars=16000,     # Trigger compaction threshold
    keep_last=5,                   # Keep last N entries verbatim
    allowed_tools=[...],           # Whitelist of tool names
    snapshot_dir="./snapshots",
    snapshot_interval=10,          # Save every N steps
)
```

## 🔧 Usage Examples

### Sending Tasks

```python
from restack_ai import Restack
from src.models import Task

client = Restack()

# Research task
task = Task(
    id="task-001",
    kind="research",
    payload={"topic": "LLMs for Code Generation"},
    priority=1
)

await client.send_agent_event(
    agent_id="basemodel-agent-1",
    run_id=run_id,
    event_name="enqueue_task",
    event_input=task.model_dump()
)

# Writeup task
task = Task(
    id="task-002",
    kind="writeup",
    payload={
        "title": "Results Summary",
        "experiments": ["exp-001", "exp-002"]
    }
)

await client.send_agent_event(
    agent_id="basemodel-agent-1",
    run_id=run_id,
    event_name="enqueue_task",
    event_input=task.model_dump()
)
```

### Custom Planning

```python
from src.models import Plan, PlanStep

# Manual plan override
plan = Plan(
    plan_id="custom-plan-1",
    task_id="task-001",
    mode="scripted",
    steps=[
        PlanStep(name="search_papers", inputs={"query": "topic"}),
        PlanStep(name="generate_ideas", inputs={"topic": "topic"}),
    ]
)

await client.send_agent_event(
    agent_id="basemodel-agent-1",
    run_id=run_id,
    event_name="set_plan",
    event_input=plan.model_dump()
)
```

## 🧪 Testing

Run tests (when implemented):
```bash
pytest tests/
```

## 📊 Observability

- **Structured logs**: Every decision/step logged with timestamps, digests, latency
- **Metrics**: Steps executed, tasks completed, errors encountered
- **Snapshots**: Full state saved periodically to `./snapshots/`
- **History**: Compacted memory with extractive summaries
- **UI**: View real-time progress at http://localhost:5233

## 🛡️ Safety & Governance

- **Tool allowlist**: Only configured tools can execute
- **Validation**: Pydantic schemas for all inputs/outputs
- **Rate limiting**: Configurable concurrency per queue
- **Timeouts**: Per-step timeout enforcement
- **Error handling**: Retries with exponential backoff

## 🗺️ Roadmap

### v0.1 (MVP) ✅
- Heuristic planner
- Sequential execution
- Char-budget compaction
- JSONL snapshots
- Tool allowlist

### v0.2 (Resilience)
- Per-tool retries/backoff
- Concurrency queues
- Circuit breaker
- Parallel step groups

### v0.3 (Model-driven)
- LLM-based planner
- Token-aware compaction
- Dynamic tool selection

### v0.4 (Security)
- WASM/container sandbox
- Secrets scrubbing
- Audit logs

### v1.0 (Production)
- Full metrics & traces
- CLI tools
- Integration test suite

## 📚 Documentation

- See `specs.md` for complete specification
- API docs: [Restack Python Framework](https://docs.restack.io)
- Developer UI: http://localhost:5233

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

**Restack engine not running?**
```bash
docker ps  # Check if container is running
docker logs restack  # View logs
```

**Import errors?**
```bash
pip install -e .  # Reinstall in editable mode
```

**Agent not responding?**
- Check http://localhost:5233 for status
- Verify configuration was sent
- Check service logs for errors

## 📞 Support

- GitHub Issues: Report bugs or request features
- Documentation: https://docs.restack.io
- Community: Join Restack Discord

---

Built with ❤️ using [Restack](https://www.restack.io/)
