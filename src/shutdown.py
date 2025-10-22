"""
Shutdown agent gracefully
"""
import asyncio
import argparse
from dotenv import load_dotenv
from restack_ai import Restack


async def main():
    """Send shutdown event to agent"""
    
    parser = argparse.ArgumentParser(description="Shutdown BaseModel Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--run-id", required=True, help="Run ID")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Restack client
    client = Restack()
    
    print(f"Sending shutdown signal to agent: {args.agent_id}")
    
    # Send shutdown event
    await client.send_agent_event(
        agent_id=args.agent_id,
        run_id=args.run_id,
        event_name="shutdown",
        event_input={},
    )
    
    print("✓ Shutdown signal sent")
    print("Agent will complete current task and save final snapshot before shutting down.")


if __name__ == "__main__":
    asyncio.run(main())
