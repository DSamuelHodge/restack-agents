# Restack Python Agent Reference

Complete guide for building AI agents with Restack's Python framework.

---

## What is an Agent?

An **agent** is an event-driven background process that:
- Persists state across restarts
- Executes tasks over extended periods
- Runs continuously (weeks to months)
- Responds to external events

---

## Core Decorators

### `@agent.defn()`
Defines the agent class.

```python
from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        pass
```

### `@agent.run`
Entry point for agent execution.

```python
@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        # Main logic here
        return {"status": "complete"}
```

### `@agent.event`
Handles incoming events that modify agent state.

```python
from typing import List
from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    def __init__(self):
        self.messages = []
        self.end = False
    
    @agent.event
    async def messages(self, messages: List[dict]):
        """Receive new messages"""
        self.messages = messages
        return messages
    
    @agent.event
    async def end(self):
        """Signal shutdown"""
        self.end = True
        return True
```

---

## State Management

### `__init__()`
Define variables that persist in agent state.

```python
@agent.defn()
class MyAgent:
    def __init__(self):
        self.config = None
        self.tasks = []
        self.completed = 0
```

---

## Control Flow

### `condition()`
Wait for a state condition to become true.

```python
from restack_ai.agent import agent, condition

@agent.defn()
class MyAgent:
    def __init__(self):
        self.end = False
    
    @agent.run
    async def run(self):
        # Wait until end flag is set
        await condition(lambda: self.end)
        return {"shutdown": True}
```

**Common patterns:**
```python
# Wait for configuration
await condition(lambda: self.config is not None)

# Wait for work or shutdown
await condition(lambda: len(self.tasks) > 0 or self.end)
```

---

## Executing Steps

### `agent.step()`
Execute a function with timeout and retry policies.

```python
from restack_ai.agent import agent, import_functions
from datetime import timedelta

with import_functions():
    from src.functions.email import send_email

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        result = await agent.step(
            function=send_email,
            function_input={
                "to": "user@example.com",
                "subject": "Hello",
                "text": "Message body"
            },
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(
                max_attempts=3,
                initial_interval=timedelta(seconds=10),
                backoff_coefficient=2.0
            )
        )
        return result
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `function` | callable | Function to execute (required) |
| `function_input` | dict | Input data (required) |
| `task_queue` | str | Queue name (default: "restack") |
| `start_to_close_timeout` | timedelta | Max execution time |
| `schedule_to_close_timeout` | timedelta | Max time from scheduling |
| `schedule_to_start_timeout` | timedelta | Max wait before execution |
| `heartbeat_timeout` | timedelta | Heartbeat interval |
| `retry_policy` | RetryPolicy | Retry configuration |

**RetryPolicy options:**
- `max_attempts` (int) - Number of retries
- `initial_interval` (timedelta) - First retry delay
- `max_interval` (timedelta) - Max retry delay
- `backoff_coefficient` (float) - Exponential backoff multiplier

---

## Long-Running Agents

### `agent.should_continue_as_new()`
Check if agent needs restart (after ~2000 events).

```python
@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        self.end = False
        
        # Wait for end signal or restart trigger
        await condition(
            lambda: self.end or agent.should_continue_as_new()
        )
        
        if agent.should_continue_as_new():
            agent.agent_continue_as_new()
        
        return {"status": "complete"}
```

### `agent.agent_continue_as_new()`
Restart agent with same ID and fresh history.

```python
@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        # Process work...
        
        # Restart with new input
        if agent.should_continue_as_new():
            agent.agent_continue_as_new(
                input={"checkpoint": self.last_processed_id}
            )
```

**Use for:**
- Agents running weeks/months
- Processing >2000 events
- Preventing history bloat

---

## Child Workflows/Agents

### `agent.child_start()`
Launch child agent without waiting for completion.

```python
from restack_ai.agent import agent
from src.agents.child_agent import ChildAgent

@agent.defn()
class ParentAgent:
    @agent.run
    async def run(self):
        # Start child and continue immediately
        handle = await agent.child_start(
            agent=ChildAgent,
            agent_input={"task_id": "123"},
            task_queue="child-queue"
        )
        
        # Child runs independently
        return {"child_handle": handle}
```

### `agent.child_execute()`
Execute child workflow and wait for result.

```python
from restack_ai.agent import agent
from src.workflows.analysis import analyze_data

@agent.defn()
class ParentAgent:
    @agent.run
    async def run(self):
        # Wait for child to complete
        result = await agent.child_execute(
            workflow=analyze_data,
            workflow_id="analysis-001",
            workflow_input={"dataset": "users.csv"}
        )
        
        return result  # Child's return value
```

---

## Utilities

### `import_functions()`
Import functions within context manager for proper registration.

```python
from restack_ai.agent import import_functions

with import_functions():
    from src.functions.search import search_papers
    from src.functions.email import send_email
    from src.functions.storage import save_data
```

### `log`
Log messages at different severity levels.

```python
from restack_ai.agent import agent, log

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self, input: dict):
        log.info("Agent started", input)
        log.debug("Processing task")
        log.warning("Resource low")
        log.error("Operation failed")
        log.critical("Fatal error")
```

### `agent.uuid()`
Generate unique identifier.

```python
@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        task_id = agent.uuid()
        log.info(f"Task ID: {task_id}")
        return task_id
```

### `agent.agent_info()`
Retrieve current agent metadata.

```python
@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        info = agent.agent_info()
        # Returns: agent_id, run_id, task_queue, etc.
        log.info(f"Running as: {info.agent_id}")
        return info
```

---

## Complete Example

```python
from restack_ai.agent import agent, condition, log, import_functions
from datetime import timedelta
from typing import List

with import_functions():
    from src.functions.process import process_item

@agent.defn()
class TaskProcessor:
    def __init__(self):
        self.config = None
        self.tasks = []
        self.completed = 0
        self.end = False
    
    @agent.event
    async def configure(self, config: dict):
        """Initialize agent configuration"""
        self.config = config
        log.info("Agent configured")
    
    @agent.event
    async def add_task(self, task: dict):
        """Add task to queue"""
        self.tasks.append(task)
    
    @agent.event
    async def shutdown(self):
        """Signal graceful shutdown"""
        self.end = True
    
    @agent.run
    async def run(self):
        # Wait for configuration
        await condition(lambda: self.config is not None)
        log.info("Agent ready")
        
        while not self.end:
            # Wait for work or shutdown
            await condition(
                lambda: len(self.tasks) > 0 or 
                        self.end or 
                        agent.should_continue_as_new()
            )
            
            # Handle restart
            if agent.should_continue_as_new():
                agent.agent_continue_as_new()
                break
            
            # Process tasks
            while self.tasks and not self.end:
                task = self.tasks.pop(0)
                
                try:
                    result = await agent.step(
                        function=process_item,
                        function_input={"task": task},
                        start_to_close_timeout=timedelta(seconds=60)
                    )
                    
                    self.completed += 1
                    log.info(f"Task complete: {task['id']}")
                    
                except Exception as e:
                    log.error(f"Task failed: {e}")
        
        return {
            "status": "shutdown",
            "completed": self.completed
        }
```

---

## Scheduling Agents

```python
from restack_ai import Restack
from datetime import datetime

async def start_agent():
    client = Restack()
    
    # Schedule agent
    agent_id = f"processor-{int(datetime.now().timestamp())}"
    run_id = await client.schedule_agent(
        agent_name="TaskProcessor",
        agent_id=agent_id,
        task_queue="restack"
    )
    
    # Send configuration
    await client.send_agent_event(
        agent_id=agent_id,
        event_name="configure",
        event_input={"max_retries": 3}
    )
    
    # Send tasks
    await client.send_agent_event(
        agent_id=agent_id,
        event_name="add_task",
        event_input={"id": "task-001", "action": "process"}
    )
    
    return run_id
```

---

## Key Patterns

**Event-driven state machine:**
```python
await condition(lambda: self.state == "ready")
```

**Graceful shutdown:**
```python
await condition(lambda: self.end)
```

**Periodic restarts:**
```python
if agent.should_continue_as_new():
    agent.agent_continue_as_new()
```

**Error handling:**
```python
try:
    result = await agent.step(...)
except Exception as e:
    log.error(f"Failed: {e}")
```