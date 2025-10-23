"""
Schedule agent and send tasks
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from restack_ai import Restack
from temporalio.exceptions import WorkflowAlreadyStartedError

from src.models import BaseModelConfig, Task


async def main():
    """Schedule the BaseModel Agent and send a test task"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Restack client
    client = Restack()
    
    # Use timestamp to ensure unique agent_id for each run
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    agent_id = f"basemodel-agent-{timestamp}"
    
    print(f"Scheduling BaseModel Agent: {agent_id}")
    
    # Agent configuration
    config = BaseModelConfig(
        agent_name="BaseModelAgent",
        workspace_dir=os.getenv("AGENT_WORKSPACE_DIR", "./workspace"),
        planning_interval=5,
        planner_mode="heuristic",
        memory_budget_chars=int(os.getenv("MEMORY_BUDGET_CHARS", "16000")),
        keep_last=5,
        allowed_tools=[
            "search_papers",
            "generate_ideas",
            "refine_ideas",
            "run_experiment",
            "collect_results",
            "compile_writeup",
            "reviewer",
        ],
        snapshot_dir="./snapshots",
        snapshot_interval=10,
    )
    
    # Schedule the agent
    run_id = await client.schedule_agent(
        agent_name="BaseModelAgent",
        agent_id=agent_id,
        agent_input={},
    )
    
    print(f"✓ Agent scheduled with run_id: {run_id}")
    
    # Send configuration event
    print("Sending configuration...")
    await client.send_agent_event(
        agent_id=agent_id,
        run_id=run_id,
        event_name="configure",
        event_input=config.model_dump(),
    )
    
    print("✓ Configuration sent")
    
    # Send a research task
    print("\nSending research task...")
    task = Task(
        id="task-001",
        kind="research",
        payload={
            "topic": "Large Language Models for Code Generation",
        },
        priority=1,
    )
    
    await client.send_agent_event(
        agent_id=agent_id,
        run_id=run_id,
        event_name="enqueue_task",
        event_input=task.model_dump(),
    )
    
    print("✓ Research task sent")
    
    # Send a writeup task
    print("\nSending writeup task...")
    task2 = Task(
        id="task-002",
        kind="writeup",
        payload={
            "title": "Experimental Results Summary",
            "experiments": ["exp-001", "exp-002", "exp-003"],
        },
        priority=0,
    )
    
    await client.send_agent_event(
        agent_id=agent_id,
        run_id=run_id,
        event_name="enqueue_task",
        event_input=task2.model_dump(),
    )
    
    print("✓ Writeup task sent")
    
    print("\n" + "="*60)
    print("Agent is now running!")
    print("="*60)
    print(f"\nView progress at: http://localhost:5233")
    print(f"Agent ID: {agent_id}")
    print(f"Run ID: {run_id}")
    print("\nThe agent will:")
    print("  1. Process research task (search papers, generate & refine ideas)")
    print("  2. Process writeup task (collect results, compile doc, review)")
    print("  3. Compact memory when budget exceeded")
    print("  4. Save snapshots every 10 steps")
    print("\nTo shutdown the agent, run:")
    print(f"  python -m src.shutdown --agent-id {agent_id} --run-id {run_id}")


if __name__ == "__main__":
    asyncio.run(main())
