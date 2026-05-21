# from langgraph.graph import END
# from typing import Literal, cast
# from utils.states import OverallState


# def route_after_planner(state: OverallState) -> Literal["fan_out_analysts", "__end__"]:
#     if not state["analysts"]:
#         return cast(Literal["__end__"], END)
#     return "fan_out_analysts"
