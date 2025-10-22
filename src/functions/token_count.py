"""
Token counting utility for memory budget management
"""
from restack_ai.function import function, log
from pydantic import BaseModel


class TokenCountInput(BaseModel):
    """Input for token counting function"""
    text: str


class TokenCountOutput(BaseModel):
    """Output from token counting function"""
    char_count: int
    estimated_tokens: int


@function.defn()
async def token_count(input: TokenCountInput) -> TokenCountOutput:
    """
    Estimate token count for text.
    Uses simple heuristic: ~4 chars per token (conservative for GPT models)
    """
    char_count = len(input.text)
    # Conservative estimate: 4 characters per token
    estimated_tokens = char_count // 4
    
    log.info(f"Counted {char_count} chars, ~{estimated_tokens} tokens")
    
    return TokenCountOutput(
        char_count=char_count,
        estimated_tokens=estimated_tokens
    )
