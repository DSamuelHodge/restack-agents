"""
Planning models for BaseModel Agent
"""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    """Represents a single step in a plan"""
    
    name: str = Field(description="Function or workflow name to execute")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    group: Optional[str] = Field(default=None, description="Parallel execution group identifier")
    retry: int = Field(default=2, description="Number of retry attempts")
    timeout_s: int = Field(default=60, description="Timeout in seconds")
    depends_on: list[str] = Field(default_factory=list, description="Step names this depends on")
    metadata: dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    """Represents a complete execution plan"""
    
    plan_id: str = Field(description="Unique plan identifier")
    task_id: str = Field(description="Associated task ID")
    mode: Literal["scripted", "heuristic", "model"] = "heuristic"
    steps: list[PlanStep] = Field(default_factory=list)
    created_at: float
    version: int = Field(default=1, description="Plan version for tracking updates")
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    def next_steps(self, completed: set[str]) -> list[PlanStep]:
        """Get steps ready to execute (dependencies met)"""
        ready = []
        for step in self.steps:
            # Skip if already completed
            if step.name in completed:
                continue
            # Check if all dependencies are met
            if all(dep in completed for dep in step.depends_on):
                ready.append(step)
        return ready
    
    def parallel_groups(self) -> dict[str, list[PlanStep]]:
        """Group steps by parallel execution group"""
        groups: dict[str, list[PlanStep]] = {}
        for step in self.steps:
            group_key = step.group or step.name
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(step)
        return groups
