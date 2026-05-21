# CLAUDE.md

## Langgraph Job Analyst

Multi-agent job market researcher built with LangGraph. Parallel analyst subgraphs fan out, synthesize a structured report.

## Commands

## Before finishing any task
- `uv run ruff check --fix .`
- `uv run ruff format .`
- `uv run mypy app/`

## Architecture (high-level)

- `app/graph/` — LangGraph graph definitions (nodes, edges, compiled graphs)
- `app/graph/utils/states.py` — Pydantic state schemas (typed dicts / BaseModel)
- `app/graph/utils/nodes.py` — individual node functions (pure where possible)
- `app/graph/tools/search.py` — Tavily, Duckduckgo
- `app/graph/utils/llm.py` — llm setup     

## Logging Rules

- Use `structlog`. Get loggers via `log = structlog.get_logger()`.
- **Event names**: lowercase, dot-notated, past tense for events. Examples: `user.login`, `graph.started`, `cache.hit`. Treat them as stable constants — no interpolation, no variables in the name.
- **Never f-string or `%`-format log messages.** Pass variables as kwargs:
  - ✅ `log.info("user.login", user_id=uid, ip=addr)`
  - ❌ `log.info(f"user {uid} logged in")`
  - ❌ `log.info("user %s logged in", uid)`
- **Exceptions**: inside `except` blocks, use `log.exception("thing.failed", ...)`. Use `log.error(...)` only when there is no live exception.
- **Bind context** once with `log = log.bind(request_id=..., user_id=...)` instead of repeating fields on every call.
- **Log levels**: `debug` = dev detail, `info` = normal lifecycle, `warning` = recoverable anomaly, `error` = failed operation, `critical` = system-level failure.

## Coding Rules

- Add a one-line class docstring to every pydantic model and dataclass.
- Add `Field(description=...)` to every field on a pydantic model that is used as
  an LLM structured-output schema. Skip descriptions on internal-only models.

## Testing
- Mock LLM calls with `FakeListChatModel` or recorded fixtures
- When writing tests for this LangGraph project, always consult the official 
  testing docs before implementing:
  **Docs:** https://docs.langchain.com/oss/python/langgraph/test
  