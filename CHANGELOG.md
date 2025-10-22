# Changelog

All notable changes to BaseModel Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-22

### Added
- Initial release of BaseModel Agent
- Core agent with event-driven architecture
- Heuristic planner for task execution
- Memory management with automatic compaction
- Snapshot persistence (JSONL format)
- Research workflow (search → ideas → refine)
- Document pipeline workflow (collect → compile → review)
- 11 tool functions (search, generate, refine, experiment, etc.)
- Comprehensive configuration via Pydantic models
- Service registration and scheduling
- Example scripts and documentation
- Test suite foundation

### Features
- Event handlers: configure, enqueue_task, inject_memory, set_plan, shutdown
- Planning modes: scripted, heuristic (model-driven TBD)
- Memory budget with char-based compaction
- Tool allowlist and validation
- Structured logging and history
- Periodic snapshots
- Task priority queue
- Dependency-aware step execution

### Documentation
- Complete README with quick start
- Architecture overview
- API examples
- Troubleshooting guide
- Contributing guidelines
- MIT License

## [Unreleased]

### Planned for v0.2
- Per-tool retry policies with exponential backoff
- Concurrency queue management
- Circuit breaker for repeated failures
- Parallel step group execution

### Planned for v0.3
- LLM-based model-driven planner
- Token-aware memory compaction
- Dynamic tool selection

### Planned for v0.4
- WASM/container sandbox for code execution
- Secrets scrubbing in logs
- Audit trail and compliance features
