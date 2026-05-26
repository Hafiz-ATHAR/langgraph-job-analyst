from typing import Any, cast

import httpx
from langchain_core.messages import HumanMessage

from app.graph.tools.search import search_web
from app.graph.utils.decorators import safe_node
from app.graph.utils.llm import get_llm
from app.graph.utils.prompt_registry import load_prompt
from app.graph.utils.states import (
    Analyst,
    AnalystState,
    AnalystTeam,
    OverallState,
    Section,
)

RETRYABLE_LLM_EXCEPTIONS = (
    httpx.RequestError,
)  # CLAUDE: (APIConnectionError, APITimeoutError, RateLimitError)


def generate_analysts(state: OverallState) -> dict[str, list[Analyst]]:
    prompt = load_prompt("generate_analysts").format(job_title=state["job_title"])

    llm = (
        get_llm()
        .with_structured_output(AnalystTeam)
        .with_retry(
            stop_after_attempt=3,
            retry_if_exception_type=RETRYABLE_LLM_EXCEPTIONS,
        )
    )

    try:
        team = cast(AnalystTeam, llm.invoke([HumanMessage(content=prompt)]))
    except Exception as exc:
        print(
            f"node.failed node=generate_analysts "
            f"job_title={state['job_title']!r} error={type(exc).__name__}: {exc}"
        )
        return {"analysts": []}

    return {"analysts": team.analysts}


@safe_node(fallback=lambda _state, _exc: {"search_results": []})  # type: ignore
async def search(state: AnalystState) -> dict[str, Any]:
    """Run a Tavily web search for the analyst's angle."""
    role = state["analyst"].role
    query = f"{state['job_title']} {state['analyst'].search_angle}"
    print(f"[{role}] calling tavily...", flush=True)
    results = await search_web(query)
    print(f"[{role}] got {len(results)} results", flush=True)
    return {"search_results": results}


def _data_unavailable_section(role: str, reason: str) -> Section:
    return Section(
        title=f"{role}: data unavailable",
        content=f"Could not generate this section due to an error: {reason}.",
    )


def _format_search_results(results: list[dict[str, Any]]) -> str:
    lines = []
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        lines.append(f"- {title} ({url}): {content}")
    return "\n".join(lines)


@safe_node(  # type: ignore
    fallback=lambda state, exc: {
        "sections": [
            _data_unavailable_section(state["analyst"].role, type(exc).__name__)
        ]
    }
)
async def summarize(state: AnalystState) -> dict[str, Any]:
    """Draft a report Section from the analyst's search results."""
    analyst = state["analyst"]
    role = analyst.role

    if not state.get("search_results"):
        print(f"[{role}] no search results, returning unavailable section", flush=True)
        return {"sections": [_data_unavailable_section(role, "EmptySearchResults")]}

    prompt = load_prompt("analyst_prompt").format(
        role=role,
        description=analyst.description,
        job_title=state["job_title"],
        search_angle=analyst.search_angle,
        search_results=_format_search_results(state["search_results"]),
    )

    llm = (
        get_llm()
        .with_structured_output(Section)
        .with_retry(
            stop_after_attempt=3,
            retry_if_exception_type=RETRYABLE_LLM_EXCEPTIONS,
        )
    )

    print(f"[{role}] calling llm for summary...", flush=True)
    section = cast(Section, await llm.ainvoke([HumanMessage(content=prompt)]))
    print(f"[{role}] got section title={section.title!r}", flush=True)
    return {"sections": [section]}
