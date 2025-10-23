"""
Event and data models for BaseModel Agent
"""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Represents a task to be processed by the agent"""
    
    id: str = Field(description="Unique task identifier")
    kind: Literal["research", "writeup", "review", "custom"] = "custom"
    payload: dict[str, Any] = Field(default_factory=dict, description="Task-specific data")
    priority: int = Field(default=0, description="Higher number = higher priority")
    created_at: float = Field(default=0.0, description="Timestamp (not available in workflow context)")


class HistoryEntry(BaseModel):
    """Represents a single entry in the agent's history/memory"""
    
    ts: float = Field(default=0.0, description="Timestamp (not available in workflow context)")
    kind: Literal["plan", "step", "obs", "error", "meta"] = "meta"
    name: str = Field(description="Name of the action/step/observation")
    inputs_digest: str = Field(default="", description="Hash/summary of inputs")
    result_digest: Optional[str] = Field(default=None, description="Hash/summary of outputs")
    latency_ms: Optional[int] = Field(default=None, description="Execution time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    tags: list[str] = Field(default_factory=list, description="Additional metadata tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra structured data")


class Artifact(BaseModel):
    """Represents a named artifact produced by the agent"""
    
    name: str = Field(description="Artifact identifier")
    kind: Literal["file", "url", "data", "reference"] = "data"
    location: Optional[str] = Field(default=None, description="File path, URL, or storage key")
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    created_at: float = Field(default=0.0, description="Timestamp (not available in workflow context)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSnapshot(BaseModel):
    """Complete snapshot of agent state for persistence"""
    
    snapshot_id: str
    agent_name: str
    timestamp: float
    config: dict[str, Any]  # Serialized BaseModelConfig
    inbox: list[dict[str, Any]]  # Serialized Task list
    plan: Optional[dict[str, Any]]  # Serialized Plan
    history: list[dict[str, Any]]  # Serialized HistoryEntry list
    artifacts: dict[str, dict[str, Any]]  # Serialized Artifact dict
    cursors: dict[str, Any]
    stats: dict[str, Any]
    version: str = "0.1.0"
