"""
Shutdown agent gracefully or cancel workflow
"""
import asyncio
import argparse
import os
from dotenv import load_dotenv
from restack_ai import Restack
from temporalio.client import Client


async def main():
    """Send shutdown event to agent or cancel workflow"""
    
    parser = argparse.ArgumentParser(description="Shutdown BaseModel Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--run-id", help="Run ID (for graceful shutdown)")
    parser.add_argument("--cancel", action="store_true", help="Force cancel workflow instead of graceful shutdown")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    if args.cancel:
        # Force cancel the workflow using Temporal client directly
        workflow_id = f"local-{args.agent_id}"
        print(f"Canceling workflow: {workflow_id}")
        
        try:
            # Get Restack engine address from environment
            engine_address = os.getenv("RESTACK_ENGINE_ADDRESS", "localhost:6233")
            # Remove http:// prefix if present
            if engine_address.startswith("http://"):
                engine_address = engine_address[7:]
            
            # Connect to Temporal server (Restack engine port)
            print(f"Connecting to Restack engine at {engine_address}...")
            temporal_client = await Client.connect(engine_address)
            handle = temporal_client.get_workflow_handle(workflow_id)
            await handle.cancel()
            print("✓ Workflow cancelled successfully")
        except Exception as e:
            print(f"✗ Failed to cancel workflow: {e}")
            print("Workflow may not be running or already completed.")
    
    elif args.run_id:
        # Graceful shutdown using Restack client
        client = Restack()
        print(f"Sending shutdown signal to agent: {args.agent_id}")
        
        await client.send_agent_event(
            agent_id=args.agent_id,
            run_id=args.run_id,
            event_name="shutdown",
            event_input={},
        )
        
        print("✓ Shutdown signal sent")
        print("Agent will complete current task and save final snapshot before shutting down.")
    
    else:
        print("Error: Either --run-id or --cancel must be provided")
        print("\nExamples:")
        print(f"  Graceful shutdown:  python src/shutdown.py --agent-id {args.agent_id} --run-id <run-id>")
        print(f"  Force cancel:       python src/shutdown.py --agent-id {args.agent_id} --cancel")


if __name__ == "__main__":
    asyncio.run(main())
