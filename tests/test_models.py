"""
Test suite for BaseModel Agent
"""
import pytest
from src.models import (
    BaseModelConfig,
    Task,
    Plan,
    PlanStep,
    HistoryEntry,
    Artifact,
)


class TestModels:
    """Test data models"""
    
    def test_config_creation(self):
        """Test configuration model"""
        config = BaseModelConfig(
            agent_name="TestAgent",
            planner_mode="heuristic",
            memory_budget_chars=10000,
        )
        assert config.agent_name == "TestAgent"
        assert config.planner_mode == "heuristic"
        assert config.memory_budget_chars == 10000
    
    def test_task_creation(self):
        """Test task model"""
        task = Task(
            id="test-task-1",
            kind="research",
            payload={"topic": "AI"},
        )
        assert task.id == "test-task-1"
        assert task.kind == "research"
        assert task.payload["topic"] == "AI"
    
    def test_plan_creation(self):
        """Test plan model"""
        plan = Plan(
            plan_id="plan-1",
            task_id="task-1",
            mode="scripted",
            steps=[
                PlanStep(name="step1", inputs={}),
                PlanStep(name="step2", inputs={}, depends_on=["step1"]),
            ],
            created_at=1234567890.0
        )
        assert len(plan.steps) == 2
        assert plan.steps[1].depends_on == ["step1"]
    
    def test_plan_next_steps(self):
        """Test plan dependency resolution"""
        plan = Plan(
            plan_id="plan-1",
            task_id="task-1",
            mode="scripted",
            steps=[
                PlanStep(name="step1", inputs={}),
                PlanStep(name="step2", inputs={}, depends_on=["step1"]),
                PlanStep(name="step3", inputs={}, depends_on=["step2"]),
            ],
            created_at=1234567890.0
        )
        
        # Initially, only step1 should be ready
        ready = plan.next_steps(completed=set())
        assert len(ready) == 1
        assert ready[0].name == "step1"
        
        # After step1, step2 should be ready
        ready = plan.next_steps(completed={"step1"})
        assert len(ready) == 1
        assert ready[0].name == "step2"
        
        # After step1 and step2, step3 should be ready
        ready = plan.next_steps(completed={"step1", "step2"})
        assert len(ready) == 1
        assert ready[0].name == "step3"
    
    def test_history_entry_creation(self):
        """Test history entry model"""
        entry = HistoryEntry(
            kind="step",
            name="test_function",
            inputs_digest="abc123",
            result_digest="def456",
            latency_ms=150,
        )
        assert entry.kind == "step"
        assert entry.name == "test_function"
        assert entry.latency_ms == 150
    
    def test_artifact_creation(self):
        """Test artifact model"""
        artifact = Artifact(
            name="result.pdf",
            kind="file",
            location="/path/to/result.pdf",
            size_bytes=1024,
        )
        assert artifact.name == "result.pdf"
        assert artifact.kind == "file"
        assert artifact.size_bytes == 1024


# Run tests with: pytest tests/test_models.py
