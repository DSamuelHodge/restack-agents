"""
Writeup compilation tool
"""
from restack_ai.function import function, log
from pydantic import BaseModel


class CompileWriteupInput(BaseModel):
    """Input for compiling writeup"""
    title: str
    sections: dict[str, str]
    format: str = "markdown"


class CompileWriteupOutput(BaseModel):
    """Output from writeup compilation"""
    document: str
    file_path: str | None = None


@function.defn()
async def compile_writeup(input: CompileWriteupInput) -> CompileWriteupOutput:
    """
    Compile research writeup from sections (mock implementation).
    In production, generate LaTeX/PDF, handle citations, figures.
    """
    log.info(f"Compiling writeup: {input.title}")
    
    # Build document
    document_parts = [f"# {input.title}\n"]
    
    for section_name, content in input.sections.items():
        document_parts.append(f"\n## {section_name}\n")
        document_parts.append(content)
    
    document = "\n".join(document_parts)
    
    log.info(f"Writeup compiled: {len(document)} characters")
    
    return CompileWriteupOutput(
        document=document,
        file_path=None  # In production, save to file
    )
