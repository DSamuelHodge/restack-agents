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

## Testing

The service now starts successfully without import errors:

```powershell
python src/service.py
# Starting BaseModel Agent service...
# Registering agents, workflows, and functions...
# [restack] 2025-10-22T18:34:05.559Z [INFO] Starting service on task queue basemodel-agent-queue
# ✓ Service running successfully!
# ✓ No ImportError
```

All import errors have been resolved:
- ✅ Fixed: `cannot import name 'step' from 'restack_ai.agent'`
- ✅ Fixed: `cannot import name 'RetryPolicy' from 'restack_ai'`

## References

- [Restack Python Agents Documentation](https://docs.restack.io/libraries/python/agents)
- [Restack Python Functions Documentation](https://docs.restack.io/libraries/python/functions)
- [Restack Python Workflows Documentation](https://docs.restack.io/libraries/python/workflows)
