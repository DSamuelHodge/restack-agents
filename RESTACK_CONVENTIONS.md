# Restack Conventions Applied

This document summarizes the Restack Python framework conventions applied to the BaseModel Agent.

## Import Corrections

### ✅ Fixed Imports in `basemodel_agent.py`

**Before (Incorrect):**
```python
from restack_ai.agent import agent, step, condition
from restack_ai.function import log
```

**After (Correct):**
```python
from restack_ai.agent import agent, condition, log, import_functions
```

### Key Changes:
1. **Removed `step` import** - `step` is not directly importable; it's accessed as `agent.step()`
2. **Moved `log` import** - `log` comes from `restack_ai.agent`, not `restack_ai.function`
3. **Added `import_functions`** - Context manager for properly importing functions

## Function Import Pattern

### ✅ Using `import_functions()` Context Manager

**Correct Pattern:**
```python
with import_functions():
    from ..functions.memory_io import save_snapshot, load_snapshot
    from ..functions.memory_compactor import memory_compactor
    from ..functions.token_count import token_count
    from ..functions.tools import (
        search_papers,
        generate_ideas,
        refine_ideas,
        run_experiment,
        collect_results,
        compile_writeup,
        reviewer,
    )
```

This ensures functions are properly registered with the Restack framework.

## Agent Decorators

### ✅ Correct Agent Decorator Usage

```python
@agent.defn()
class BaseModelAgent:
    """Agent class definition"""
    
    def __init__(self):
        """Initialize agent state variables"""
        self.cfg = None
        self.inbox = []
        # ... other state
    
    @agent.event
    async def configure(self, config: dict):
        """Event handler for configuration"""
        pass
    
    @agent.event
    async def enqueue_task(self, task: dict):
        """Event handler for tasks"""
        pass
    
    @agent.run
    async def run(self):
        """Main agent entry point"""
        await condition(lambda: self.cfg is not None)
        # ... main loop
```

### Decorator Reference:
- `@agent.defn()` - Defines the agent class
- `@agent.event` - Defines event handlers (configure, enqueue_task, inject_memory, set_plan, shutdown)
- `@agent.run` - Defines the main entry point
- `condition(lambda: ...)` - Wait for a condition to be true

## Executing Steps

### ✅ Using `agent.step()` Method

**Correct Usage:**
```python
result = await agent.step(
    function=func,
    function_input=step_obj.inputs,
    start_to_close_timeout=timedelta(seconds=60),
)
```

**NOT:**
```python
result = await step(...)  # ❌ Wrong - step is not imported
```

### Available Parameters for `agent.step()`:
- `function` - The function to execute (required)
- `function_input` - Input data for the function (required)
- `start_to_close_timeout` - Maximum execution time
- `task_queue` - Specific queue to use
- `retry_policy` - Retry configuration

## Logging

### ✅ Using `log` from `restack_ai.agent`

```python
from restack_ai.agent import log

log.info("Message")
log.debug("Debug info")
log.warning("Warning")
log.error("Error occurred")
log.critical("Critical issue")
```

## Condition Waits

### ✅ Using `condition()` for Event-Driven Waiting

```python
from restack_ai.agent import condition

# Wait for configuration
await condition(lambda: self.cfg is not None)

# Wait for tasks or shutdown
await condition(lambda: len(self.inbox) > 0 or self.shutdown_flag)

# Continue-as-new pattern
await condition(lambda: self.end or agent.should_continue_as_new())
if agent.should_continue_as_new():
    agent.agent_continue_as_new()
```

## Workflow Conventions

### ✅ Workflow Decorator Pattern

**Correct Imports:**
```python
from restack_ai.workflow import workflow, log, RetryPolicy
```

**NOT:**
```python
from restack_ai import RetryPolicy  # ❌ Wrong - RetryPolicy is in workflow module
```

**Correct Usage:**
```python
from restack_ai.workflow import workflow, log, RetryPolicy
from datetime import timedelta

@workflow.defn()
class ResearchWorkflow:
    @workflow.run
    async def run(self, input: ResearchWorkflowInput):
        result = await workflow.step(
            function=search_papers,
            function_input={"query": input.topic},
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )
        return result
```

### ✅ Critical: Use Named Parameters in workflow.step()

**Correct:**
```python
result = await workflow.step(
    function=my_function,           # ✅ Named parameter
    function_input={"key": "value"} # ✅ Named parameter
)
```

**WRONG:**
```python
result = await workflow.step(
    my_function,           # ❌ Positional argument
    {"key": "value"}       # ❌ Positional argument
)
# TypeError: Workflow.step() takes 1 positional argument but 3 were given
```

**Note**: The type checker may show false positive errors for `start_to_close_timeout` parameter, but it is valid and works correctly at runtime.

## Workflow Determinism Requirements

### ⚠️ CRITICAL: Non-Deterministic Functions Are Restricted

**Problem**: Temporal workflows require **deterministic replay** for fault tolerance and recovery. Any function that returns different values on different calls is non-deterministic and will cause `RestrictedWorkflowAccessError`.

**Restricted Functions** (will throw errors in workflow context):
```python
# ❌ THESE WILL FAIL IN WORKFLOWS:
import datetime
timestamp = datetime.datetime.now()  # RestrictedWorkflowAccessError

import time
timestamp = time.time()              # RestrictedWorkflowAccessError

import random
value = random.random()              # RestrictedWorkflowAccessError

import uuid
id = uuid.uuid4()                    # RestrictedWorkflowAccessError
```

### ✅ Solutions for Timestamp Tracking

**Option 1: Use Static Defaults** (Simplest)
```python
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str
    created_at: float = Field(default=0.0, description="Timestamp not available in workflow context")
```

**Option 2: Pass Timestamps from Outside Workflow**
```python
# In schedule.py (NOT in workflow context)
from datetime import datetime

task = Task(
    id="task-001",
    created_at=datetime.now().timestamp()  # ✅ OK - not in workflow
)

await client.send_agent_event(
    agent_id=agent_id,
    event_name="enqueue_task",
    event_input=task.model_dump()
)
```

**Option 3: Omit Time-Based Metrics**
```python
# In agent workflow code
async def _process_task(self, task: Task):
    # ❌ DON'T DO THIS:
    # start_time = time.time()
    # latency_ms = int((time.time() - start_time) * 1000)
    
    # ✅ DO THIS INSTEAD:
    self._log_event(
        kind="step",
        name="process_task",
        latency_ms=None  # Make it optional, set to None
    )
```

### ✅ Real-World Example from BaseModel Agent

**Before (Incorrect - causes RestrictedWorkflowAccessError):**
```python
from datetime import datetime
import time

class BaseModelAgent:
    async def _process_task(self, task: Task):
        start_time = time.time()  # ❌ Non-deterministic
        
        await self._execute_plan(task)
        
        latency = int((time.time() - start_time) * 1000)  # ❌ Non-deterministic
        self._log_event(latency_ms=latency)
```

**After (Correct - deterministic):**
```python
class BaseModelAgent:
    async def _process_task(self, task: Task):
        # No start_time tracking
        
        await self._execute_plan(task)
        
        # Latency tracking is optional
        self._log_event(latency_ms=None)  # ✅ Static value
```

### Key Learnings

1. **Workflow code must be 100% deterministic** - same inputs always produce same outputs
2. **Both `datetime.now()` AND `time.time()` are restricted** - not just datetime
3. **Timestamp tracking is not essential** - most workflow logic doesn't need exact timestamps
4. **Static defaults work fine** - use `0.0` or `None` for timestamp fields in workflow context
5. **Pass time-sensitive data from outside** - scheduler/client can add timestamps before sending to workflow

## Function Conventions

### ✅ Function Decorator Pattern

```python
from restack_ai.function import function, log
from pydantic import BaseModel

class MyFunctionInput(BaseModel):
    query: str

class MyFunctionOutput(BaseModel):
    results: list[str]

@function.defn()
async def my_function(input: MyFunctionInput) -> MyFunctionOutput:
    log.info(f"Executing with: {input.query}")
    return MyFunctionOutput(results=["result1", "result2"])
```

## Service Registration

### ✅ Proper Service Startup

```python
from restack_ai import Restack
from restack_ai.restack import ServiceOptions

async def main():
    client = Restack()
    
    await client.start_service(
        agents=[BaseModelAgent],
        workflows=[ResearchWorkflow, DocPipelineWorkflow],
        functions=[
            save_snapshot,
            load_snapshot,
            memory_compactor,
            # ... other functions
        ],
        task_queue="basemodel-agent-queue",
        options=ServiceOptions(
            rate_limit=10,
            max_concurrent_function_runs=5,
        ),
    )
```

## Summary of Fixes

1. ✅ Corrected imports in `basemodel_agent.py`
   - Removed `step` from imports (use `agent.step()` instead)
   - Moved `log` from `restack_ai.function` to `restack_ai.agent`
   - Added `import_functions` for proper function registration

2. ✅ Changed `step()` to `agent.step()` in agent code

3. ✅ Added `import_functions()` context manager for function imports

4. ✅ Fixed `RetryPolicy` import in workflow files
   - Changed from `from restack_ai import RetryPolicy`
   - To `from restack_ai.workflow import RetryPolicy`

5. ✅ Verified all decorator usage (@agent.defn, @agent.event, @agent.run)

6. ✅ Confirmed proper use of `condition()` for event-driven waiting

7. ✅ **Fixed workflow determinism violations** (v0.2.0)
   - Removed all `datetime.now()` and `time.time()` calls from workflow context
   - Updated Pydantic model defaults from time-based factories to static values
   - Made latency tracking optional instead of calculated
   - Set timestamps to `0.0` for workflow-executed code
   - Task queue aligned to "restack" for proper service/scheduler communication

8. ✅ **Enhanced service configuration**
   - Added `ResourceOptions` import and parameter
   - Changed task queue from "basemodel-agent-queue" to "restack"
   - Added unique timestamped agent IDs in scheduler to avoid conflicts

## Testing

The service now starts successfully and executes tasks end-to-end:

```powershell
# Terminal 1: Start service
python src/service.py
# Starting BaseModel Agent service...
# ✓ Service started successfully!
# ✓ Task Queue: restack

# Terminal 2: Schedule tasks
python src/schedule.py
# ✓ Agent scheduled with run_id: 019a0e78...
# ✓ Configuration sent
# ✓ Research task sent
# ✓ Writeup task sent
```

All errors resolved:
- ✅ Fixed: `cannot import name 'step' from 'restack_ai.agent'`
- ✅ Fixed: `cannot import name 'RetryPolicy' from 'restack_ai'`
- ✅ Fixed: `TypeError: Workflow.step() takes 1 positional argument but 3 were given`
- ✅ Fixed: `RestrictedWorkflowAccessError: Cannot access datetime.datetime.now.__call__`
- ✅ Fixed: `RestrictedWorkflowAccessError: Cannot access time.time.__call__`
- ✅ Fixed: Task queue mismatch between service and scheduler
- ✅ Verified: Complete task execution (research + writeup pipelines) working successfully

## References

- [Restack Python Agents Documentation](https://docs.restack.io/libraries/python/agents)
- [Restack Python Functions Documentation](https://docs.restack.io/libraries/python/functions)
- [Restack Python Workflows Documentation](https://docs.restack.io/libraries/python/workflows)
