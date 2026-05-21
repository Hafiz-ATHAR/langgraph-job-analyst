from langgraph.graph import StateGraph, START, END
from .utils.states import OverallState
from .utils.nodes import generate_analysts
# from .utils.routes import route_after_fetch, route_after_accumulate


def build_graph():
    g = StateGraph(OverallState)
    g.add_node("generate_analysts", generate_analysts)
    # g.add_node("analyst_subgraph", analyst_subgraph)
    # g.add_node("synthesizer", synthesizer)

    g.add_edge(START, "generate_analysts")
    # g.add_conditional_edges(
    #     "generate_analysts", fan_out_to_analysts, ["analyst_subgraph"]
    # )
    # g.add_edge("analyst_subgraph", "synthesizer")
    # g.add_edge("synthesizer", END)
    g.add_edge("generate_analysts", END)
    return g.compile()


graph = build_graph()
