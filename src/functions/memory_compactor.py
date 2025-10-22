"""
Memory compaction function for history management
"""
from typing import Any
from restack_ai.function import function, log
from pydantic import BaseModel
import json


class MemoryCompactorInput(BaseModel):
    """Input for memory compaction"""
    history: list[dict[str, Any]]  # Serialized HistoryEntry list
    keep_last: int = 5
    budget_chars: int = 16000


class MemoryCompactorOutput(BaseModel):
    """Output from memory compaction"""
    compacted_history: list[dict[str, Any]]
    original_count: int
    compacted_count: int
    chars_before: int
    chars_after: int


@function.defn()
async def memory_compactor(input: MemoryCompactorInput) -> MemoryCompactorOutput:
    """
    Compact history when memory budget exceeded.
    Strategy: Keep last N entries verbatim, summarize older entries.
    """
    history = input.history
    keep_last = input.keep_last
    
    original_count = len(history)
    chars_before = len(json.dumps(history))
    
    log.info(f"Compacting history: {original_count} entries, {chars_before} chars")
    
    # If history is small enough, return as-is
    if len(history) <= keep_last or chars_before <= input.budget_chars:
        log.info("History within budget, no compaction needed")
        return MemoryCompactorOutput(
            compacted_history=history,
            original_count=original_count,
            compacted_count=original_count,
            chars_before=chars_before,
            chars_after=chars_before
        )
    
    # Split: keep tail, summarize head
    tail = history[-keep_last:]
    head = history[:-keep_last]
    
    # Create summary entry
    summary_entry = {
        "ts": head[0]["ts"] if head else 0,
        "kind": "meta",
        "name": "COMPACTED_HISTORY",
        "inputs_digest": f"Summarized {len(head)} entries",
        "result_digest": _create_summary(head),
        "latency_ms": None,
        "error": None,
        "tags": ["compaction", "summary"],
        "metadata": {
            "original_count": len(head),
            "time_range": [head[0]["ts"], head[-1]["ts"]] if head else []
        }
    }
    
    # Combine: [summary] + tail
    compacted = [summary_entry] + tail
    chars_after = len(json.dumps(compacted))
    
    log.info(f"Compaction complete: {original_count} -> {len(compacted)} entries, "
             f"{chars_before} -> {chars_after} chars")
    
    return MemoryCompactorOutput(
        compacted_history=compacted,
        original_count=original_count,
        compacted_count=len(compacted),
        chars_before=chars_before,
        chars_after=chars_after
    )


def _create_summary(entries: list[dict[str, Any]]) -> str:
    """Create extractive summary of history entries"""
    # Count by kind
    by_kind: dict[str, int] = {}
    errors = []
    key_steps = []
    
    for entry in entries:
        kind = entry.get("kind", "unknown")
        by_kind[kind] = by_kind.get(kind, 0) + 1
        
        # Collect errors
        if entry.get("error"):
            errors.append(f"{entry.get('name')}: {entry.get('error')}")
        
        # Collect important steps
        if kind == "step" and not entry.get("error"):
            key_steps.append(entry.get("name"))
    
    summary_parts = [
        f"Executed {len(entries)} operations:",
        f"  Plans: {by_kind.get('plan', 0)}, Steps: {by_kind.get('step', 0)}, "
        f"Observations: {by_kind.get('obs', 0)}, Errors: {by_kind.get('error', 0)}"
    ]
    
    if key_steps:
        summary_parts.append(f"  Key steps: {', '.join(key_steps[:5])}")
    
    if errors:
        summary_parts.append(f"  Errors encountered: {'; '.join(errors[:3])}")
    
    return " | ".join(summary_parts)
