"""
Document Pipeline Workflow - From data collection to writeup
"""
from datetime import timedelta
from restack_ai.workflow import workflow, log, RetryPolicy, import_functions
from pydantic import BaseModel


class DocPipelineWorkflowInput(BaseModel):
    """Input for document pipeline workflow"""
    title: str
    experiment_ids: list[str]
    sections: dict[str, str]


class DocPipelineWorkflowOutput(BaseModel):
    """Output from document pipeline workflow"""
    document: str
    review_feedback: str
    review_score: float
    status: str


@workflow.defn()
class DocPipelineWorkflow:
    """
    Document compilation and review pipeline.
    Steps:
    1. Collect experimental results
    2. Compile writeup
    3. Review document
    """
    
    @workflow.run
    async def run(self, input: DocPipelineWorkflowInput) -> DocPipelineWorkflowOutput:
        log.info(f"Starting doc pipeline for: {input.title}")
        
        # Import functions using proper context manager
        with import_functions():
            from ..functions.tools import collect_results, compile_writeup, reviewer
        
        # Step 1: Collect results
        log.info("Step 1: Collecting results")
        results = await workflow.step(
            collect_results,
            {"experiment_ids": input.experiment_ids},
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        # Step 2: Compile writeup
        log.info("Step 2: Compiling writeup")
        writeup = await workflow.step(
            compile_writeup,
            {
                "title": input.title,
                "sections": input.sections,
                "format": "markdown"
            },
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=120)
        )
        
        # Step 3: Review
        log.info("Step 3: Reviewing document")
        review = await workflow.step(
            reviewer,
            {
                "content": writeup["document"],
                "review_type": "writeup"
            },
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10), maximum_attempts=3),
            start_to_close_timeout=timedelta(seconds=90)
        )
        
        log.info("Doc pipeline complete")
        
        return DocPipelineWorkflowOutput(
            document=writeup["document"],
            review_feedback=review["feedback"],
            review_score=review["score"],
            status="completed"
        )
