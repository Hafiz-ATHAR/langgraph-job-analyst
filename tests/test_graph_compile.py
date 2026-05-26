import importlib
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_APP_GRAPH = _REPO_ROOT / "app" / "graph"


def _discover_modules() -> list[str]:
    return sorted(
        ".".join(p.with_suffix("").relative_to(_REPO_ROOT).parts)
        for p in _APP_GRAPH.rglob("*.py")
        if "__pycache__" not in p.parts
    )


@pytest.mark.parametrize("module_name", _discover_modules())
def test_graph_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)


def test_main_graph_entrypoint() -> None:
    from app.graph.agent import graph

    assert hasattr(
        graph, "invoke"
    ), "app.graph.agent.graph is not a compiled StateGraph"
    assert graph.get_graph().nodes, "compiled graph has no nodes"


def test_analyst_subgraph_compiles() -> None:
    from app.graph.agent import _analyst_subgraph

    assert hasattr(
        _analyst_subgraph, "ainvoke"
    ), "_analyst_subgraph is not a compiled StateGraph"

    node_names = set(_analyst_subgraph.get_graph().nodes)
    assert {
        "search",
        "summarize",
    } <= node_names, f"expected 'search' and 'summarize' nodes, got: {node_names}"
