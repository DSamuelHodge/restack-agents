"""
Configuration models for BaseModel Agent
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class BaseModelConfig(BaseModel):
    """Main configuration for BaseModelAgent"""
    
    # Identity
    agent_name: str = "BaseModelAgent"
    workspace_dir: Optional[str] = None
    
    # Planning
    planning_interval: Optional[int] = None  # Steps between planning; None = plan per task
    planner_mode: Literal["scripted", "heuristic", "model"] = "heuristic"
    
    # Memory
    memory_budget_chars: int = Field(default=16000, description="Max chars before compaction")
    memory_budget_tokens: Optional[int] = None  # Optional token-based budget
    keep_last: int = Field(default=5, description="Keep last N entries verbatim during compaction")
    safety_margin: float = Field(default=0.9, description="Trigger compaction at this % of budget")
    
    # Tool policy
    allowed_tools: list[str] = Field(default_factory=list, description="Whitelist of tool names")
    tool_timeouts: dict[str, int] = Field(default_factory=dict, description="Per-tool timeout in seconds")
    default_timeout_s: int = 60
    
    # Concurrency queues
    queues: dict[str, int] = Field(
        default_factory=lambda: {"openai": 4, "io": 8, "compute": 2},
        description="Queue names and max concurrent tasks"
    )
    
    # Persistence
    snapshot_dir: str = "./snapshots"
    snapshot_interval: Optional[int] = None  # Steps between snapshots; None = after each task
    
    # Retry & resilience
    default_retry_attempts: int = 2
    retry_backoff_base: float = 2.0  # Exponential backoff multiplier
    circuit_breaker_threshold: int = 5  # Failures before circuit opens
    
    # Observability
    structured_logging: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
