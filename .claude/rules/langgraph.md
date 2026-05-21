---
paths:
  - "app/graph/**/*.py"
---

# LangGraph conventions

- **State**: use `TypedDict`, not `BaseModel`. Use `Annotated[list[X], add]` (or
  another reducer) for any field that fan-in nodes append to.

- **Nodes**: plain `def`/`async def` functions that take state and return a
  partial dict (only the keys they modify). No classes unless instance state is
  truly needed.

- **Async**: nodes that do IO (Tavily, DuckDuckGo, MLflow) must be `async def`.

- **Fan-out**: use `Send(node_name, partial_state)` from `langgraph.types` for
  parallel work (e.g. one Send per analyst). Don't loop and call the node directly.

- **Structured output**: use `llm.with_structured_output(SomeModel)` for typed
  LLM responses — never parse JSON from a raw string. The pydantic model's
  `Field(description=...)` becomes the LLM's instructions.

- **Prompts**: load via `from app.graph.utils.prompt_registry import load_prompt`,
  not by importing the string constants in `prompts.py` directly. The constants
  are the seed source, not the runtime source.

- **Imports**: prefer `from langgraph.graph import StateGraph, START, END` and
  `from langchain_core.messages import ...`. Don't import from the `langchain`
  umbrella package.

- Conditional edges return node names as strings (use `Literal` types).

- For streaming use v2 .

