"""
Service registration for BaseModel Agent
"""
import asyncio
import os
from dotenv import load_dotenv
from restack_ai import Restack
from restack_ai.restack import ServiceOptions, ResourceOptions

from src.agents import BaseModelAgent
from src.workflows import ResearchWorkflow, DocPipelineWorkflow
from src.functions import (
    save_snapshot,
    load_snapshot,
    memory_compactor,
    token_count,
    search_papers,
    generate_ideas,
    refine_ideas,
    run_experiment,
    collect_results,
    compile_writeup,
    reviewer,
)


async def main():
    """Start the BaseModel Agent service"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Restack client
    client = Restack()
    
    print("Starting BaseModel Agent service...")
    print("Registering agents, workflows, and functions...")
    
    # Start service with all components
    await client.start_service(
        agents=[BaseModelAgent],
        workflows=[ResearchWorkflow, DocPipelineWorkflow],
        functions=[
            # Memory & persistence
            save_snapshot,
            load_snapshot,
            memory_compactor,
            token_count,
            # Research tools
            search_papers,
            generate_ideas,
            refine_ideas,
            # Execution tools
            run_experiment,
            collect_results,
            # Writing tools
            compile_writeup,
            reviewer,
        ],
    # No extra resources to register for now
    resources=ResourceOptions(),
        # IMPORTANT: Use the default 'restack' task queue so UI and scheduler can find the service
        task_queue="restack",
        options=ServiceOptions(
            rate_limit=10,  # Max 10 tasks per second
            max_concurrent_function_runs=5,
        ),
    )
    
    print("✓ Service started successfully!")
    print("  - Agent: BaseModelAgent")
    print("  - Workflows: ResearchWorkflow, DocPipelineWorkflow")
    print("  - Functions: 11 tools registered")
    print("  - Task Queue: restack")
    print("\nService is running. Press Ctrl+C to stop.")


if __name__ == "__main__":
    asyncio.run(main())
