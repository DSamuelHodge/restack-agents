"""
Research Workflow - Multi-step research pipeline
"""
from datetime import timedelta
from restack_ai.workflow import workflow, log, RetryPolicy, import_functions
from pydantic import BaseModel


class ResearchWorkflowInput(BaseModel):
    """Input for research workflow"""
    topic: str
    max_papers: int = 10
    num_ideas: int = 5


class ResearchWorkflowOutput(BaseModel):
    """Output from research workflow"""
    papers: list[dict]
    ideas: list[str]
    refined_ideas: list[dict]
    status: str


@workflow.defn()
class ResearchWorkflow:
    """
    Long-running research workflow.
    Steps:
    1. Search for papers
    2. Generate research ideas
    3. Refine ideas with scoring
    """
    
    @workflow.run
    async def run(self, input: ResearchWorkflowInput) -> ResearchWorkflowOutput:
        log.info(f"Starting research workflow for: {input.topic}")
        
        # Import functions using proper context manager
        with import_functions():
            from ..functions.tools import search_papers, generate_ideas, refine_ideas
        
        # Step 1: Search papers
        log.info("Step 1: Searching papers")
        papers_result = await workflow.step(
            search_papers,
            {"query": input.topic, "max_results": input.max_papers},
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        # Step 2: Generate ideas
        log.info("Step 2: Generating ideas")
        ideas_result = await workflow.step(
            generate_ideas,
            {"topic": input.topic, "num_ideas": input.num_ideas},
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=90)
        )
        
        # Step 3: Refine ideas
        log.info("Step 3: Refining ideas")
        refined_result = await workflow.step(
            refine_ideas,
            {"ideas": ideas_result["ideas"]},
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=90)
        )
        
        log.info("Research workflow complete")
        
        return ResearchWorkflowOutput(
            papers=papers_result["papers"],
            ideas=ideas_result["ideas"],
            refined_ideas=refined_result["refined_ideas"],
            status="completed"
        )
