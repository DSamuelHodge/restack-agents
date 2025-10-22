"""
BaseModel Agent - Core agent implementation
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Literal
from restack_ai.agent import agent, condition, log, import_functions

from ..models import (
    BaseModelConfig,
    Task,
    HistoryEntry,
    Artifact,
    AgentSnapshot,
    Plan,
    PlanStep,
)

# Import functions using the proper context manager
with import_functions():
    from ..functions.memory_io import (
        save_snapshot,
        SaveSnapshotInput,
        load_snapshot,
        LoadSnapshotInput,
    )
    from ..functions.memory_compactor import memory_compactor, MemoryCompactorInput
    from ..functions.token_count import token_count, TokenCountInput
    from ..functions.tools import (
        search_papers,
        generate_ideas,
        refine_ideas,
        run_experiment,
        collect_results,
        compile_writeup,
        reviewer,
    )


@agent.defn()
class BaseModelAgent:
    """
    Restack-native BaseModel Agent with planning, memory, and tool execution.
    
    Responsibilities:
    - State keeper: holds task queue, plan, memory, artifacts
    - Event router: translates events into state transitions
    - Planner: decides next steps (scripted/heuristic/model-driven)
    - Dispatcher: executes functions/workflows
    - Historian: logs steps, compacts memory
    - Persistence: saves/loads snapshots
    """
    
    def __init__(self):
        # Configuration
        self.cfg: Optional[BaseModelConfig] = None
        
        # State
        self.inbox: list[Task] = []
        self.plan: Optional[Plan] = None
        self.history: list[HistoryEntry] = []
        self.artifacts: dict[str, Artifact] = {}
        self.cursors: dict[str, Any] = {}  # Workflow/step tracking
        self.stats: dict[str, Any] = {
            "steps_executed": 0,
            "tasks_completed": 0,
            "errors_encountered": 0,
            "last_compaction": None,
            "last_snapshot": None,
        }
        
        # Control
        self.shutdown_flag: bool = False
        self.completed_steps: set[str] = set()  # Track completed step names
    
    # ========== Event Handlers ==========
    
    @agent.event
    async def configure(self, config: dict[str, Any]):
        """Configure the agent"""
        self.cfg = BaseModelConfig(**config)
        log.info(f"Agent configured: {self.cfg.agent_name}")
        
        # Log configuration event
        self._log_event(
            kind="meta",
            name="configure",
            inputs_digest=self._digest(config),
        )
    
    @agent.event
    async def enqueue_task(self, task: dict[str, Any]):
        """Add a task to the inbox"""
        task_obj = Task(**task)
        self.inbox.append(task_obj)
        log.info(f"Task enqueued: {task_obj.id} ({task_obj.kind})")
        
        self._log_event(
            kind="meta",
            name="enqueue_task",
            inputs_digest=task_obj.id,
        )
    
    @agent.event
    async def inject_memory(self, frames: list[dict[str, Any]]):
        """Inject memory frames into history"""
        for frame in frames:
            entry = HistoryEntry(**frame)
            self.history.append(entry)
        
        log.info(f"Injected {len(frames)} memory frames")
        
        self._log_event(
            kind="meta",
            name="inject_memory",
            inputs_digest=f"{len(frames)} frames",
        )
    
    @agent.event
    async def set_plan(self, plan: dict[str, Any]):
        """Manually override the current plan"""
        self.plan = Plan(**plan)
        log.info(f"Plan set manually: {self.plan.plan_id}")
        
        self._log_event(
            kind="plan",
            name="set_plan",
            inputs_digest=self.plan.plan_id,
        )
    
    @agent.event
    async def shutdown(self):
        """Signal shutdown"""
        self.shutdown_flag = True
        log.info("Shutdown signal received")
        
        self._log_event(
            kind="meta",
            name="shutdown",
            inputs_digest="",
        )
    
    # ========== Main Run Loop ==========
    
    @agent.run
    async def run(self):
        """
        Main agent loop:
        1. Wait for work
        2. Plan next steps
        3. Dispatch steps
        4. Persist state
        5. Compact memory if needed
        6. Repeat
        """
        log.info(f"Agent {self.cfg.agent_name if self.cfg else 'BaseModelAgent'} starting")
        
        # Wait for configuration
        await condition(lambda: self.cfg is not None)
        
        while not self.shutdown_flag:
            # Wait for tasks
            await condition(lambda: len(self.inbox) > 0 or self.shutdown_flag)
            
            if self.shutdown_flag:
                break
            
            # Process next task
            task = self._next_task()
            if task:
                await self._process_task(task)
            
            # Periodic maintenance
            await self._maybe_compact_memory()
            await self._maybe_save_snapshot()
        
        # Final snapshot on shutdown
        await self._save_snapshot()
        
        log.info("Agent shutdown complete")
        
        return {
            "status": "shutdown",
            "stats": self.stats,
            "tasks_completed": self.stats["tasks_completed"],
        }
    
    # ========== Task Processing ==========
    
    def _next_task(self) -> Optional[Task]:
        """Get next task from inbox (priority-sorted)"""
        if not self.inbox:
            return None
        
        # Sort by priority (higher first), then by created_at
        self.inbox.sort(key=lambda t: (-t.priority, t.created_at))
        return self.inbox.pop(0)
    
    async def _process_task(self, task: Task):
        """Process a single task"""
        log.info(f"Processing task: {task.id} ({task.kind})")
        
        start_time = datetime.now()
        
        try:
            # Generate plan
            await self._plan_task(task)
            
            # Execute plan
            await self._execute_plan(task)
            
            # Mark success
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_event(
                kind="obs",
                name=f"task_completed:{task.kind}",
                inputs_digest=task.id,
                result_digest="success",
                latency_ms=latency,
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            log.error(f"Task failed: {task.id} - {e}")
            self._log_event(
                kind="error",
                name=f"task_failed:{task.kind}",
                inputs_digest=task.id,
                error=str(e),
            )
            self.stats["errors_encountered"] += 1
    
    # ========== Planning ==========
    
    async def _plan_task(self, task: Task):
        """Generate execution plan for task"""
        log.info(f"Planning task: {task.id}")
        
        if not self.cfg:
            log.warning("Agent not configured, using default heuristic planner")
            plan = self._heuristic_planner(task)
        else:
            # Use configured planner mode
            mode = self.cfg.planner_mode
            
            if mode == "scripted":
                plan = self._scripted_planner(task)
            elif mode == "heuristic":
                plan = self._heuristic_planner(task)
            elif mode == "model":
                plan = await self._model_planner(task)
            else:
                plan = self._heuristic_planner(task)
        
        self.plan = plan
        self.completed_steps.clear()  # Reset for new plan
        
        self._log_event(
            kind="plan",
            name="plan_created",
            inputs_digest=task.id,
            result_digest=f"{len(plan.steps)} steps",
        )
    
    def _scripted_planner(self, task: Task) -> Plan:
        """Scripted planner - static sequences per task kind"""
        steps = []
        
        if task.kind == "research":
            steps = [
                PlanStep(name="search_papers", inputs={"query": task.payload.get("topic", "")}, timeout_s=30),
                PlanStep(name="generate_ideas", inputs={"topic": task.payload.get("topic", "")}, timeout_s=60),
                PlanStep(name="refine_ideas", inputs={"ideas": []}, timeout_s=60, depends_on=["generate_ideas"]),
            ]
        elif task.kind == "writeup":
            steps = [
                PlanStep(name="collect_results", inputs={"experiment_ids": task.payload.get("experiments", [])}, timeout_s=30),
                PlanStep(name="compile_writeup", inputs={"title": task.payload.get("title", "Report")}, timeout_s=120),
                PlanStep(name="reviewer", inputs={"content": "", "review_type": "writeup"}, timeout_s=60, depends_on=["compile_writeup"]),
            ]
        else:
            # Default: simple observation
            steps = [PlanStep(name="reviewer", inputs={"content": str(task.payload), "review_type": "general"}, timeout_s=30)]
        
        return Plan(
            plan_id=f"plan_{task.id}",
            task_id=task.id,
            mode="scripted",
            steps=steps,
            created_at=datetime.now().timestamp(),
        )
    
    def _heuristic_planner(self, task: Task) -> Plan:
        """Heuristic planner - simple rules"""
        # Similar to scripted but with minor adaptations
        return self._scripted_planner(task)
    
    async def _model_planner(self, task: Task) -> Plan:
        """Model-driven planner - use LLM (future implementation)"""
        log.info("Model-driven planning not yet implemented, falling back to heuristic")
        return self._heuristic_planner(task)
    
    # ========== Execution ==========
    
    async def _execute_plan(self, task: Task):
        """Execute the current plan"""
        if not self.plan:
            log.warning("No plan to execute")
            return
        
        log.info(f"Executing plan: {self.plan.plan_id} ({len(self.plan.steps)} steps)")
        
        # Execute steps sequentially (respecting dependencies)
        while len(self.completed_steps) < len(self.plan.steps):
            ready_steps = self.plan.next_steps(self.completed_steps)
            
            if not ready_steps:
                # All dependencies not met, might be stuck
                log.warning("No ready steps but plan incomplete")
                break
            
            for step_obj in ready_steps:
                await self._execute_step(step_obj)
    
    async def _execute_step(self, step_obj: PlanStep):
        """Execute a single plan step"""
        log.info(f"Executing step: {step_obj.name}")
        
        # Check tool allowlist
        if self.cfg and self.cfg.allowed_tools and step_obj.name not in self.cfg.allowed_tools:
            log.warning(f"Tool not allowed: {step_obj.name}")
            self._log_event(
                kind="error",
                name=step_obj.name,
                inputs_digest=self._digest(step_obj.inputs),
                error="Tool not in allowlist",
            )
            self.completed_steps.add(step_obj.name)
            return
        
        start_time = datetime.now()
        
        try:
            # Map step name to function
            func = self._get_function(step_obj.name)
            
            if not func:
                raise ValueError(f"Unknown function: {step_obj.name}")
            
            # Execute with timeout
            timeout = timedelta(seconds=step_obj.timeout_s)
            result = await agent.step(
                function=func,
                function_input=step_obj.inputs,
                start_to_close_timeout=timeout,
            )
            
            # Log success
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_event(
                kind="step",
                name=step_obj.name,
                inputs_digest=self._digest(step_obj.inputs),
                result_digest=self._digest(result),
                latency_ms=latency,
            )
            
            self.stats["steps_executed"] += 1
            self.completed_steps.add(step_obj.name)
            
        except Exception as e:
            log.error(f"Step failed: {step_obj.name} - {e}")
            self._log_event(
                kind="error",
                name=step_obj.name,
                inputs_digest=self._digest(step_obj.inputs),
                error=str(e),
            )
            self.stats["errors_encountered"] += 1
            self.completed_steps.add(step_obj.name)  # Mark as done (failed)
    
    def _get_function(self, name: str):
        """Map function name to actual function"""
        function_map = {
            "search_papers": search_papers,
            "generate_ideas": generate_ideas,
            "refine_ideas": refine_ideas,
            "run_experiment": run_experiment,
            "collect_results": collect_results,
            "compile_writeup": compile_writeup,
            "reviewer": reviewer,
        }
        return function_map.get(name)
    
    # ========== Memory Management ==========
    
    async def _maybe_compact_memory(self):
        """Compact memory if budget exceeded"""
        if not self.cfg:
            return
        
        # Calculate current memory size
        history_json = json.dumps([h.model_dump() for h in self.history])
        current_size = len(history_json)
        
        threshold = int(self.cfg.memory_budget_chars * self.cfg.safety_margin)
        
        if current_size > threshold:
            log.info(f"Memory budget exceeded ({current_size} > {threshold}), compacting")
            
            await self._compact_memory()
    
    async def _compact_memory(self):
        """Perform memory compaction"""
        if not self.cfg:
            log.warning("Cannot compact memory: agent not configured")
            return
            
        try:
            result = await agent.step(
                function=memory_compactor,
                function_input=MemoryCompactorInput(
                    history=[h.model_dump() for h in self.history],
                    keep_last=self.cfg.keep_last,
                    budget_chars=self.cfg.memory_budget_chars,
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # Replace history
            self.history = [HistoryEntry(**h) for h in result["compacted_history"]]
            
            self.stats["last_compaction"] = datetime.now().timestamp()
            
            log.info(f"Memory compacted: {result['original_count']} -> {result['compacted_count']} entries")
            
        except Exception as e:
            log.error(f"Memory compaction failed: {e}")
    
    # ========== Persistence ==========
    
    async def _maybe_save_snapshot(self):
        """Save snapshot if interval elapsed"""
        if not self.cfg or not self.cfg.snapshot_interval:
            return
        
        last_snap = self.stats.get("last_snapshot")
        if last_snap:
            elapsed_steps = self.stats["steps_executed"] - last_snap
            if elapsed_steps < self.cfg.snapshot_interval:
                return
        
        await self._save_snapshot()
    
    async def _save_snapshot(self):
        """Save current state to snapshot"""
        if not self.cfg:
            log.warning("Cannot save snapshot: agent not configured")
            return
            
        try:
            snapshot_id = f"{int(datetime.now().timestamp())}"
            
            snapshot = AgentSnapshot(
                snapshot_id=snapshot_id,
                agent_name=self.cfg.agent_name,
                timestamp=datetime.now().timestamp(),
                config=self.cfg.model_dump(),
                inbox=[t.model_dump() for t in self.inbox],
                plan=self.plan.model_dump() if self.plan else None,
                history=[h.model_dump() for h in self.history],
                artifacts={k: v.model_dump() for k, v in self.artifacts.items()},
                cursors=self.cursors,
                stats=self.stats,
            )
            
            await agent.step(
                function=save_snapshot,
                function_input=SaveSnapshotInput(
                    snapshot=snapshot.model_dump(),
                    snapshot_dir=self.cfg.snapshot_dir,
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            self.stats["last_snapshot"] = self.stats["steps_executed"]
            
            log.info(f"Snapshot saved: {snapshot_id}")
            
        except Exception as e:
            log.error(f"Snapshot save failed: {e}")
    
    # ========== Utilities ==========
    
    def _log_event(
        self,
        kind: Literal['plan', 'step', 'obs', 'error', 'meta'],
        name: str,
        inputs_digest: str,
        result_digest: str | None = None,
        latency_ms: int | None = None,
        error: str | None = None,
    ):
        """Add entry to history"""
        entry = HistoryEntry(
            kind=kind,
            name=name,
            inputs_digest=inputs_digest,
            result_digest=result_digest,
            latency_ms=latency_ms,
            error=error,
        )
        self.history.append(entry)
    
    def _digest(self, obj: Any) -> str:
        """Create short digest of object"""
        try:
            s = json.dumps(obj, sort_keys=True, default=str)
            return hashlib.md5(s.encode()).hexdigest()[:8]
        except Exception:
            return str(obj)[:16]
