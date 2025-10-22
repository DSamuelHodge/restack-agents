"""
Example: Run workflows directly (without agent)
"""
import asyncio
from restack_ai import Restack
from src.workflows import ResearchWorkflow, DocPipelineWorkflow


async def main():
    """Schedule workflows directly"""
    
    client = Restack()
    
    # Example 1: Run research workflow
    print("Scheduling ResearchWorkflow...")
    
    research_result = await client.schedule_workflow(
        workflow_name="ResearchWorkflow",
        workflow_id="research-workflow-1",
        workflow_input={
            "topic": "Transformer Models for Time Series",
            "max_papers": 8,
            "num_ideas": 7
        }
    )
    
    print(f"✓ ResearchWorkflow scheduled: {research_result}")
    
    # Example 2: Run document pipeline workflow
    print("\nScheduling DocPipelineWorkflow...")
    
    doc_result = await client.schedule_workflow(
        workflow_name="DocPipelineWorkflow",
        workflow_id="doc-pipeline-1",
        workflow_input={
            "title": "Q4 Research Summary",
            "experiment_ids": ["exp-101", "exp-102", "exp-103"],
            "sections": {
                "Introduction": "This report summarizes our Q4 experiments...",
                "Methods": "We employed three different approaches...",
                "Results": "The experiments yielded the following outcomes...",
                "Conclusion": "In conclusion, we found that..."
            }
        }
    )
    
    print(f"✓ DocPipelineWorkflow scheduled: {doc_result}")
    
    print("\n" + "="*60)
    print("Workflows are now running!")
    print("View progress at: http://localhost:5233")


if __name__ == "__main__":
    asyncio.run(main())
