"""
Research tool functions for BaseModel Agent
"""
from restack_ai.function import function, log
from pydantic import BaseModel


class SearchPapersInput(BaseModel):
    """Input for searching research papers"""
    query: str
    max_results: int = 10


class SearchPapersOutput(BaseModel):
    """Output from paper search"""
    papers: list[dict]
    count: int


@function.defn()
async def search_papers(input: SearchPapersInput) -> SearchPapersOutput:
    """
    Search for research papers (mock implementation).
    In production, integrate with arXiv, Semantic Scholar, etc.
    """
    log.info(f"Searching papers for: {input.query}")
    
    # Mock results
    papers = [
        {
            "title": f"Research Paper on {input.query} #{i+1}",
            "authors": ["Author A", "Author B"],
            "abstract": f"This paper explores {input.query} from a novel perspective...",
            "url": f"https://arxiv.org/abs/mock{i}",
            "year": 2024
        }
        for i in range(min(input.max_results, 3))
    ]
    
    log.info(f"Found {len(papers)} papers")
    
    return SearchPapersOutput(papers=papers, count=len(papers))
