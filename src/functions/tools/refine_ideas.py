"""
Idea refinement tool
"""
from restack_ai.function import function, log
from pydantic import BaseModel


class RefineIdeasInput(BaseModel):
    """Input for refining ideas"""
    ideas: list[str]
    criteria: list[str] = []


class RefineIdeasOutput(BaseModel):
    """Output from idea refinement"""
    refined_ideas: list[dict]


@function.defn()
async def refine_ideas(input: RefineIdeasInput) -> RefineIdeasOutput:
    """
    Refine and score research ideas (mock implementation).
    In production, use LLM to evaluate novelty, feasibility, impact.
    """
    log.info(f"Refining {len(input.ideas)} ideas")
    
    # Mock refinement with scores
    refined = [
        {
            "idea": idea,
            "novelty_score": 0.8,
            "feasibility_score": 0.7,
            "impact_score": 0.9,
            "refined_description": f"Enhanced: {idea}"
        }
        for idea in input.ideas
    ]
    
    log.info(f"Refined {len(refined)} ideas")
    
    return RefineIdeasOutput(refined_ideas=refined)
