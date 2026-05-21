from typing import cast
import httpx
from langchain_core.messages import HumanMessage
from app.graph.utils.llm import get_llm
from app.graph.utils.prompt_registry import load_prompt
from app.graph.utils.states import Analyst, AnalystTeam, OverallState

RETRYABLE_LLM_EXCEPTIONS = (httpx.RequestError,) # CLAUDE: (APIConnectionError, APITimeoutError, RateLimitError)


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

