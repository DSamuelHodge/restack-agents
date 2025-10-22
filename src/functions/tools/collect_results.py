"""
Results collection tool
"""
from restack_ai.function import function, log
from pydantic import BaseModel


class CollectResultsInput(BaseModel):
    """Input for collecting results"""
    experiment_ids: list[str]
    format: str = "summary"


class CollectResultsOutput(BaseModel):
    """Output from results collection"""
    results: list[dict]
    summary: str


@function.defn()
async def collect_results(input: CollectResultsInput) -> CollectResultsOutput:
    """
    Collect and aggregate experiment results (mock implementation).
    """
    log.info(f"Collecting results for {len(input.experiment_ids)} experiments")
    
    # Mock results
    results = [
        {
            "experiment_id": exp_id,
            "status": "completed",
            "metrics": {"accuracy": 0.90 + i * 0.01}
        }
        for i, exp_id in enumerate(input.experiment_ids)
    ]
    
    summary = f"Collected {len(results)} experiment results. Average accuracy: 0.91"
    
    log.info(f"Results collected: {summary}")
    
    return CollectResultsOutput(results=results, summary=summary)
