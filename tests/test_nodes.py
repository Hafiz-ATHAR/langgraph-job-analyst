from typing import Any

import pytest

from app.graph.agent import graph
from app.graph.utils.nodes import search, summarize
from app.graph.utils.states import Analyst, AnalystTeam, Section


class _StubLLM:
    """Minimal stand-in for `get_llm()` supporting the chain in nodes.py:
    `.with_structured_output(...).with_retry(...).invoke(...)` and `.ainvoke(...)`.

    Note: CLAUDE.md prefers `FakeListChatModel`, but `FakeListChatModel` raises
    `NotImplementedError` on `.with_structured_output(...)` (no tool-calling
    support), so it can't be used for nodes that rely on structured output.
    """

    def __init__(self, response: object) -> None:
        self._response = response

    def with_structured_output(self, _schema: type) -> "_StubLLM":
        return self

    def with_retry(self, **_kwargs: object) -> "_StubLLM":
        return self

    def invoke(self, _messages: object) -> Any:
        if isinstance(self._response, BaseException):
            raise self._response
        return self._response

    async def ainvoke(self, _messages: object) -> Any:
        if isinstance(self._response, BaseException):
            raise self._response
        return self._response


def _patch_llm(monkeypatch: pytest.MonkeyPatch, response: object) -> None:
    monkeypatch.setattr(
        "app.graph.utils.nodes.get_llm",
        lambda: _StubLLM(response),
    )


def _initial_state(job_title: str) -> dict:
    return {
        "job_title": job_title,
        "analysts": [],
        "sections": [],
        "final_report": "",
    }


def _analyst(role: str) -> Analyst:
    return Analyst(
        name=f"Test {role}",
        role=role,
        description=f"{role} persona used in tests.",
        search_angle=f"{role.lower()} test angle 2026",
    )


def _analyst_state(role: str, search_results: list[dict] | None = None) -> dict:
    return {
        "job_title": "Senior Python Engineer",
        "analyst": _analyst(role),
        "search_results": search_results if search_results is not None else [],
        "sections": [],
    }


# --- generate_analysts -------------------------------------------------------


def test_generate_analysts_returns_team_from_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    team = AnalystTeam(
        analysts=[_analyst("Salary Analyst"), _analyst("Skills Analyst")]
    )
    _patch_llm(monkeypatch, team)

    out = graph.nodes["generate_analysts"].invoke(
        _initial_state("Senior Python Engineer")
    )

    assert [a.role for a in out["analysts"]] == ["Salary Analyst", "Skills Analyst"]


def test_generate_analysts_returns_empty_on_llm_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_llm(monkeypatch, RuntimeError("LLM unavailable"))

    out = graph.nodes["generate_analysts"].invoke(
        _initial_state("Senior Python Engineer")
    )

    assert out == {"analysts": []}


# --- search ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_returns_results_from_tavily(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_results = [{"title": "Salary report", "url": "https://x/y", "content": "..."}]

    async def _fake_search_web(_query: str) -> list[dict]:
        return fake_results

    monkeypatch.setattr("app.graph.utils.nodes.search_web", _fake_search_web)

    out = await search(_analyst_state("Salary Analyst"))

    assert out == {"search_results": fake_results}


@pytest.mark.asyncio
async def test_search_returns_empty_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _raising(_query: str) -> list[dict]:
        raise RuntimeError("Tavily exploded")

    monkeypatch.setattr("app.graph.utils.nodes.search_web", _raising)

    out = await search(_analyst_state("Salary Analyst"))

    assert out == {"search_results": []}


# --- summarize ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_summarize_returns_section_from_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    section = Section(
        title="Compensation for Senior Python Engineer",
        content="Salary ranges between X and Y across regions.",
    )
    _patch_llm(monkeypatch, section)

    state = _analyst_state(
        "Salary Analyst",
        search_results=[{"title": "t", "url": "u", "content": "c"}],
    )
    out = await summarize(state)

    assert out == {"sections": [section]}


@pytest.mark.asyncio
async def test_summarize_with_empty_results_returns_unavailable_section(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # If summarize accidentally calls the LLM on empty search_results, this
    # stub raises — surfacing the missing short-circuit immediately.
    _patch_llm(monkeypatch, RuntimeError("LLM should not be called for empty input"))

    out = await summarize(_analyst_state("Skills Analyst", search_results=[]))

    assert len(out["sections"]) == 1
    section = out["sections"][0]
    assert section.title == "Skills Analyst: data unavailable"
    assert "EmptySearchResults" in section.content


@pytest.mark.asyncio
async def test_summarize_returns_unavailable_on_llm_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_llm(monkeypatch, RuntimeError("LLM exploded"))

    state = _analyst_state(
        "Skills Analyst",
        search_results=[{"title": "t", "url": "u", "content": "c"}],
    )
    out = await summarize(state)

    section = out["sections"][0]
    assert section.title == "Skills Analyst: data unavailable"
    assert "RuntimeError" in section.content
