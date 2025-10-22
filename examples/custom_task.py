"""
Example: Custom task with custom planner
"""
import asyncio
from restack_ai import Restack
from src.models import Task, Plan, PlanStep


async def main():
    """Send a custom task with a manual plan"""
    
    client = Restack()
    agent_id = "basemodel-agent-1"
    run_id = "your-run-id-here"  # Replace with actual run_id from schedule.py
    
    # Custom task
    task = Task(
        id="task-custom-001",
        kind="custom",
        payload={
            "description": "Custom research pipeline with specific steps",
            "topic": "Neural Architecture Search"
        },
        priority=2
    )
    
    # Send task
    await client.send_agent_event(
        agent_id=agent_id,
        run_id=run_id,
        event_name="enqueue_task",
        event_input=task.model_dump()
    )
    
    print(f"✓ Custom task sent: {task.id}")
    
    # Optional: Override with custom plan
    custom_plan = Plan(
        plan_id="plan-custom-001",
        task_id=task.id,
        mode="scripted",
        steps=[
            PlanStep(
                name="search_papers",
                inputs={"query": "Neural Architecture Search", "max_results": 15},
                timeout_s=45
            ),
            PlanStep(
                name="generate_ideas",
                inputs={"topic": "Neural Architecture Search", "num_ideas": 10},
                timeout_s=90,
                depends_on=["search_papers"]
            ),
            PlanStep(
                name="refine_ideas",
                inputs={"ideas": []},
                timeout_s=90,
                depends_on=["generate_ideas"]
            ),
            PlanStep(
                name="reviewer",
                inputs={"content": "ideas", "review_type": "research"},
                timeout_s=60,
                depends_on=["refine_ideas"]
            ),
        ],
        created_at=asyncio.get_event_loop().time()
    )
    
    await client.send_agent_event(
        agent_id=agent_id,
        run_id=run_id,
        event_name="set_plan",
        event_input=custom_plan.model_dump()
    )
    
    print(f"✓ Custom plan sent: {custom_plan.plan_id}")
    print("  Steps:", [s.name for s in custom_plan.steps])


if __name__ == "__main__":
    asyncio.run(main())
