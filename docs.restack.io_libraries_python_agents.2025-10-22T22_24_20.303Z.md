# Agents

Library documentation for building AI agents with Restack

An agent operates as an event-driven background process that persists state, executes tasks over time, and runs continuously for weeks or even months.
Learn how to [build reliable agents](https://docs.restack.io/blueprints/introduction)

### [​](https://docs.restack.io/libraries/python/agents\#%40agent-defn)  `@agent.defn()`

Defines the agent class.


from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        pass

```

### [​](https://docs.restack.io/libraries/python/agents\#init)  `__init__()`

Allows defining variables that the agent keeps in its state.


from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    def __init__(self) -> None:
        self.end = False
        self.messages = []

```

### [​](https://docs.restack.io/libraries/python/agents\#%40agent-event)  `@agent.event`

Defines an event handler for the agent.
The most common ones include `messages` and `end`.


from restack_ai.agent import agent, event

@agent.defn()
class MyAgent:
    @agent.event
    async def messages(self, messages: List[Message]):
        self.messages = messages
        return messages

    @agent.event
    async def end(self):
        self.end = True
        return end

```

### [​](https://docs.restack.io/libraries/python/agents\#%40agent-run)  `@agent.run`

Defines the entry point for the agent.


from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        pass

```

### [​](https://docs.restack.io/libraries/python/agents\#%40agent-condition)  `@agent.condition`

Defines a condition for the agent to wait for.
Used for example to wait for an event and complete the agent.

agent.py


from restack_ai.agent import agent, condition

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        await condition(lambda: self.end)

```

### [​](https://docs.restack.io/libraries/python/agents\#agent-step)  `agent.step()`

Inside an agent, use steps to define how and when functions run.


from restack_ai.agent import agent, step

await agent.step(
    function=send_email,
    function_input=SendEmailInput(
        text=text,
        subject=input.subject,
        to=input.to,
    ),
    start_to_close_timeout=timedelta(seconds=120)
)

```

### [​](https://docs.restack.io/libraries/python/agents\#agent-should-continue-as-new)  `agent.should_continue_as_new()`

Return true/false if the agent needs a restart with a following `agent.agent_continue_as_new()` call.
Function checks amount of events and history on the running agent to determine if it needs a restart or not.


from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        self.end = false
        await agent.condition(lambda: end is True or agent.should_continue_as_new())
        agent.agent_continue_as_new()

```

### [​](https://docs.restack.io/libraries/python/agents\#agent-agent-continue-as-new)  `agent.agent_continue_as_new()`

Restart the current agent with the same agent id and input at the end of the current run.
Use this for long running agents or agents expected to receive lots of events (Over 2000).
Restack spawns a new agent with the same agentId and with the provided input passed to the agentContinueAsNew function.


from restack_ai.agent import agent

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        await agent.agent_continue_as_new()

```

## [​](https://docs.restack.io/libraries/python/agents\#utilities)  Utilities

### [​](https://docs.restack.io/libraries/python/agents\#import-functions)  `import_functions()`

Imports the [functions](https://docs.restack.io/libraries/python/functions) from the `functions` folder into the agent by leveraging the `with import_functions()` context manager.


from restack_ai.agent import import_functions

with import_functions():
    from src.functions.my_function import my_function

```

### [​](https://docs.restack.io/libraries/python/agents\#log)  `log()`

Logs a message to the agent.

agent.py


from restack_ai.agent import agent, log

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self, agent_input: AgentInput):
        log.info("Hello, world!", agent_input)

```

Use levels like `info`, `debug`, `warning`, `error`, `critical`.

### [​](https://docs.restack.io/libraries/python/agents\#agent-child-start)  `agent.child_start()`

Initiates a child workflow or agent directly from an agent.The child workflow or agent runs independently of the parent agent.
This method doesn’t wait for the child workflow or agent to complete to return a promise but instead returns the child workflow or agent handle.

agent.py


from restack_ai.agent import agent, import_functions, child_start
from src.agents.child_agent import my_child_agent

@agent.defn()
class ParentAgent:
    @agent.run
    async def run(self):
        handle = await agent.child_start(
            agent=my_child_agent,
            agent_input={"key": "value"},
        )
        return handle

```

## Optional parameters

[​](https://docs.restack.io/libraries/python/agents#param-task-queue)

task\_queue

string

default:"restack"

Specifies the task queue for the step. Defaults to the “restack” task queue if not set.

[​](https://docs.restack.io/libraries/python/agents#param-schedule-to-close-timeout)

schedule\_to\_close\_timeout

timedelta

Sets the duration for the task to complete from scheduling.

[​](https://docs.restack.io/libraries/python/agents#param-schedule-to-start-timeout)

schedule\_to\_start\_timeout

timedelta

Defines the time before task execution begins.

[​](https://docs.restack.io/libraries/python/agents#param-start-to-close-timeout)

start\_to\_close\_timeout

timedelta

Specifies the time for task completion after starting.

[​](https://docs.restack.io/libraries/python/agents#param-heartbeat-timeout)

heartbeat\_timeout

timedelta

Determines the interval for sending heartbeat signals.

[​](https://docs.restack.io/libraries/python/agents#param-retry-policy)

retry\_policy

RetryPolicy

Configures the retry strategy for the task.

- `max_attempts` (int) Number of retry attempts.
- `initial_interval` (timedelta) Initial delay before the first retry.
- `max_interval` (timedelta) Delay between retries.
- `backoff_coefficient` (float) Factor by which the retry interval increases with each attempt.

### [​](https://docs.restack.io/libraries/python/agents\#agent-child-execute)  `agent.child_execute()`

Execute a child agent directly from an agent and wait for its completion.
Unlike `child_start()`, `child_execute()` waits until the child workflow completes and returns its result. The child workflow runs as part of the agent’s execution flow.

agents/parent\_agent.py


from restack_ai.agent import agent, child_execute
from src.workflows.child_workflow import my_child_workflow

@agent.defn()
class ParentAgent:
    @agent.run
    async def run(self):
        response = await agent.child_execute(
            workflow=my_child_workflow,
            workflow_id="my-workflow-id",
            workflow_input={"key": "value"},
        )
        return response

```

[​](https://docs.restack.io/libraries/python/agents#param-workflow-func)

workflow\_func

function

required

The child workflow function to execute.

### [​](https://docs.restack.io/libraries/python/agents\#agent-uuid)  `agent.uuid`

Generates a unique identifier for the agent.

agent.py


from restack_ai.agent import agent, uuid

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self, agent_input: AgentInput):
        generated_id = agent.uuid()
        return generated_id

```

### [​](https://docs.restack.io/libraries/python/agents\#agent-agent-info)  `agent.agent_info()`

Retrieves information about the current agent.

agent.py



from restack_ai.agent import agent, agent_info

@agent.defn()
class MyAgent:
    @agent.run
    async def run(self):
        info = agent_info()
        return info

