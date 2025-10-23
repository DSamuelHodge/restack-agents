# Restack Conventions Applied

This document summarizes the Restack Python framework conventions applied to the BaseModel Agent.

# Restack Python Framework Conventions

Quick reference for building agents, workflows, and functions with Restack AI.

---

## Core Imports

### Agent Module
```python
from restack_ai.agent import agent, condition, log, import_functions
```

- `agent` - Decorator and execution context
- `condition` - Wait for state changes
- `log` - Logging utility
- `import_functions` - Context manager for function imports

### Workflow Module
```python
from restack_ai.workflow import workflow, log, RetryPolicy
```

### Function Module
```python
from restack_ai.function import function, log
```

---

## Agent Pattern

```python
from restack_ai.agent import agent, condition, log, import_functions
from datetime import timedelta

# Import functions inside context manager
with import_functions():
    from ..functions.tools import search_papers, generate_ideas

@agent.defn()
class MyAgent:
    def __init__(self):
        self.config = None
        self.tasks = []
    
    @agent.event
    async def configure(self, config: dict):
        """Event handler for configuration"""
        self.config = config
        log.info("Agent configured")
    
    @agent.event
    async def add_task(self, task: dict):
        """Event handler for tasks"""
        self.tasks.append(task)
    
    @agent.run
    async def run(self):
        """Main entry point"""
        # Wait for configuration
        await condition(lambda: self.config is not None)
        
        # Wait for work
        await condition(lambda: len(self.tasks) > 0)
        
        # Execute step
        result = await agent.step(
            function=search_papers,
            function_input={"query": "quantum computing"},
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        return {"status": "complete"}
```

**Key Points:**
- Use `agent.step()` not `step()` - it's a method, not a standalone function
- All event handlers must be `async`
- Use `condition()` for event-driven waiting

---

## Workflow Pattern

```python
from restack_ai.workflow import workflow, log, RetryPolicy
from datetime import timedelta

@workflow.defn()
class ResearchWorkflow:
    @workflow.run
    async def run(self, input: dict):
        # Execute with retry policy
        papers = await workflow.step(
            function=search_papers,
            function_input={"query": input["topic"]},
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )
        
        ideas = await workflow.step(
            function=generate_ideas,
            function_input={"papers": papers}
        )
        
        return {"ideas": ideas}
```

**Critical:** Always use **named parameters** in `workflow.step()`:
```python
# ✅ Correct
await workflow.step(function=my_func, function_input=data)

# ❌ Wrong - causes TypeError
await workflow.step(my_func, data)
```

---

## Function Pattern

```python
from restack_ai.function import function, log
from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str
    limit: int = 10

class SearchOutput(BaseModel):
    results: list[str]

@function.defn()
async def search_papers(input: SearchInput) -> SearchOutput:
    log.info(f"Searching: {input.query}")
    
    # Your logic here
    results = ["paper1", "paper2"]
    
    return SearchOutput(results=results)
```

---

## Workflow Determinism Rules

**Problem:** Temporal workflows replay execution for fault tolerance. Non-deterministic functions break replay.

### ❌ Restricted in Workflows
```python
import datetime
timestamp = datetime.datetime.now()  # RestrictedWorkflowAccessError

import time
timestamp = time.time()  # RestrictedWorkflowAccessError

import random
value = random.random()  # RestrictedWorkflowAccessError

import uuid
id = uuid.uuid4()  # RestrictedWorkflowAccessError
```

### ✅ Solutions

**Option 1: Static defaults**
```python
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str
    created_at: float = Field(default=0.0)  # Not datetime.now()
```

**Option 2: Pass from outside workflow**
```python
# In scheduler (not in workflow context)
from datetime import datetime

task = Task(
    id="task-001",
    created_at=datetime.now().timestamp()  # ✅ OK here
)

await client.send_agent_event(
    agent_id=agent_id,
    event_name="enqueue_task",
    event_input=task.model_dump()
)
```

**Option 3: Make metrics optional**
```python
# Inside workflow
self._log_event(
    kind="step",
    name="process_task",
    latency_ms=None  # Don't calculate with time.time()
)
```

---

## Service Registration

```python
from restack_ai import Restack
from restack_ai.restack import ServiceOptions

async def main():
    client = Restack()
    
    await client.start_service(
        agents=[MyAgent],
        workflows=[ResearchWorkflow],
        functions=[search_papers, generate_ideas],
        task_queue="restack",  # Default queue name
        options=ServiceOptions(
            rate_limit=10,
            max_concurrent_function_runs=5
        )
    )
```

---

## Scheduling Agents

```python
from restack_ai import Restack
from datetime import datetime

async def schedule_agent():
    client = Restack()
    
    # Start agent
    agent_id = f"my-agent-{int(datetime.now().timestamp())}"
    run_id = await client.schedule_agent(
        agent_name="MyAgent",
        agent_id=agent_id,
        task_queue="restack"
    )
    
    # Send configuration event
    await client.send_agent_event(
        agent_id=agent_id,
        event_name="configure",
        event_input={"setting": "value"}
    )
    
    # Send task event
    await client.send_agent_event(
        agent_id=agent_id,
        event_name="add_task",
        event_input={"task_id": "t1", "action": "search"}
    )
```

**Note:** Use unique agent IDs (e.g., timestamp-based) to avoid conflicts when scheduling multiple runs.

---

## Common Patterns

### Waiting for Conditions
```python
# Wait for config
await condition(lambda: self.config is not None)

# Wait for tasks or shutdown
await condition(lambda: len(self.tasks) > 0 or self.shutdown)
```

### Executing Steps with Timeout
```python
from datetime import timedelta

result = await agent.step(
    function=my_function,
    function_input={"key": "value"},
    start_to_close_timeout=timedelta(seconds=30)
)
```

### Error Handling
```python
try:
    result = await agent.step(
        function=risky_function,
        function_input=data,
        start_to_close_timeout=timedelta(seconds=60)
    )
except Exception as e:
    log.error(f"Step failed: {e}")
```

---

## Testing Commands

```bash
# Terminal 1: Start service
python src/service.py

# Terminal 2: Schedule agent
python src/schedule.py
```

---

## Key Takeaways

1. **Imports:** `log` comes from `restack_ai.agent`, not `restack_ai.function`
2. **Step execution:** Use `agent.step()` or `workflow.step()` with **named parameters**
3. **Determinism:** No `datetime.now()`, `time.time()`, `random`, or `uuid` in workflows
4. **Function imports:** Wrap in `with import_functions():` context
5. **Task queue:** Use `"restack"` for default compatibility
6. **Agent IDs:** Make unique per run to avoid scheduling conflicts

## References

- [Restack Python Agents Documentation](https://docs.restack.io/libraries/python/agents)
- [Restack Python Functions Documentation](https://docs.restack.io/libraries/python/functions)
- [Restack Python Workflows Documentation](https://docs.restack.io/libraries/python/workflows)
