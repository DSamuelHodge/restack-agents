"""
Memory I/O functions for snapshot persistence
"""
import json
import os
from pathlib import Path
from typing import Any
from restack_ai.function import function, log
from pydantic import BaseModel


class SaveSnapshotInput(BaseModel):
    """Input for saving snapshot"""
    snapshot: dict[str, Any]  # Serialized AgentSnapshot
    snapshot_dir: str = "./snapshots"


class SaveSnapshotOutput(BaseModel):
    """Output from saving snapshot"""
    file_path: str
    success: bool
    error: str | None = None


class LoadSnapshotInput(BaseModel):
    """Input for loading snapshot"""
    snapshot_id: str | None = None  # If None, load latest
    snapshot_dir: str = "./snapshots"


class LoadSnapshotOutput(BaseModel):
    """Output from loading snapshot"""
    snapshot: dict[str, Any] | None
    file_path: str | None = None
    success: bool
    error: str | None = None


@function.defn()
async def save_snapshot(input: SaveSnapshotInput) -> SaveSnapshotOutput:
    """
    Save agent snapshot to disk as JSONL (one line per snapshot for append-ability)
    """
    try:
        snapshot_dir = Path(input.snapshot_dir)
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        snapshot_id = input.snapshot["snapshot_id"]
        agent_name = input.snapshot["agent_name"]
        
        # Save to individual file and append to log
        file_path = snapshot_dir / f"{agent_name}_{snapshot_id}.json"
        log_path = snapshot_dir / f"{agent_name}_history.jsonl"
        
        # Write individual snapshot
        with open(file_path, "w") as f:
            json.dump(input.snapshot, f, indent=2)
        
        # Append to history log
        with open(log_path, "a") as f:
            f.write(json.dumps(input.snapshot) + "\n")
        
        log.info(f"Snapshot saved: {file_path}")
        
        return SaveSnapshotOutput(
            file_path=str(file_path),
            success=True
        )
    
    except Exception as e:
        log.error(f"Failed to save snapshot: {e}")
        return SaveSnapshotOutput(
            file_path="",
            success=False,
            error=str(e)
        )


@function.defn()
async def load_snapshot(input: LoadSnapshotInput) -> LoadSnapshotOutput:
    """
    Load agent snapshot from disk.
    If snapshot_id is None, loads the latest snapshot.
    """
    try:
        snapshot_dir = Path(input.snapshot_dir)
        
        if not snapshot_dir.exists():
            return LoadSnapshotOutput(
                snapshot=None,
                success=False,
                error=f"Snapshot directory not found: {snapshot_dir}"
            )
        
        # If specific ID requested, load that file
        if input.snapshot_id:
            matching_files = list(snapshot_dir.glob(f"*_{input.snapshot_id}.json"))
            if not matching_files:
                return LoadSnapshotOutput(
                    snapshot=None,
                    success=False,
                    error=f"Snapshot not found: {input.snapshot_id}"
                )
            file_path = matching_files[0]
        else:
            # Load latest snapshot
            json_files = list(snapshot_dir.glob("*.json"))
            if not json_files:
                return LoadSnapshotOutput(
                    snapshot=None,
                    success=False,
                    error="No snapshots found"
                )
            file_path = max(json_files, key=os.path.getmtime)
        
        # Read snapshot
        with open(file_path, "r") as f:
            snapshot = json.load(f)
        
        log.info(f"Snapshot loaded: {file_path}")
        
        return LoadSnapshotOutput(
            snapshot=snapshot,
            file_path=str(file_path),
            success=True
        )
    
    except Exception as e:
        log.error(f"Failed to load snapshot: {e}")
        return LoadSnapshotOutput(
            snapshot=None,
            success=False,
            error=str(e)
        )
