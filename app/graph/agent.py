from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .utils.nodes import generate_analysts, search, summarize
from .utils.states import AnalystOutputState, AnalystState, OverallState


def _build_analyst_subgraph() -> Any:
    sg: StateGraph = StateGraph(AnalystState, output_schema=AnalystOutputState)
    sg.add_node("search", search)  # type: ignore
    sg.add_node("summarize", summarize)  # type: ignore
    sg.add_edge(START, "search")
    sg.add_edge("search", "summarize")
    sg.add_edge("summarize", END)
    return sg.compile()


_analyst_subgraph = _build_analyst_subgraph()


def fan_out_to_analysts(state: OverallState) -> list[Send] | str:
    if not state["analysts"]:
        return END
    return [
        Send(
            "analyst_subgraph",
            {
                "job_title": state["job_title"],
                "analyst": a,
                "search_results": [],
                "sections": [],
            },
        )
        for a in state["analysts"]
    ]


def build_graph() -> Any:
    g: StateGraph = StateGraph(OverallState)
    g.add_node("generate_analysts", generate_analysts)
    g.add_node("analyst_subgraph", _analyst_subgraph)

    g.add_edge(START, "generate_analysts")
    g.add_conditional_edges(
        "generate_analysts",
        fan_out_to_analysts,
        ["analyst_subgraph", END],
    )
    g.add_edge("analyst_subgraph", END)
    return g.compile()


graph = build_graph()
